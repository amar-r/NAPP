"""
Tax Calculator Service for Nanny Payroll

This service calculates all applicable taxes for nanny payroll including:
- Federal Income Tax
- Federal Social Security Tax (FICA)
- Federal Medicare Tax
- Federal Unemployment Tax (FUTA)
- Virginia State Income Tax
- Virginia State Unemployment Tax (SUTA)
"""

from typing import Optional, Dict, Any
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

class TaxCalculator:
    """Comprehensive tax calculator for nanny payroll."""
    
    # 2024 Federal Tax Rates and Limits
    FEDERAL_SOCIAL_SECURITY_RATE = 0.062  # 6.2% for employee
    FEDERAL_SOCIAL_SECURITY_LIMIT = 168600  # 2024 limit
    FEDERAL_MEDICARE_RATE = 0.0145  # 1.45% for employee
    FEDERAL_FUTA_RATE = 0.006  # 0.6% for employer
    FEDERAL_FUTA_LIMIT = 7000  # per employee per year
    
    # Virginia State Tax Rates and Limits
    VIRGINIA_INCOME_TAX_RATE = 0.0575  # 5.75% flat rate
    VIRGINIA_SUTA_RATE = 0.0271  # 2.71% for employer
    VIRGINIA_SUTA_LIMIT = 8000  # per employee per year
    
    def __init__(self):
        self.cumulative_data = {
            'gross_pay': 0.0,
            'social_security_taxable': 0.0,
            'medicare_taxable': 0.0,
            'futa_taxable': 0.0,
            'suta_taxable': 0.0
        }
    
    def calculate_all_payroll_data(self, gross_pay: float, last_entry: Optional[Any] = None) -> Dict[str, float]:
        """
        Calculate all payroll data for a given gross pay amount.
        
        Args:
            gross_pay: The gross pay amount for the pay period
            last_entry: The last payroll entry to get cumulative data
            
        Returns:
            Dictionary containing all calculated tax amounts and totals
        """
        # Update cumulative data if we have a last entry
        if last_entry:
            self.cumulative_data = {
                'gross_pay': last_entry.cumulative_gross_pay if hasattr(last_entry, 'cumulative_gross_pay') else 0.0,
                'social_security_taxable': last_entry.cumulative_social_security_ytd if hasattr(last_entry, 'cumulative_social_security_ytd') else 0.0,
                'medicare_taxable': last_entry.cumulative_medicare_ytd if hasattr(last_entry, 'cumulative_medicare_ytd') else 0.0,
                'futa_taxable': last_entry.cumulative_futa_ytd if hasattr(last_entry, 'cumulative_futa_ytd') else 0.0,
                'suta_taxable': last_entry.cumulative_suta_ytd if hasattr(last_entry, 'cumulative_suta_ytd') else 0.0
            }
        
        # Calculate individual taxes
        federal_income_tax = self._calculate_federal_income_tax(gross_pay)
        federal_social_security_tax = self._calculate_federal_social_security_tax(gross_pay)
        federal_medicare_tax = self._calculate_federal_medicare_tax(gross_pay)
        federal_unemployment_tax = self._calculate_federal_unemployment_tax(gross_pay)
        
        virginia_income_tax = self._calculate_virginia_income_tax(gross_pay)
        virginia_unemployment_tax = self._calculate_virginia_unemployment_tax(gross_pay)
        
        # Calculate totals
        total_taxes = (federal_income_tax + federal_social_security_tax + 
                      federal_medicare_tax + virginia_income_tax)
        
        net_pay = gross_pay - total_taxes
        
        total_cost = (gross_pay + federal_unemployment_tax + virginia_unemployment_tax)
        
        # Update cumulative data
        self.cumulative_data['gross_pay'] += gross_pay
        self.cumulative_data['social_security_taxable'] += min(gross_pay, max(0, self.FEDERAL_SOCIAL_SECURITY_LIMIT - self.cumulative_data['social_security_taxable']))
        self.cumulative_data['medicare_taxable'] += gross_pay
        self.cumulative_data['futa_taxable'] += min(gross_pay, max(0, self.FEDERAL_FUTA_LIMIT - self.cumulative_data['futa_taxable']))
        self.cumulative_data['suta_taxable'] += min(gross_pay, max(0, self.VIRGINIA_SUTA_LIMIT - self.cumulative_data['suta_taxable']))
        
        return {
            'federal_income_tax': round(federal_income_tax, 2),
            'federal_social_security_tax': round(federal_social_security_tax, 2),
            'federal_medicare_tax': round(federal_medicare_tax, 2),
            'federal_unemployment_tax': round(federal_unemployment_tax, 2),
            'virginia_income_tax': round(virginia_income_tax, 2),
            'virginia_unemployment_tax': round(virginia_unemployment_tax, 2),
            'net_pay': round(net_pay, 2),
            'total_taxes': round(total_taxes, 2),
            'total_cost': round(total_cost, 2),
            'cumulative_gross_pay': round(self.cumulative_data['gross_pay'], 2),
            'cumulative_social_security_ytd': round(self.cumulative_data['social_security_taxable'], 2),
            'cumulative_medicare_ytd': round(self.cumulative_data['medicare_taxable'], 2),
            'cumulative_futa_ytd': round(self.cumulative_data['futa_taxable'], 2),
            'cumulative_suta_ytd': round(self.cumulative_data['suta_taxable'], 2)
        }
    
    def _calculate_federal_income_tax(self, gross_pay: float) -> float:
        """
        Calculate Federal Income Tax using simplified withholding tables.
        This is a simplified calculation - in practice, you'd use IRS withholding tables.
        """
        # Simplified calculation - in reality, you'd use IRS Publication 15-T
        # For now, using a basic percentage based on income brackets
        if gross_pay <= 11000:
            rate = 0.10
        elif gross_pay <= 44725:
            rate = 0.12
        elif gross_pay <= 95375:
            rate = 0.22
        elif gross_pay <= 182100:
            rate = 0.24
        else:
            rate = 0.32
        
        return gross_pay * rate
    
    def _calculate_federal_social_security_tax(self, gross_pay: float) -> float:
        """Calculate Federal Social Security Tax (FICA)."""
        taxable_amount = min(gross_pay, max(0, self.FEDERAL_SOCIAL_SECURITY_LIMIT - self.cumulative_data['social_security_taxable']))
        return taxable_amount * self.FEDERAL_SOCIAL_SECURITY_RATE
    
    def _calculate_federal_medicare_tax(self, gross_pay: float) -> float:
        """Calculate Federal Medicare Tax."""
        return gross_pay * self.FEDERAL_MEDICARE_RATE
    
    def _calculate_federal_unemployment_tax(self, gross_pay: float) -> float:
        """Calculate Federal Unemployment Tax (FUTA)."""
        taxable_amount = min(gross_pay, max(0, self.FEDERAL_FUTA_LIMIT - self.cumulative_data['futa_taxable']))
        return taxable_amount * self.FEDERAL_FUTA_RATE
    
    def _calculate_virginia_income_tax(self, gross_pay: float) -> float:
        """Calculate Virginia State Income Tax."""
        return gross_pay * self.VIRGINIA_INCOME_TAX_RATE
    
    def _calculate_virginia_unemployment_tax(self, gross_pay: float) -> float:
        """Calculate Virginia State Unemployment Tax (SUTA)."""
        taxable_amount = min(gross_pay, max(0, self.VIRGINIA_SUTA_LIMIT - self.cumulative_data['suta_taxable']))
        return taxable_amount * self.VIRGINIA_SUTA_RATE
    
    def get_tax_summary(self, payroll_data: Dict[str, float]) -> Dict[str, Any]:
        """Get a summary of all tax calculations."""
        return {
            'employee_taxes': {
                'federal_income_tax': payroll_data['federal_income_tax'],
                'federal_social_security_tax': payroll_data['federal_social_security_tax'],
                'federal_medicare_tax': payroll_data['federal_medicare_tax'],
                'virginia_income_tax': payroll_data['virginia_income_tax'],
                'total_employee_taxes': payroll_data['total_taxes']
            },
            'employer_taxes': {
                'federal_unemployment_tax': payroll_data['federal_unemployment_tax'],
                'virginia_unemployment_tax': payroll_data['virginia_unemployment_tax'],
                'total_employer_taxes': payroll_data['federal_unemployment_tax'] + payroll_data['virginia_unemployment_tax']
            },
            'payroll_summary': {
                'gross_pay': payroll_data.get('gross_pay', 0),
                'net_pay': payroll_data['net_pay'],
                'total_cost': payroll_data['total_cost']
            }
        } 