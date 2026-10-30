from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    app_name: str = "UTH-SeatSense API"
    database_url: str | None = Field(default=None, repr=False)
    database_host: str | None = None
    database_port: int = Field(default=5432, ge=1, le=65535)
    database_name: str | None = None
    database_user: str | None = None
    database_password: SecretStr | None = Field(default=None, repr=False)
    cv_service_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(extra="ignore")

    def connection_url(self):
        if self.database_url:
            return self.database_url
        if not all((self.database_host,self.database_name,self.database_user,self.database_password)):
            raise ValueError('Configure DATABASE_URL or all DATABASE_* connection fields')
        return URL.create('postgresql+psycopg',host=self.database_host,port=self.database_port,
                          database=self.database_name,username=self.database_user,
                          password=self.database_password.get_secret_value())


settings = Settings()
