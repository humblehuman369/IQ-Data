from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'FlipCycle API'
    environment: str = Field(default='development', alias='ENVIRONMENT')
    api_prefix: str = '/api'
    allowed_origins: list[str] = ['http://localhost:3000', 'https://flipcycle.vercel.app']

    database_url: str = Field(default='postgresql+psycopg://flipcycle:flipcycle@localhost:5432/flipcycle', alias='DATABASE_URL')
    redis_url: str = Field(default='redis://localhost:6379/0', alias='REDIS_URL')

    jwt_secret: SecretStr = Field(default='change-me-in-production', alias='JWT_SECRET')
    jwt_algorithm: str = 'HS256'
    access_token_minutes: int = 60
    refresh_token_days: int = 14

    stripe_secret_key: SecretStr | None = Field(default=None, alias='STRIPE_SECRET_KEY')
    stripe_webhook_secret: SecretStr | None = Field(default=None, alias='STRIPE_WEBHOOK_SECRET')
    resend_api_key: SecretStr | None = Field(default=None, alias='RESEND_API_KEY')
    anthropic_api_key: SecretStr | None = Field(default=None, alias='ANTHROPIC_API_KEY')
    aws_access_key_id: SecretStr | None = Field(default=None, alias='AWS_ACCESS_KEY_ID')
    aws_secret_access_key: SecretStr | None = Field(default=None, alias='AWS_SECRET_ACCESS_KEY')
    aws_region: str = Field(default='us-east-1', alias='AWS_REGION')
    s3_bucket: str | None = Field(default=None, alias='S3_BUCKET')
    sentry_dsn: str | None = Field(default=None, alias='SENTRY_DSN')

    def normalized_database_url(self) -> str:
        if self.database_url.startswith('postgres://'):
            return self.database_url.replace('postgres://', 'postgresql+psycopg://', 1)
        if self.database_url.startswith('postgresql://'):
            return self.database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
