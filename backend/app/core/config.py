from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./sql_app.db"
    app_name: str = "Delivery Driver API"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
