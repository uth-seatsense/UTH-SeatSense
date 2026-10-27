from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "UTH-SeatSense CV"
    model_config = SettingsConfigDict(env_prefix="CV_", extra="ignore")


settings = Settings()
