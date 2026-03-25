from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.exchange_rate import ExchangeRate, ExchangeRateSnapshot


class ExchangeRateRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_snapshot(self) -> ExchangeRateSnapshot | None:
        stmt = (
            select(ExchangeRateSnapshot)
            .options(joinedload(ExchangeRateSnapshot.rates))
            .order_by(ExchangeRateSnapshot.announcement_date.desc(), ExchangeRateSnapshot.id.desc())
        )
        return self.db.execute(stmt).unique().scalars().first()

    def get_snapshot_by_date(self, announcement_date: date) -> ExchangeRateSnapshot | None:
        stmt = (
            select(ExchangeRateSnapshot)
            .options(joinedload(ExchangeRateSnapshot.rates))
            .where(ExchangeRateSnapshot.announcement_date == announcement_date)
        )
        return self.db.execute(stmt).unique().scalars().first()

    def save_snapshot(
        self,
        announcement_date: date,
        source: str,
        rates: list[dict],
    ) -> ExchangeRateSnapshot:
        snapshot = self.get_snapshot_by_date(announcement_date)
        if snapshot is None:
            snapshot = ExchangeRateSnapshot(
                announcement_date=announcement_date,
                source=source,
            )
            self.db.add(snapshot)
            self.db.flush()
        else:
            snapshot.source = source
            snapshot.rates.clear()
            self.db.flush()

        for rate in rates:
            snapshot.rates.append(
                ExchangeRate(
                    cur_unit=rate["cur_unit"],
                    cur_nm=rate["cur_nm"],
                    deal_bas_r=rate["deal_bas_r"],
                    ttb=rate["ttb"],
                    tts=rate["tts"],
                )
            )

        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_currency_history(self, cur_unit: str, limit: int = 30) -> list[ExchangeRate]:
        stmt = (
            select(ExchangeRate)
            .options(joinedload(ExchangeRate.snapshot))
            .where(ExchangeRate.cur_unit == cur_unit.upper())
            .join(ExchangeRate.snapshot)
            .order_by(ExchangeRateSnapshot.announcement_date.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).unique().scalars().all())
