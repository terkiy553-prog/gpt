from __future__ import annotations

from decimal import Decimal

from gpt_trader.domain.decision import DecisionAction, DecisionReason, TradeDecision
from gpt_trader.domain.edge import EdgeDirection, EdgeSignal
from gpt_trader.domain.market import Symbol
from gpt_trader.domain.regime import RegimeState
from gpt_trader.engines.base import Engine, EngineMetadata


class DeterministicDecisionEngine(Engine):
    @property
    def metadata(self) -> EngineMetadata:
        return EngineMetadata("deterministic_decision_engine", "0.1.0", True)

    def decide(
        self,
        decision_id: str,
        symbol: Symbol,
        evaluated_at_ms: int,
        regime: RegimeState,
        edge_signals: tuple[EdgeSignal, ...],
    ) -> TradeDecision:
        candidates = tuple(edge for edge in edge_signals if edge.is_trade_candidate)
        if not regime.allows_trading:
            return self._final(decision_id, symbol, evaluated_at_ms, DecisionAction.VETO, DecisionReason.REGIME_VETO, Decimal("0"), regime, None, edge_signals, "regime veto")
        if not candidates:
            return self._final(decision_id, symbol, evaluated_at_ms, DecisionAction.HOLD, DecisionReason.NO_EDGE, Decimal("0"), regime, None, edge_signals, "no active edge")
        directions = {edge.direction for edge in candidates}
        if EdgeDirection.LONG in directions and EdgeDirection.SHORT in directions:
            return self._final(decision_id, symbol, evaluated_at_ms, DecisionAction.VETO, DecisionReason.CONFLICTING_EDGES, Decimal("0"), regime, None, edge_signals, "conflicting edge directions")
        selected = max(candidates, key=lambda edge: (edge.confidence, abs(edge.score)))
        action = DecisionAction.ENTER_LONG if selected.direction == EdgeDirection.LONG else DecisionAction.ENTER_SHORT
        return self._final(decision_id, symbol, evaluated_at_ms, action, DecisionReason.EDGE_CONFIRMED, selected.confidence, regime, selected, edge_signals, selected.reason)

    def _final(
        self,
        decision_id: str,
        symbol: Symbol,
        evaluated_at_ms: int,
        action: DecisionAction,
        reason: DecisionReason,
        confidence: Decimal,
        regime: RegimeState,
        selected_edge: EdgeSignal | None,
        all_edges: tuple[EdgeSignal, ...],
        notes: str,
    ) -> TradeDecision:
        edge_ids = tuple(edge.family.value for edge in all_edges)
        return TradeDecision(decision_id, symbol, evaluated_at_ms, action, reason, confidence, regime, selected_edge, edge_ids, notes)
