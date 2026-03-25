from datetime import date, timedelta

import requests

from backend.app.core.config import settings


class ExchangeRateService:
    def __init__(self) -> None:
        self.base_url = settings.exchange_api_base_url
        self.api_key = settings.korea_exim_api_key

    @staticmethod
    def _parse_rate_value(raw_value: str | None) -> float | None:
        if raw_value is None:
            return None

        cleaned = raw_value.replace(",", "").strip()
        if not cleaned:
            return None

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _request_rates(self, search_date: date) -> list[dict]:
        response = requests.get(
            self.base_url,
            params={
                "authkey": self.api_key,
                "searchdate": search_date.strftime("%Y%m%d"),
                "data": "AP01",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def fetch_latest_available(self, lookback_days: int = 10) -> tuple[date, list[dict]]:
        if not self.api_key:
            raise ValueError("KOREA_EXIM_API_KEY is not configured.")

        today = date.today()
        for offset in range(lookback_days + 1):
            target_date = today - timedelta(days=offset)
            payload = self._request_rates(target_date)
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                normalized = [
                    {
                        "cur_unit": item.get("cur_unit", "").strip(),
                        "cur_nm": item.get("cur_nm", "").strip(),
                        "deal_bas_r": self._parse_rate_value(item.get("deal_bas_r")),
                        "ttb": self._parse_rate_value(item.get("ttb")),
                        "tts": self._parse_rate_value(item.get("tts")),
                    }
                    for item in payload
                    if item.get("cur_unit")
                ]
                if normalized:
                    return target_date, normalized

        raise ValueError("No exchange rate data was returned for the recent dates checked.")

    def get_config_status(self) -> dict[str, str | bool]:
        return {
            "api_key_configured": bool(self.api_key),
            "api_base_url": self.base_url,
            "db_path": settings.exchange_db_path,
        }
