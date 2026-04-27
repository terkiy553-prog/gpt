from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from gpt_trader.domain.market import Symbol
from gpt_trader.domain.risk import RiskDecision, RiskResult


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    TAKE_PROFIT_MARKET = "take_profit_market"


class TimeInForce(StrEnum):
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"


class ExecutionMode(StrEnum):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


class ExecutionVetoReason(StrEnum):
    NONE = "none"
    RISK_NOT_APPROVED = "risk_not_approved"
    INVALID_ORDER_SIZE = "invalid_order_size"
    INVALID_PRICE = "invalid_price"
    EXCHANGE_FILTER_MISSING = "exchange_filter_missing"
    LIVE_TRADING_DISABLED = "live_trading_disabled"


@dataclass(frozen=True, slots=True)
class ExecutionIntent:
    intent_id: str
    symbol: Symbol
    created_at_ms: int
    mode: ExecutionMode
    risk_result: RiskResult
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    notional: Decimal
    limit_price: Decimal | None
    time_in_force: TimeInForce | None
    reduce_only: bool
    veto_reason: ExecutionVetoReason = ExecutionVetoReason.NONE

    def __post_init__(self) -> None:
        if not self.intent_id:
            raise ValueError("intent_id is required")
        if self.created_at_ms <= 0:
            raise ValueError("created_at_ms must be positive")
        if self.risk_result.risk_decision != RiskDecision.APPROVED:
            if self.veto_reason != ExecutionVetoReason.RISK_NOT_APPROVED:
                raise ValueError("unapproved risk requires RISK_NOT_APPROVED execution veto")
            if self.quantity != 0 or self.notional != 0:
                raise ValueError("vetoed execution cannot have quantity or notional")
            return
        if self.veto_reason != ExecutionVetoReason.NONE:
            if self.quantity != 0 or self.notional != 0:
                raise ValueError("vetoed execution cannot have quantity or notional")
            return
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.notional <= 0:
            raise ValueError("notional must be positive")
        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("limit order requires limit_price")
        if self.limit_price is not None and self.limit_price <= 0:
            raise ValueError("limit_price must be positive")


@dataclass(frozen=True, slots=True)
class FillEvent:
    fill_id: str
    intent_id: str
    symbol: Symbol
    exchange_time_ms: int
    side: OrderSide
    price: Decimal
    quantity: Decimal
    fee: Decimal
    liquidity: str

    def __post_init__(self) -> None:
        if not self.fill_id:
            raise ValueError("fill_id is required")
        if not self.intent_id:
            raise ValueError("intent_id is required")
        if self.exchange_time_ms <= 0:
            raise ValueError("exchange_time_ms must be positive")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.fee < 0:
            raise ValueError("fee cannot be negative")
        if self.liquidity not in {"maker", "taker", "simulated"}:
            raise ValueError("liquidity must be maker, taker, or simulated")
