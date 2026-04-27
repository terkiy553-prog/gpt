from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from gpt_trader.domain.edge import EdgeSignal
from gpt_trader.domain.market import Symbol
from gpt_trader.domain.regime import RegimeState


class DecisionAction(StrEnum):
    HOLD = "hold"
    ENTER_LONG = "enter_long"
    ENTER_SHORT = "enter_short"
    EXIT = "exit"
    REDUCE = "reduce"
    VETO = "veto"


class DecisionReason(StrEnum):
    EDGE_CONFIRMED = "edge_confirmed"
    NO_EDGE = "no_edge"
    REGIME_VETO = "regime_veto"
    LOW_CONFIDENCE = "low_confidence"
    CONFLICTING_EDGES = "conflicting_edges"
    RISK_RESERVED = "risk_reserved"


@dataclass(frozen=True, slots=True)
class TradeDecision:
    decision_id: str
    symbol: Symbol
    evaluated_at_ms: int
    action: DecisionAction
    reason: DecisionReason
    confidence: Decimal
    regime: RegimeState
    selected_edge: EdgeSignal | None
    all_edge_ids: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id is required")
        if self.evaluated_at_ms <= 0:
            raise ValueError("evaluated_at_ms must be positive")
        if not Decimal("0") <= self.confidence <= Decimal("1"):
            raise ValueError("confidence must be between 0 and 1")
        if self.action in {DecisionAction.ENTER_LONG, DecisionAction.ENTER_SHORT}:
            if self.selected_edge is None:
                raise ValueError("entry decision requires selected_edge")
            if not self.selected_edge.is_trade_candidate:
                raise ValueError("entry decision requires trade candidate edge")
        if self.action == DecisionAction.VETO and self.reason == DecisionReason.EDGE_CONFIRMED:
            raise ValueError("veto decision cannot use EDGE_CONFIRMED reason")

    @property
    def requests_position_change(self) -> bool:
        return self.action in {
            DecisionAction.ENTER_LONG,
            DecisionAction.ENTER_SHORT,
            DecisionAction.EXIT,
            DecisionAction.REDUCE,
        }
