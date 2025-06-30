import pytest
from app.services.tax_calc import TaxCalculator
from app.config import settings
from app.models import PayrollEntry

# Fixture to initialize the calculator
@pytest.fixture
def calculator():
    return TaxCalculator()

def test_calculate_first_payroll(calculator):
    """
    Test calculation for the very first payroll entry where there are no cumulative totals yet.
    """
    gross_pay = 1000.00
    
    # Expected calculations based on default rates
    expected_federal_tax = gross_pay * settings.federal_tax_rate
    expected_ss_employee = gross_pay * settings.social_security_rate
    expected_medicare_employee = gross_pay * settings.medicare_rate
    expected_ss_employer = gross_pay * settings.social_security_rate
    expected_medicare_employer = gross_pay * settings.medicare_rate
    expected_futa = gross_pay * settings.futa_rate
    expected_suta = gross_pay * settings.suta_rate

    expected_net_pay = gross_pay - expected_federal_tax - expected_ss_employee - expected_medicare_employee
    expected_total_cost = gross_pay + expected_ss_employer + expected_medicare_employer + expected_futa + expected_suta

    # Call the calculator
    result = calculator.calculate_all_payroll_data(gross_pay=gross_pay, last_entry=None)

    # Asserts
    assert result["federal_tax"] == round(expected_federal_tax, 2)
    assert result["social_security_employee"] == round(expected_ss_employee, 2)
    assert result["net_pay"] == round(expected_net_pay, 2)
    assert result["total_cost"] == round(expected_total_cost, 2)
    assert result["futa_tax"] == round(expected_futa, 2)
    assert result["suta_tax"] == round(expected_suta, 2)
    
    # Check cumulative totals for the first run
    assert result["cumulative_gross_ytd"] == round(gross_pay, 2)
    assert result["cumulative_futa_ytd"] == round(expected_futa, 2)

def test_calculation_crossing_wage_limit(calculator):
    """
    Test a scenario where the payroll crosses a wage limit (e.g., FUTA).
    """
    # Assume FUTA limit is $7000. Last pay brought total to $6500.
    # Current gross pay is $1000. Only $500 should be taxed for FUTA.
    last_entry = PayrollEntry(
        id=1,
        week_start_date="2023-12-01",
        week_end_date="2023-12-08",
        gross_pay=500.00,
        notes="",
        federal_tax=50.0,
        social_security_employee=31.0,
        social_security_employer=31.0,
        medicare_employee=7.25,
        medicare_employer=7.25,
        futa_tax=3.0,
        suta_tax=27.0,
        net_pay=411.75,
        total_cost=601.25,
        cumulative_gross_ytd=6500.00, # Previous YTD Gross
        cumulative_social_security_ytd=403.00,
        cumulative_medicare_ytd=94.25,
        cumulative_futa_ytd=39.00,
        cumulative_suta_ytd=351.00,
    )

    gross_pay = 1000.00
    
    # FUTA is only on the first $7000. Prev gross is $6500.
    # So, only $500 of the current $1000 gross pay is subject to FUTA.
    taxable_futa = settings.futa_wage_limit - last_entry.cumulative_gross_ytd
    expected_futa_tax = taxable_futa * settings.futa_rate

    result = calculator.calculate_all_payroll_data(gross_pay=gross_pay, last_entry=last_entry)

    assert result["futa_tax"] == round(expected_futa_tax, 2)
    
    # Check that the new cumulative FUTA is correct
    expected_cumulative_futa = last_entry.cumulative_futa_ytd + expected_futa_tax
    assert result["cumulative_futa_ytd"] == round(expected_cumulative_futa, 2) 