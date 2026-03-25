from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.repositories.exchange_rate_repository import ExchangeRateRepository
from backend.app.schemas.exchange_rate import (
    BackfillExchangeRateResponse,
    ConfigStatusResponse,
    CurrencyHistoryItem,
    CurrencyHistoryResponse,
    ExchangeRateItem,
    ExchangeRateResponse,
    SyncExchangeRateResponse,
)
from backend.app.services.exchange_rate_service import ExchangeRateService
from datetime import date, timedelta

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


@router.post("/backfill", response_model=BackfillExchangeRateResponse)
def backfill_rates(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
) -> BackfillExchangeRateResponse:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작일은 종료일보다 이후일 수 없습니다.")

    service = ExchangeRateService()
    repository = ExchangeRateRepository(db)

    saved_days = 0
    saved_rates = 0
    skipped_days = 0
    cursor = start_date

    while cursor <= end_date:
        try:
            rates = service.fetch_by_date(cursor)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"{cursor.isoformat()} 환율 조회 중 오류가 발생했습니다: {exc}",
            ) from exc

        if rates:
            snapshot = repository.save_snapshot(
                announcement_date=cursor,
                source="koreaexim",
                rates=rates,
            )
            saved_days += 1
            saved_rates += len(snapshot.rates)
        else:
            skipped_days += 1

        cursor += timedelta(days=1)

    return BackfillExchangeRateResponse(
        message="기간 환율 적재가 완료되었습니다.",
        source="koreaexim",
        start_date=start_date,
        end_date=end_date,
        saved_days=saved_days,
        saved_rates=saved_rates,
        skipped_days=skipped_days,
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
