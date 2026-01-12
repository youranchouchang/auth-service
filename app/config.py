import os
from typing import Optional

class Settings:
    # 数据库配置
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./auth.db')
    
    # JWT配置
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production-12345')
    ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    def __init__(self):
        # 确保所有值都是正确的类型
        self.DATABASE_URL = str(self.DATABASE_URL)
        self.SECRET_KEY = str(self.SECRET_KEY)
        self.ALGORITHM = str(self.ALGORITHM)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(self.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(self.REFRESH_TOKEN_EXPIRE_DAYS)

settings = Settings()
