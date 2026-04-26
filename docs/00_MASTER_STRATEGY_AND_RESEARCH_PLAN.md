# Master Strategy and Research Plan

## Mission

Build a production-grade cryptocurrency futures trading system whose primary optimization target is long-term profit, constrained by safety, auditability, controllability, deterministic backtest/paper/live parity, and clean architecture.

## Core rule

This is not a module-collection project. It is a profit-seeking system with a small canonical architecture, deep validation, realistic execution modeling, and strict live-trading gates.

## Non-negotiables

- Profit is the top optimization objective.
- No hidden fallback.
- No silent alias.
- No duplicate truth.
- No temporary patch logic.
- No live order path before evidence gates.
- Every canonical domain has one owner.
- Backtest, paper, and live share the same contracts.

## Canonical architecture

```text
DataEngine -> RegimeEngine -> EdgeEngine -> DecisionEngine -> RiskEngine -> ExecutionEngine -> AuditEngine
```

## Profit strategy

The system will use a hybrid regime-gated edge allocator:

1. RegimeEngine classifies market state.
2. EdgeEngine scores multiple candidate edge families.
3. DecisionEngine emits one deterministic trade intent.
4. RiskEngine sizes or vetoes.
5. ExecutionEngine simulates or executes with fill constraints.
6. AuditEngine records the full decision trace.

## Initial edge families

- trend continuation after volatility expansion
- mean reversion only in verified chop regimes
- liquidation / flow shock continuation
- funding-pressure filters
- microstructure imbalance as confirmation, not final authority

## Evidence gates

1. Schema gate
2. Replay determinism gate
3. Fee and fill realism gate
4. Out-of-sample robustness gate
5. Regime behavior gate
6. Risk and drawdown gate
7. Paper/live parity gate
8. Tiny controlled live pilot gate

## Live vetoes

Live trading remains disabled if market data is stale, fee model is unknown, symbol filters are missing, risk engine is disabled, audit writer is unavailable, paper/live parity is broken, kill switch is active, or daily loss limit is breached.

## Build phases

Phase 0: governance and protocol.
Phase 1: typed domain contracts.
Phase 2: deterministic engine skeleton.
Phase 3: risk-first execution boundary.
Phase 4: event-driven backtest core.
Phase 5: fill-realism research path.
Phase 6: edge research harness.
Phase 7: paper trading.
Phase 8: controlled live pilot.
