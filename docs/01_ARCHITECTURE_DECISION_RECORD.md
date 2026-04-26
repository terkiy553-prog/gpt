# Architecture Decision Record 01: Simple Canonical Core, Deep Intelligence Inside

## Status

Accepted.

## Context

The project goal is to build a production-grade cryptocurrency futures trading system focused on long-term profitability while preserving auditability, controllability, deterministic replay, and clean architecture.

The main architectural danger is uncontrolled complexity: many strategy files, overlapping model authorities, hidden fallbacks, duplicate truth, and backtest-only logic. Such complexity can create impressive backtests while making live behavior impossible to understand, control, or reproduce.

## Decision

Use a small canonical core with strict domain ownership:

```text
DataEngine -> RegimeEngine -> EdgeEngine -> DecisionEngine -> RiskEngine -> ExecutionEngine -> AuditEngine
```

No other top-level decision authority is allowed.

## Domain ownership

### DataEngine

Owns market data contracts, validation, normalization, replay order, stale-feed state, and exchange metadata.

### RegimeEngine

Owns market state classification. It decides which edge families are allowed to participate.

### EdgeEngine

Owns candidate edge scoring. It does not place trades and does not bypass risk.

### DecisionEngine

Owns final trade intent. It creates exactly one decision object for each evaluation cycle.

### RiskEngine

Owns final pre-execution veto and sizing constraints. No edge can bypass risk.

### ExecutionEngine

Owns order intent, fill simulation, fees, spread, depth, slippage, and live/paper execution boundaries.

### AuditEngine

Owns replay, traceability, config/code version metadata, and decision evidence.

## Consequences

### Positive

- The system stays understandable and controllable.
- Backtest, paper, and live can share the same contracts.
- Every trade can be traced to regime, edge, decision, risk, execution, and audit records.
- New intelligence can be added without creating new hidden authorities.

### Negative

- Development is slower at the beginning.
- Each new idea must pass domain ownership and evidence gates.
- Experimental strategies cannot be merged into runtime just because one backtest looks profitable.

## Strategy admission rule

A strategy or model is not admitted to canonical runtime unless it improves at least one of:

- post-cost profitability
- robustness across regimes
- drawdown control
- fill quality
- paper/live parity
- auditability
- operational safety

## Live trading rule

Live trading remains disabled until the system passes schema, replay, fill-realism, out-of-sample, paper parity, risk, and audit gates.

## Non-goal

The non-goal is a large collection of independent models or modules. The goal is a simple shell with deeply validated intelligence inside canonical boundaries.
