from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional, List

class PayrollBase(BaseModel):
    """Base schema for payroll entries."""
    week_start_date: date
    week_end_date: date
    gross_pay: float = Field(..., gt=0, description="Gross pay amount")
    notes: Optional[str] = None

class PayrollCreate(PayrollBase):
    """Schema for creating a new payroll entry."""
    
    @validator('week_end_date')
    def week_end_after_start(cls, v, values):
        if 'week_start_date' in values and v <= values['week_start_date']:
            raise ValueError('Week end date must be after week start date')
        return v

class PayrollUpdate(BaseModel):
    """Schema for updating a payroll entry."""
    week_start_date: Optional[date] = None
    week_end_date: Optional[date] = None
    gross_pay: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None

class PayrollResponse(PayrollBase):
    """Schema for payroll entry responses."""
    id: int
    federal_income_tax: float
    federal_social_security_tax: float
    federal_medicare_tax: float
    federal_unemployment_tax: float
    virginia_income_tax: float
    virginia_unemployment_tax: float
    net_pay: float
    total_taxes: float
    total_cost: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PayrollList(BaseModel):
    """Schema for list of payroll entries."""
    entries: List[PayrollResponse]
    total_count: int
    total_gross_pay: float
    total_net_pay: float
    total_cost: float

class ExportFilters(BaseModel):
    """Schema for export filters."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_gross_pay: Optional[float] = None
    max_gross_pay: Optional[float] = None
    format: str = Field(default="csv", pattern="^(csv|json|table)$")