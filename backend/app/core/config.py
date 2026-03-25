from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Exchange Rate Dashboard API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    korea_exim_api_key: str = ""
    exchange_api_base_url: str = (
        "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
    )
    exchange_db_path: str = str(BASE_DIR / "backend" / "data" / "exchange_rates.db")
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    frontend_host: str = "127.0.0.1"
    frontend_port: int = 8501

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
