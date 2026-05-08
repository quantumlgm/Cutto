from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ENV_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    ALLOW_ORIGINS: list[str]
    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_EXPERATION: int
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def DB_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_URL_psycopg(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(env_file=ENV_DIR / ".env")


settings = Settings()
