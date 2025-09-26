from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    PYTH_ORACLE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()