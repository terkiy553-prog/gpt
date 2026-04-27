from __future__ import annotations

from gpt_trader.domain.audit import AuditEvent
from gpt_trader.engines.base import Engine, EngineMetadata


class InMemoryAuditEngine(Engine):
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def metadata(self) -> EngineMetadata:
        return EngineMetadata("in_memory_audit_engine", "0.1.0", True)

    def record(self, event: AuditEvent) -> None:
        self._events.append(event)

    def all_events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def count(self) -> int:
        return len(self._events)
