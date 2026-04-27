from decimal import Decimal

from gpt_trader.domain.risk import AccountRiskState, RiskLimits
from gpt_trader.engines.risk_engine import BasicRiskEngine


def test_basic_risk_engine_metadata() -> None:
    engine = BasicRiskEngine(
        RiskLimits(
            Decimal("1000"),
            Decimal("3"),
            Decimal("100"),
            Decimal("200"),
            Decimal("0.6"),
        )
    )
    assert engine.metadata.name == "basic_risk_engine"
    assert engine.metadata.deterministic is True


def test_account_risk_state_requires_positive_equity() -> None:
    try:
        AccountRiskState(Decimal("0"), Decimal("0"), Decimal("0"), False)
    except ValueError as exc:
        assert "equity" in str(exc)
    else:
        raise AssertionError("expected ValueError")
