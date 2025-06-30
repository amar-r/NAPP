from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class PayrollBase(BaseModel):
    week_start_date: date
    week_end_date: date
    gross_pay: float
    notes: Optional[str] = None

class PayrollCreate(PayrollBase):
    pass

class PayrollResponse(PayrollBase):
    id: int
    federal_tax: float
    social_security_employee: float
    social_security_employer: float
    medicare_employee: float
    medicare_employer: float
    futa_tax: float
    suta_tax: float
    net_pay: float
    total_cost: float
    cumulative_gross_ytd: float
    cumulative_social_security_ytd: float
    cumulative_medicare_ytd: float
    cumulative_futa_ytd: float
    cumulative_suta_ytd: float
    
    class Config:
        from_attributes = True