from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Backend API"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"  # local, production

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://app_user:app_pass@localhost:5432/app_db"
    DB_ECHO: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
