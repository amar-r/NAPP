from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = "sqlite:///./napp.db"
    
    # Tax rates and limits
    federal_tax_rate: float = 0.15
    social_security_rate: float = 0.062
    medicare_rate: float = 0.0145
    futa_rate: float = 0.006
    suta_rate: float = 0.027
    social_security_wage_limit: float = 168600.0
    futa_wage_limit: float = 7000.0
    suta_wage_limit: float = 7000.0
    
    # Virginia state tax rates
    virginia_income_tax_rate: float = 0.0575
    virginia_suta_rate: float = 0.0271
    virginia_suta_wage_limit: float = 8000.0
    
    # Application settings
    app_name: str = "NAPP - Nanny Automated Payroll Profiler"
    app_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
