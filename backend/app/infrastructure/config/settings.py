from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Backend API"
    debug: bool = False
    db_url: str = "postgresql+asyncpg://app_user:app_pass@localhost:5432/app_db"
    db_echo: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
