from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UTH-SeatSense API"
    database_url: str = "postgresql+psycopg://seatsense:seatsense@localhost:5432/seatsense"
    cv_service_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
