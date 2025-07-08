from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class PayrollEntry(Base):
    """Model for payroll entries with comprehensive tax calculations."""
    
    __tablename__ = "payroll_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic payroll information
    week_start_date = Column(Date, nullable=False, index=True)
    week_end_date = Column(Date, nullable=False, index=True)
    gross_pay = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Calculated tax amounts
    federal_income_tax = Column(Float, default=0.0)
    federal_social_security_tax = Column(Float, default=0.0)
    federal_medicare_tax = Column(Float, default=0.0)
    federal_unemployment_tax = Column(Float, default=0.0)
    
    # Virginia state taxes
    virginia_income_tax = Column(Float, default=0.0)
    virginia_unemployment_tax = Column(Float, default=0.0)
    
    # Calculated totals
    net_pay = Column(Float, default=0.0)
    total_taxes = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Cumulative YTD amounts
    cumulative_gross_pay = Column(Float, default=0.0)
    cumulative_social_security_ytd = Column(Float, default=0.0)
    cumulative_medicare_ytd = Column(Float, default=0.0)
    cumulative_futa_ytd = Column(Float, default=0.0)
    cumulative_suta_ytd = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PayrollEntry(id={self.id}, week_end={self.week_end_date}, gross=${self.gross_pay})>"