from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base


class ExchangeRateSnapshot(Base):
    __tablename__ = "exchange_rate_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    announcement_date: Mapped[date] = mapped_column(Date, index=True)
    source: Mapped[str] = mapped_column(String(32), default="koreaexim")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    rates: Mapped[list["ExchangeRate"]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (UniqueConstraint("snapshot_id", "cur_unit", name="uq_snapshot_currency"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("exchange_rate_snapshots.id", ondelete="CASCADE"),
        index=True,
    )
    cur_unit: Mapped[str] = mapped_column(String(16), index=True)
    cur_nm: Mapped[str] = mapped_column(String(64))
    deal_bas_r: Mapped[float | None] = mapped_column(Float, nullable=True)
    ttb: Mapped[float | None] = mapped_column(Float, nullable=True)
    tts: Mapped[float | None] = mapped_column(Float, nullable=True)

    snapshot: Mapped[ExchangeRateSnapshot] = relationship(back_populates="rates")
