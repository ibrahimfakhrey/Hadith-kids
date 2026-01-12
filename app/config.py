from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App settings
    app_name: str = "Hadith API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database settings
    database_url: str = "sqlite:///./data/hadith.db"

    # Meilisearch settings
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = ""
    meilisearch_index: str = "hadiths"

    # API settings
    api_prefix: str = "/api/v1"

    # Hadith data source
    hadith_api_base_url: str = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1"

    # JWT Authentication settings
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
