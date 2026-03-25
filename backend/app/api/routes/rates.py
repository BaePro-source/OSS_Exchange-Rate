from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.repositories.exchange_rate_repository import ExchangeRateRepository
from backend.app.schemas.exchange_rate import (
    ConfigStatusResponse,
    CurrencyHistoryItem,
    CurrencyHistoryResponse,
    ExchangeRateItem,
    ExchangeRateResponse,
    SyncExchangeRateResponse,
)
from backend.app.services.exchange_rate_service import ExchangeRateService

router = APIRouter()


@router.get("/latest", response_model=ExchangeRateResponse)
def get_latest_rates(db: Session = Depends(get_db)) -> ExchangeRateResponse:
    snapshot = ExchangeRateRepository(db).get_latest_snapshot()
    if snapshot is None:
        return ExchangeRateResponse(
            source="koreaexim",
            announcement_date=None,
            retrieved_at=None,
            rates=[],
        )

    return ExchangeRateResponse(
        source=snapshot.source,
        announcement_date=snapshot.announcement_date,
        retrieved_at=snapshot.retrieved_at,
        rates=[
            ExchangeRateItem(
                cur_unit=rate.cur_unit,
                cur_nm=rate.cur_nm,
                deal_bas_r=rate.deal_bas_r,
                ttb=rate.ttb,
                tts=rate.tts,
            )
            for rate in snapshot.rates
        ],
    )


@router.get("/config-status", response_model=ConfigStatusResponse)
def get_config_status() -> ConfigStatusResponse:
    return ConfigStatusResponse(**ExchangeRateService().get_config_status())


@router.post("/sync", response_model=SyncExchangeRateResponse)
def sync_latest_rates(db: Session = Depends(get_db)) -> SyncExchangeRateResponse:
    service = ExchangeRateService()
    try:
        announcement_date, rates = service.fetch_latest_available()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch exchange rates: {exc}") from exc

    snapshot = ExchangeRateRepository(db).save_snapshot(
        announcement_date=announcement_date,
        source="koreaexim",
        rates=rates,
    )
    return SyncExchangeRateResponse(
        message="Exchange rates synced successfully.",
        source=snapshot.source,
        announcement_date=snapshot.announcement_date,
        rate_count=len(snapshot.rates),
    )


@router.get("/history/{cur_unit}", response_model=CurrencyHistoryResponse)
def get_currency_history(
    cur_unit: str,
    limit: int = 30,
    db: Session = Depends(get_db),
) -> CurrencyHistoryResponse:
    history = ExchangeRateRepository(db).get_currency_history(cur_unit=cur_unit, limit=limit)
    return CurrencyHistoryResponse(
        cur_unit=cur_unit.upper(),
        history=[
            CurrencyHistoryItem(
                announcement_date=rate.snapshot.announcement_date,
                cur_unit=rate.cur_unit,
                cur_nm=rate.cur_nm,
                deal_bas_r=rate.deal_bas_r,
                ttb=rate.ttb,
                tts=rate.tts,
            )
            for rate in history
        ],
    )
