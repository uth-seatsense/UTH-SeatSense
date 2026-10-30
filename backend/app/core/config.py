from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "UTH-SeatSense API"
    database_url: str | None = Field(default=None, repr=False)
    cv_service_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
