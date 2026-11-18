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
    allowed_email_domains: str = ""
    otp_hash_secret: SecretStr | None = Field(default=None, repr=False)
    otp_ttl_minutes: int = Field(default=5, ge=1, le=15)
    otp_resend_seconds: int = Field(default=60, ge=1, le=600)
    otp_max_attempts: int = Field(default=5, ge=1, le=5)
    access_token_ttl_minutes: int = Field(default=60, ge=5, le=1440)
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str | None = None
    smtp_password: SecretStr | None = Field(default=None, repr=False)
    smtp_from_email: str | None = None
    smtp_starttls: bool = True
    booking_min_duration_minutes: int = Field(default=30, ge=15, le=120)
    booking_max_duration_minutes: int = Field(default=120, ge=30, le=240)
    booking_max_advance_days: int = Field(default=7, ge=1, le=30)
    booking_max_per_day: int = Field(default=1, ge=1, le=10)
    booking_gap_minutes: int = Field(default=15, ge=0, le=120)
    booking_cancel_cutoff_minutes: int = Field(default=30, ge=0, le=1440)
    checkin_grace_minutes: int = Field(default=15, ge=1, le=60)

    model_config = SettingsConfigDict(extra="ignore")

    def email_domain_allowlist(self) -> frozenset[str]:
        return frozenset(
            domain.strip().lower()
            for domain in self.allowed_email_domains.split(",")
            if domain.strip()
        )

    def connection_url(self):
        if self.database_url:
            return self.database_url
        if not all((self.database_host,self.database_name,self.database_user,self.database_password)):
            raise ValueError('Configure DATABASE_URL or all DATABASE_* connection fields')
        return URL.create('postgresql+psycopg',host=self.database_host,port=self.database_port,
                          database=self.database_name,username=self.database_user,
                          password=self.database_password.get_secret_value())


settings = Settings()
