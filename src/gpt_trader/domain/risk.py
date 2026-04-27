from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from gpt_trader.domain.decision import DecisionAction, TradeDecision
from gpt_trader.domain.market import Symbol


class RiskDecision(StrEnum):
    APPROVED = "approved"
    VETOED = "vetoed"


class RiskVetoReason(StrEnum):
    NONE = "none"
    DECISION_NOT_TRADEABLE = "decision_not_tradeable"
    MAX_NOTIONAL_EXCEEDED = "max_notional_exceeded"
    MAX_LEVERAGE_EXCEEDED = "max_leverage_exceeded"
    DAILY_LOSS_LIMIT_REACHED = "daily_loss_limit_reached"
    DRAWDOWN_LIMIT_REACHED = "drawdown_limit_reached"
    STALE_MARKET_DATA = "stale_market_data"
    LIQUIDITY_NOT_TRADEABLE = "liquidity_not_tradeable"
    KILL_SWITCH_ACTIVE = "kill_switch_active"


@dataclass(frozen=True, slots=True)
class RiskLimits:
    max_position_notional: Decimal
    max_leverage: Decimal
    max_daily_loss: Decimal
    max_drawdown: Decimal
    min_decision_confidence: Decimal

    def __post_init__(self) -> None:
        for name, value in {
            "max_position_notional": self.max_position_notional,
            "max_leverage": self.max_leverage,
            "max_daily_loss": self.max_daily_loss,
            "max_drawdown": self.max_drawdown,
            "min_decision_confidence": self.min_decision_confidence,
        }.items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.max_position_notional == 0:
            raise ValueError("max_position_notional must be positive")
        if self.max_leverage == 0:
            raise ValueError("max_leverage must be positive")
        if self.min_decision_confidence > Decimal("1"):
            raise ValueError("min_decision_confidence cannot exceed 1")


@dataclass(frozen=True, slots=True)
class AccountRiskState:
    equity: Decimal
    current_daily_pnl: Decimal
    current_drawdown: Decimal
    kill_switch_active: bool

    def __post_init__(self) -> None:
        if self.equity <= 0:
            raise ValueError("equity must be positive")
        if self.current_drawdown < 0:
            raise ValueError("current_drawdown cannot be negative")


@dataclass(frozen=True, slots=True)
class RiskResult:
    result_id: str
    symbol: Symbol
    evaluated_at_ms: int
    decision: TradeDecision
    risk_decision: RiskDecision
    veto_reason: RiskVetoReason
    approved_notional: Decimal
    approved_leverage: Decimal
    notes: str

    def __post_init__(self) -> None:
        if not self.result_id:
            raise ValueError("result_id is required")
        if self.evaluated_at_ms <= 0:
            raise ValueError("evaluated_at_ms must be positive")
        if self.approved_notional < 0:
            raise ValueError("approved_notional cannot be negative")
        if self.approved_leverage < 0:
            raise ValueError("approved_leverage cannot be negative")
        if self.risk_decision == RiskDecision.APPROVED:
            if self.veto_reason != RiskVetoReason.NONE:
                raise ValueError("approved risk result cannot have veto reason")
            if self.decision.action not in {DecisionAction.ENTER_LONG, DecisionAction.ENTER_SHORT}:
                raise ValueError("approved risk result requires entry decision")
            if self.approved_notional <= 0 or self.approved_leverage <= 0:
                raise ValueError("approved risk result requires positive notional and leverage")
        if self.risk_decision == RiskDecision.VETOED:
            if self.veto_reason == RiskVetoReason.NONE:
                raise ValueError("vetoed risk result requires veto reason")
            if self.approved_notional != 0 or self.approved_leverage != 0:
                raise ValueError("vetoed risk result cannot approve notional or leverage")
