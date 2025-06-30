import math
from typing import Dict, Optional

from app.config import settings
from app.models import PayrollEntry


class TaxCalculator:
    """A service to encapsulate all payroll tax calculation logic."""

    def calculate_all_payroll_data(
        self, gross_pay: float, last_entry: Optional[PayrollEntry]
    ) -> Dict[str, float]:
        """
        Calculates all tax and cumulative data for a single payroll period.

        Args:
            gross_pay: The gross pay for the current period.
            last_entry: The complete PayrollEntry model instance from the previous
                        period. This can be None if it's the first entry.

        Returns:
            A dictionary containing all calculated fields required for a new
            PayrollEntry record.
        """
        # Step 1: Determine previous cumulative totals.
        if last_entry:
            prev_cumulative_gross = last_entry.cumulative_gross_ytd
        else:
            prev_cumulative_gross = 0.0

        # Step 2: Calculate current period's taxes, considering wage limits.
        taxable_ss = min(
            gross_pay,
            max(0, settings.social_security_wage_limit - prev_cumulative_gross),
        )
        taxable_futa = min(
            gross_pay, max(0, settings.futa_wage_limit - prev_cumulative_gross)
        )
        taxable_suta = min(
            gross_pay, max(0, settings.suta_wage_limit - prev_cumulative_gross)
        )

        federal_tax = gross_pay * settings.federal_tax_rate
        social_security_employee = taxable_ss * settings.social_security_rate
        medicare_employee = gross_pay * settings.medicare_rate

        social_security_employer = taxable_ss * settings.social_security_rate
        medicare_employer = gross_pay * settings.medicare_rate
        futa_tax = taxable_futa * settings.futa_rate
        suta_tax = taxable_suta * settings.suta_rate

        net_pay = gross_pay - federal_tax - social_security_employee - medicare_employee
        total_cost = (
            gross_pay
            + social_security_employer
            + medicare_employer
            + futa_tax
            + suta_tax
        )

        # Step 3: Calculate the new cumulative totals.
        # We need the previous cumulative values for each tax type.
        if last_entry:
            prev_cumulative_ss = last_entry.cumulative_social_security_ytd
            prev_cumulative_medicare = last_entry.cumulative_medicare_ytd
            prev_cumulative_futa = last_entry.cumulative_futa_ytd
            prev_cumulative_suta = last_entry.cumulative_suta_ytd
        else:
            prev_cumulative_ss = 0.0
            prev_cumulative_medicare = 0.0
            prev_cumulative_futa = 0.0
            prev_cumulative_suta = 0.0
            
        new_cumulative_gross_ytd = prev_cumulative_gross + gross_pay
        new_cumulative_ss_ytd = prev_cumulative_ss + social_security_employee
        new_cumulative_medicare_ytd = prev_cumulative_medicare + medicare_employee
        new_cumulative_futa_ytd = prev_cumulative_futa + futa_tax
        new_cumulative_suta_ytd = prev_cumulative_suta + suta_tax

        # Step 4: Return a single, complete dictionary.
        return {
            # Current period taxes and totals
            "federal_tax": round(federal_tax, 2),
            "social_security_employee": round(social_security_employee, 2),
            "social_security_employer": round(social_security_employer, 2),
            "medicare_employee": round(medicare_employee, 2),
            "medicare_employer": round(medicare_employer, 2),
            "futa_tax": round(futa_tax, 2),
            "suta_tax": round(suta_tax, 2),
            "net_pay": round(net_pay, 2),
            "total_cost": round(total_cost, 2),
            # New cumulative totals
            "cumulative_gross_ytd": round(new_cumulative_gross_ytd, 2),
            "cumulative_social_security_ytd": round(new_cumulative_ss_ytd, 2),
            "cumulative_medicare_ytd": round(new_cumulative_medicare_ytd, 2),
            "cumulative_futa_ytd": round(new_cumulative_futa_ytd, 2),
            "cumulative_suta_ytd": round(new_cumulative_suta_ytd, 2),
        }

    def calculate_cumulative_totals(
        self,
        current_period_taxes: Dict[str, float],
        previous_cumulative_totals: Dict[str, float],
        current_gross_pay: float
    ) -> Dict[str, float]:

        cumulative_gross = previous_cumulative_totals.get("gross", 0) + current_gross_pay
        cumulative_ss = previous_cumulative_totals.get("ss", 0) + current_period_taxes["social_security_employee"]
        cumulative_medicare = previous_cumulative_totals.get("medicare", 0) + current_period_taxes["medicare_employee"]
        cumulative_futa = previous_cumulative_totals.get("futa", 0) + current_period_taxes["futa_tax"]
        cumulative_suta = previous_cumulative_totals.get("suta", 0) + current_period_taxes["suta_tax"]

        return {
            "cumulative_gross_ytd": round(cumulative_gross, 2),
            "cumulative_social_security_ytd": round(cumulative_ss, 2),
            "cumulative_medicare_ytd": round(cumulative_medicare, 2),
            "cumulative_futa_ytd": round(cumulative_futa, 2),
            "cumulative_suta_ytd": round(cumulative_suta, 2),
        }