from __future__ import annotations

from decimal import Decimal

from gpt_trader.domain.decision import DecisionAction, TradeDecision
from gpt_trader.domain.risk import AccountRiskState, RiskDecision, RiskLimits, RiskResult, RiskVetoReason
from gpt_trader.engines.base import Engine, EngineMetadata


class BasicRiskEngine(Engine):
    def __init__(self, limits: RiskLimits) -> None:
        self._limits = limits

    @property
    def metadata(self) -> EngineMetadata:
        return EngineMetadata("basic_risk_engine", "0.1.0", True)

    def evaluate(
        self,
        result_id: str,
        evaluated_at_ms: int,
        decision: TradeDecision,
        account_state: AccountRiskState,
        requested_notional: Decimal,
        requested_leverage: Decimal,
        market_data_stale: bool,
    ) -> RiskResult:
        veto = self._veto(decision, account_state, requested_notional, requested_leverage, market_data_stale)
        if veto != RiskVetoReason.NONE:
            return RiskResult(result_id, decision.symbol, evaluated_at_ms, decision, RiskDecision.VETOED, veto, Decimal("0"), Decimal("0"), veto.value)
        return RiskResult(result_id, decision.symbol, evaluated_at_ms, decision, RiskDecision.APPROVED, RiskVetoReason.NONE, requested_notional, requested_leverage, "approved")

    def _veto(
        self,
        decision: TradeDecision,
        account_state: AccountRiskState,
        requested_notional: Decimal,
        requested_leverage: Decimal,
        market_data_stale: bool,
    ) -> RiskVetoReason:
        if account_state.kill_switch_active:
            return RiskVetoReason.KILL_SWITCH_ACTIVE
        if market_data_stale:
            return RiskVetoReason.STALE_MARKET_DATA
        if decision.action not in {DecisionAction.ENTER_LONG, DecisionAction.ENTER_SHORT}:
            return RiskVetoReason.DECISION_NOT_TRADEABLE
        if decision.confidence < self._limits.min_decision_confidence:
            return RiskVetoReason.DECISION_NOT_TRADEABLE
        if requested_notional <= 0 or requested_notional > self._limits.max_position_notional:
            return RiskVetoReason.MAX_NOTIONAL_EXCEEDED
        if requested_leverage <= 0 or requested_leverage > self._limits.max_leverage:
            return RiskVetoReason.MAX_LEVERAGE_EXCEEDED
        if account_state.current_daily_pnl <= -self._limits.max_daily_loss:
            return RiskVetoReason.DAILY_LOSS_LIMIT_REACHED
        if account_state.current_drawdown >= self._limits.max_drawdown:
            return RiskVetoReason.DRAWDOWN_LIMIT_REACHED
        return RiskVetoReason.NONE
