from decimal import Decimal

import pytest

from gpt_trader.domain.market import (
    BookTop,
    MarketDataSource,
    MarketEvent,
    MarketEventType,
    Symbol,
    TradeTick,
)
from gpt_trader.domain.regime import (
    LiquidityState,
    RegimeState,
    RegimeVetoReason,
    TrendState,
    VolatilityState,
)


def test_symbol_normalizes_to_uppercase() -> None:
    assert Symbol("btcusdt").value == "BTCUSDT"


def test_trade_tick_requires_positive_price_and_quantity() -> None:
    event = MarketEvent("e1", Symbol("BTCUSDT"), MarketEventType.TRADE, MarketDataSource.HISTORICAL, 1, 2)
    tick = TradeTick(event, Decimal("100"), Decimal("0.5"), False)
    assert tick.price == Decimal("100")
    with pytest.raises(ValueError):
        TradeTick(event, Decimal("0"), Decimal("0.5"), False)


def test_book_top_rejects_crossed_book() -> None:
    event = MarketEvent("e2", Symbol("BTCUSDT"), MarketEventType.BOOK, MarketDataSource.HISTORICAL, 1, 2)
    with pytest.raises(ValueError):
        BookTop(event, Decimal("101"), Decimal("1"), Decimal("100"), Decimal("1"))


def test_vetoed_regime_cannot_allow_edges() -> None:
    with pytest.raises(ValueError):
        RegimeState(
            Symbol("BTCUSDT"),
            1,
            TrendState.UNKNOWN,
            VolatilityState.UNKNOWN,
            LiquidityState.DISORDERLY,
            Decimal("0.1"),
            ("trend_continuation",),
            RegimeVetoReason.DISORDERLY_LIQUIDITY,
        )
