from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str
    database_name: str = "secure_file_share"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()