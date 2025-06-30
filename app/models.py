from sqlalchemy import Column, Integer, String, Float, Date

from app.database import Base

class PayrollEntry(Base):
    __tablename__ = "payroll_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    gross_pay = Column(Float, nullable=False)
    federal_tax = Column(Float, nullable=False)
    social_security_employee = Column(Float, nullable=False)
    social_security_employer = Column(Float, nullable=False)
    medicare_employee = Column(Float, nullable=False)
    medicare_employer = Column(Float, nullable=False)
    futa_tax = Column(Float, nullable=False)
    suta_tax = Column(Float, nullable=False)
    net_pay = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    cumulative_gross_ytd = Column(Float, nullable=False)
    cumulative_social_security_ytd = Column(Float, nullable=False)
    cumulative_medicare_ytd = Column(Float, nullable=False)
    cumulative_futa_ytd = Column(Float, nullable=False)
    cumulative_suta_ytd = Column(Float, nullable=False)
    notes = Column(String)