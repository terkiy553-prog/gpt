from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from gpt_trader.domain.market import Symbol
from gpt_trader.domain.regime import RegimeState


class EdgeFamily(StrEnum):
    TREND_CONTINUATION = "trend_continuation"
    VOLATILITY_BREAKOUT = "volatility_breakout"
    MEAN_REVERSION = "mean_reversion"
    FLOW_SHOCK = "flow_shock"
    FUNDING_PRESSURE = "funding_pressure"
    MICROSTRUCTURE_CONFIRMATION = "microstructure_confirmation"


class EdgeDirection(StrEnum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


class EdgeStatus(StrEnum):
    ACTIVE = "active"
    VETOED_BY_REGIME = "vetoed_by_regime"
    INSUFFICIENT_CONFIDENCE = "insufficient_confidence"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class EdgeSignal:
    symbol: Symbol
    family: EdgeFamily
    direction: EdgeDirection
    status: EdgeStatus
    score: Decimal
    confidence: Decimal
    horizon_seconds: int
    reason: str
    regime: RegimeState

    def __post_init__(self) -> None:
        if not Decimal("-1") <= self.score <= Decimal("1"):
            raise ValueError("score must be between -1 and 1")
        if not Decimal("0") <= self.confidence <= Decimal("1"):
            raise ValueError("confidence must be between 0 and 1")
        if self.horizon_seconds <= 0:
            raise ValueError("horizon_seconds must be positive")
        if not self.reason:
            raise ValueError("reason is required")
        if self.status != EdgeStatus.ACTIVE and self.direction != EdgeDirection.FLAT:
            raise ValueError("inactive edge must use FLAT direction")
        if self.status == EdgeStatus.ACTIVE and self.family.value not in self.regime.allowed_edge_families:
            raise ValueError("active edge family is not allowed by regime")

    @property
    def is_trade_candidate(self) -> bool:
        return self.status == EdgeStatus.ACTIVE and self.direction != EdgeDirection.FLAT
