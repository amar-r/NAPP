from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    federal_tax_rate: float = 0.15
    social_security_rate: float = 0.062
    medicare_rate: float = 0.0145
    futa_rate: float = 0.006
    suta_rate: float = 0.027
    social_security_wage_limit: float = 168600.0
    futa_wage_limit: float = 7000.0
    suta_wage_limit: float = 7000.0

    database_url: str = "sqlite:///./napp.db"

settings = Settings()
