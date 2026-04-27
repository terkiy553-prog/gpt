from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class MarketDataSource(StrEnum):
    HISTORICAL = "historical"
    PAPER = "paper"
    LIVE = "live"


class MarketEventType(StrEnum):
    TRADE = "trade"
    BOOK = "book"
    KLINE = "kline"
    FUNDING = "funding"
    METADATA = "metadata"


@dataclass(frozen=True, slots=True)
class Symbol:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("symbol is required")
        normalized = self.value.upper()
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class MarketEvent:
    event_id: str
    symbol: Symbol
    event_type: MarketEventType
    source: MarketDataSource
    exchange_time_ms: int
    received_time_ms: int

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id is required")
        if self.exchange_time_ms <= 0:
            raise ValueError("exchange_time_ms must be positive")
        if self.received_time_ms <= 0:
            raise ValueError("received_time_ms must be positive")


@dataclass(frozen=True, slots=True)
class TradeTick:
    event: MarketEvent
    price: Decimal
    quantity: Decimal
    is_buyer_maker: bool
    aggregate_trade_id: int | None = None

    def __post_init__(self) -> None:
        if self.event.event_type != MarketEventType.TRADE:
            raise ValueError("TradeTick requires TRADE event_type")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")


@dataclass(frozen=True, slots=True)
class BookTop:
    event: MarketEvent
    bid_price: Decimal
    bid_quantity: Decimal
    ask_price: Decimal
    ask_quantity: Decimal

    def __post_init__(self) -> None:
        if self.event.event_type != MarketEventType.BOOK:
            raise ValueError("BookTop requires BOOK event_type")
        if self.bid_price <= 0 or self.ask_price <= 0:
            raise ValueError("book prices must be positive")
        if self.bid_quantity < 0 or self.ask_quantity < 0:
            raise ValueError("book quantities cannot be negative")
        if self.ask_price < self.bid_price:
            raise ValueError("ask_price cannot be below bid_price")

    @property
    def spread(self) -> Decimal:
        return self.ask_price - self.bid_price

    @property
    def mid_price(self) -> Decimal:
        return (self.bid_price + self.ask_price) / Decimal("2")
