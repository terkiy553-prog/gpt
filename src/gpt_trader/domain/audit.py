from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from gpt_trader.domain.decision import TradeDecision
from gpt_trader.domain.execution import ExecutionIntent, FillEvent
from gpt_trader.domain.market import Symbol
from gpt_trader.domain.risk import RiskResult


class AuditEventType(StrEnum):
    DECISION = "decision"
    RISK = "risk"
    EXECUTION_INTENT = "execution_intent"
    FILL = "fill"


@dataclass(frozen=True, slots=True)
class AuditContext:
    run_id: str
    config_hash: str
    code_version: str
    mode: str

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run_id is required")
        if not self.config_hash:
            raise ValueError("config_hash is required")
        if not self.code_version:
            raise ValueError("code_version is required")


@dataclass(frozen=True, slots=True)
class AuditEvent:
    audit_id: str
    event_type: AuditEventType
    symbol: Symbol
    created_at_ms: int
    context: AuditContext
    decision: TradeDecision | None = None
    risk_result: RiskResult | None = None
    execution_intent: ExecutionIntent | None = None
    fill_event: FillEvent | None = None
    input_hash: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.audit_id:
            raise ValueError("audit_id is required")
        if self.created_at_ms <= 0:
            raise ValueError("created_at_ms must be positive")
        payloads = (
            self.decision,
            self.risk_result,
            self.execution_intent,
            self.fill_event,
        )
        if sum(value is not None for value in payloads) != 1:
            raise ValueError("audit event must contain exactly one payload")
