from datetime import date, datetime

from pydantic import BaseModel, Field


class ExchangeRateItem(BaseModel):
    cur_unit: str = Field(..., description="Currency unit code")
    cur_nm: str = Field(..., description="Currency name")
    deal_bas_r: float | None = Field(default=None, description="Base exchange rate")
    ttb: float | None = Field(default=None, description="Telegraphic transfer buying rate")
    tts: float | None = Field(default=None, description="Telegraphic transfer selling rate")


class ExchangeRateResponse(BaseModel):
    source: str
    announcement_date: date | None
    retrieved_at: datetime | None = None
    rates: list[ExchangeRateItem]


class ConfigStatusResponse(BaseModel):
    api_key_configured: bool
    api_base_url: str
    db_path: str


class SyncExchangeRateResponse(BaseModel):
    message: str
    source: str
    announcement_date: date
    rate_count: int


class BackfillExchangeRateResponse(BaseModel):
    message: str
    source: str
    start_date: date
    end_date: date
    saved_days: int
    saved_rates: int
    skipped_days: int


class CurrencyHistoryItem(BaseModel):
    announcement_date: date
    cur_unit: str
    cur_nm: str
    deal_bas_r: float | None
    ttb: float | None
    tts: float | None


class CurrencyHistoryResponse(BaseModel):
    cur_unit: str
    history: list[CurrencyHistoryItem]
