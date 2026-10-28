#config for the application

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str
    JWT_EXPIRATION_TIME: int
    GOOGLE_API_KEY: SecretStr

settings = Settings()