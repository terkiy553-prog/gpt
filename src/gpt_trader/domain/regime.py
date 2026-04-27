from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from gpt_trader.domain.market import Symbol


class TrendState(StrEnum):
    STRONG_UP = "strong_up"
    UP = "up"
    FLAT = "flat"
    DOWN = "down"
    STRONG_DOWN = "strong_down"
    UNKNOWN = "unknown"


class VolatilityState(StrEnum):
    COMPRESSED = "compressed"
    NORMAL = "normal"
    EXPANDING = "expanding"
    EXTREME = "extreme"
    UNKNOWN = "unknown"


class LiquidityState(StrEnum):
    HEALTHY = "healthy"
    THIN = "thin"
    DEGRADED = "degraded"
    DISORDERLY = "disorderly"
    UNKNOWN = "unknown"


class RegimeVetoReason(StrEnum):
    NONE = "none"
    UNKNOWN_MARKET_STATE = "unknown_market_state"
    DISORDERLY_LIQUIDITY = "disorderly_liquidity"
    EXTREME_VOLATILITY = "extreme_volatility"
    LOW_CONFIDENCE = "low_confidence"


@dataclass(frozen=True, slots=True)
class RegimeState:
    symbol: Symbol
    evaluated_at_ms: int
    trend: TrendState
    volatility: VolatilityState
    liquidity: LiquidityState
    confidence: Decimal
    allowed_edge_families: tuple[str, ...]
    veto_reason: RegimeVetoReason = RegimeVetoReason.NONE

    def __post_init__(self) -> None:
        if self.evaluated_at_ms <= 0:
            raise ValueError("evaluated_at_ms must be positive")
        if not Decimal("0") <= self.confidence <= Decimal("1"):
            raise ValueError("confidence must be between 0 and 1")
        if self.veto_reason != RegimeVetoReason.NONE and self.allowed_edge_families:
            raise ValueError("vetoed regime cannot allow edge families")

    @property
    def allows_trading(self) -> bool:
        return self.veto_reason == RegimeVetoReason.NONE and bool(self.allowed_edge_families)
