import pytest
from app.models.portfolio import Portfolio
from app.models.option_position import OptionPosition
from app.models.equity_position import EquityPosition
from app.services.screener import tag_option_strategies
from app.models.options import TaggedOptionPosition
from app.models.option_strategy import OptionStrategy
from datetime import datetime, date, timedelta
from typing import Union 


def create_option(
    symbol: str,
    option_type: str,
    position: str,
    strike: float,
    expiry: Union[str, date], 
    contracts: int = 1,
    isin: str = None
) -> OptionPosition:
    if isin is None:
        # Generate a simple unique ISIN for testing
        isin = f"{symbol}-{option_type}-{strike}-{expiry}-{position}-{contracts}-{datetime.now().microsecond}"

    if isinstance(expiry, str):
        expiry_date_obj = datetime.strptime(expiry, "%Y-%m-%d").date()
    else:
        expiry_date_obj = expiry

    return OptionPosition(
        type="Option",
        symbol=symbol,
        option_type=option_type,
        strike=strike,
        expiry=expiry_date_obj, # Use the date object
        position=position,
        contracts=contracts,
        price_at_purchase=1.0,
        current_price=1.5,
        market_value=1.5 * contracts * 100,
        isin=isin,
        instrument_currency="USD",
    )

def test_tag_covered_call():
    """
    Test that a short call option with sufficient underlying equity is tagged as 'Covered Call'.
    """
    portfolio_data = {
        "portfolio_id": "TEST_PF_001",
        "portfolio_currency": "USD",
        "investment_horizon_years": 5,
        "risk_profile": "Moderate",
        "product_knowledge": ["Equity", "Option"],
        "positions": [
            {
                "type": "Equity",
                "symbol": "AAPL",
                "quantity": 1000,
                "cio_rating": "Hold",
                "average_cost_price": 150.0,
                "instrument_currency": "USD",
                "market_value": 170000.0,
                "isin": "US0378331005"
            },
            {
                "type": "Option",
                "symbol": "AAPL",
                "option_type": "Call",
                "strike": 170.0,
                "expiry": "2026-12-31",
                "position": "Short",
                "contracts": 5, # 5 contracts * 100 shares/contract = 500 shares exposure
                "price_at_purchase": 2.0,
                "current_price": 2.5,
                "market_value": 1250.0,
                "isin": "US0378331005",
                "instrument_currency": "USD"
            }
        ]
    }

    portfolio = Portfolio(**portfolio_data)
    results = tag_option_strategies(portfolio)

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, TaggedOptionPosition) # Should still be TaggedOptionPosition
    assert result.symbol == "AAPL"
    assert result.option_type == "Call"
    assert result.position == "Short"
    assert result.tag == "Covered Call"
    assert result.coverage_percent == 100.0

def test_tag_protective_put():
    """
    Test that a long put option with sufficient underlying equity is tagged as 'Protective Put'.
    """
    portfolio_data = {
        "portfolio_id": "TEST_PF_002",
        "portfolio_currency": "USD",
        "investment_horizon_years": 5,
        "risk_profile": "Moderate",
        "product_knowledge": ["Equity", "Option"],
        "positions": [
            {
                "type": "Equity",
                "symbol": "GOOG",
                "quantity": 200,
                "cio_rating": "Buy",
                "average_cost_price": 120.0,
                "instrument_currency": "USD",
                "market_value": 25000.0,
                "isin": "US02079K1079"
            },
            {
                "type": "Option",
                "symbol": "GOOG",
                "option_type": "Put",
                "strike": 110.0,
                "expiry": "2026-06-30",
                "position": "Long",
                "contracts": 1, # 1 contract * 100 shares/contract = 100 shares exposure
                "price_at_purchase": 3.0,
                "current_price": 4.0,
                "market_value": 400.0,
                "isin": "US02079K1079",
                "instrument_currency": "USD"
            }
        ]
    }

    portfolio = Portfolio(**portfolio_data)
    results = tag_option_strategies(portfolio)

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, TaggedOptionPosition) # Should still be TaggedOptionPosition
    assert result.symbol == "GOOG"
    assert result.option_type == "Put"
    assert result.position == "Long"
    assert result.tag == "Protective Put"
    assert result.coverage_percent == 100.0

def test_tag_naked_call_no_equity():
    """
    Test that a short call option with no underlying equity is tagged as 'Naked'.
    """
    portfolio_data = {
        "portfolio_id": "TEST_PF_003",
        "portfolio_currency": "USD",
        "investment_horizon_years": 5,
        "risk_profile": "Aggressive",
        "product_knowledge": ["Option"],
        "positions": [
            {
                "type": "Option",
                "symbol": "TSLA",
                "option_type": "Call",
                "strike": 200.0,
                "expiry": "2025-09-20",
                "position": "Short",
                "contracts": 2, # 2 contracts = 200 shares exposure
                "price_at_purchase": 10.0,
                "current_price": 12.0,
                "market_value": 2400.0,
                "isin": "US88160R1014",
                "instrument_currency": "USD"
            }
        ]
    }

    portfolio = Portfolio(**portfolio_data)
    results = tag_option_strategies(portfolio)

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, TaggedOptionPosition) # Should still be TaggedOptionPosition
    assert result.symbol == "TSLA"
    assert result.option_type == "Call"
    assert result.position == "Short"
    assert result.tag == "Naked" # Or "Partially Covered Call" if equity_held_shares > 0
    assert result.coverage_percent == 0.0

def test_tag_naked_put_no_equity():
    """
    Test that a short put option (which is inherently naked if no cash/securities reserve is modeled)
    is tagged as 'Naked' or 'Short Put'.
    """
    portfolio_data = {
        "portfolio_id": "TEST_PF_004",
        "portfolio_currency": "USD",
        "investment_horizon_years": 5,
        "risk_profile": "Aggressive",
        "product_knowledge": ["Option"],
        "positions": [
            {
                "type": "Option",
                "symbol": "AMZN",
                "option_type": "Put",
                "strike": 140.0,
                "expiry": "2025-10-17",
                "position": "Short", # A naked short put (selling puts without cash/securities for obligation)
                "contracts": 1,
                "price_at_purchase": 5.0,
                "current_price": 6.0,
                "market_value": 600.0,
                "isin": "US0231351067",
                "instrument_currency": "USD"
            }
        ]
    }

    portfolio = Portfolio(**portfolio_data)
    results = tag_option_strategies(portfolio)

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, TaggedOptionPosition) # Should still be TaggedOptionPosition
    assert result.symbol == "AMZN"
    assert result.option_type == "Put"
    assert result.position == "Short"
    assert result.tag == "Short Put" # Changed from "Naked" to "Short Put" for clarity as per options.py
    assert result.coverage_percent == 0.0

def test_long_straddle_identification():
    """Tests correct identification of a Long Straddle (Long Call + Long Put, same strike, same expiry)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date() # Use date object

    portfolio = Portfolio(
        portfolio_id="test_straddle",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option"],
        positions=[
            create_option("SPY", "Call", "Long", 400.0, test_expiry, isin="SPY-LC-400"),
            create_option("SPY", "Put", "Long", 400.0, test_expiry, isin="SPY-LP-400"),
        ],
    )

    tagged_options = tag_option_strategies(portfolio)

    assert len(tagged_options) == 1 # Expecting one OptionStrategy object
    strategy = tagged_options[0]
    assert isinstance(strategy, OptionStrategy)
    assert strategy.strategy_name == "Long Straddle"
    assert strategy.underlying_symbol == "SPY"
    assert strategy.expiry_date == test_expiry
    assert len(strategy.legs) == 2

    # Verify legs within the strategy
    call_leg = next((leg for leg in strategy.legs if leg.option_type == "Call"), None)
    put_leg = next((leg for leg in strategy.legs if leg.option_type == "Put"), None)

    assert call_leg is not None
    assert put_leg is not None
    assert call_leg.position == "Long"
    assert put_leg.position == "Long"
    assert call_leg.strike == 400.0
    assert put_leg.strike == 400.0

    # Check net premium
    assert strategy.net_premium_paid_received == (1.0 * 1 * 100) + (1.0 * 1 * 100) # (premium paid for call) + (premium paid for put) = 200.0


def test_short_straddle_identification():
    """Tests correct identification of a Short Straddle (Short Call + Short Put, same strike, same expiry)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date()

    portfolio = Portfolio(
        portfolio_id="test_short_straddle",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option"],
        positions=[
            create_option("SPY", "Call", "Short", 400.0, test_expiry, isin="SPY-SC-400"),
            create_option("SPY", "Put", "Short", 400.0, test_expiry, isin="SPY-SP-400"),
        ],
    )

    tagged_options = tag_option_strategies(portfolio)

    assert len(tagged_options) == 1
    strategy = tagged_options[0]
    assert isinstance(strategy, OptionStrategy)
    assert strategy.strategy_name == "Short Straddle"
    assert strategy.underlying_symbol == "SPY"
    assert strategy.expiry_date == test_expiry
    assert len(strategy.legs) == 2
    assert strategy.net_premium_paid_received == -(1.0 * 1 * 100) - (1.0 * 1 * 100) # (premium received for call) + (premium received for put) = -200.0


def test_long_strangle_identification():
    """Tests correct identification of a Long Strangle (Long Call + Long Put, different strikes, same expiry)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date()

    portfolio = Portfolio(
        portfolio_id="test_strangle",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option"],
        positions=[
            create_option("QQQ", "Call", "Long", 380.0, test_expiry, isin="QQQ-LC-380"), # Higher strike Call
            create_option("QQQ", "Put", "Long", 370.0, test_expiry, isin="QQQ-LP-370"), # Lower strike Put
        ],
    )

    tagged_options = tag_option_strategies(portfolio)

    assert len(tagged_options) == 1
    strategy = tagged_options[0]
    assert isinstance(strategy, OptionStrategy)
    assert strategy.strategy_name == "Long Strangle"
    assert strategy.underlying_symbol == "QQQ"
    assert strategy.expiry_date == test_expiry
    assert len(strategy.legs) == 2
    assert strategy.net_premium_paid_received == (1.0 * 1 * 100) + (1.0 * 1 * 100) # 200.0


def test_short_strangle_identification():
    """Tests correct identification of a Short Strangle (Short Call + Short Put, different strikes, same expiry)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date()

    portfolio = Portfolio(
        portfolio_id="test_short_strangle",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option"],
        positions=[
            create_option("QQQ", "Call", "Short", 380.0, test_expiry, isin="QQQ-SC-380"),
            create_option("QQQ", "Put", "Short", 370.0, test_expiry, isin="QQQ-SP-370"),
        ],
    )

    tagged_options = tag_option_strategies(portfolio)

    assert len(tagged_options) == 1
    strategy = tagged_options[0]
    assert isinstance(strategy, OptionStrategy)
    assert strategy.strategy_name == "Short Strangle"
    assert strategy.underlying_symbol == "QQQ"
    assert strategy.expiry_date == test_expiry
    assert len(strategy.legs) == 2
    assert strategy.net_premium_paid_received == -(1.0 * 1 * 100) - (1.0 * 1 * 100) # -200.0


def test_call_vertical_spread_identification():
    """Tests correct identification of a Call Vertical Spread (e.g., Bull Call Spread: Long Call Lower Strike + Short Call Higher Strike)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date()

    portfolio = Portfolio(
        portfolio_id="test_call_spread",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option"],
        positions=[
            create_option("MSFT", "Call", "Long", 450.0, test_expiry, isin="MSFT-LC-450"), # Buy lower strike call
            create_option("MSFT", "Call", "Short", 460.0, test_expiry, isin="MSFT-SC-460"), # Sell higher strike call
        ],
    )

    tagged_options = tag_option_strategies(portfolio)

    assert len(tagged_options) == 1
    strategy = tagged_options[0]
    assert isinstance(strategy, OptionStrategy)
    assert strategy.strategy_name == "Call Vertical Spread"
    assert strategy.underlying_symbol == "MSFT"
    assert strategy.expiry_date == test_expiry
    assert len(strategy.legs) == 2
    # Long call premium (1.0 * 1 * 100) + Short call premium (-1.0 * 1 * 100) = 0.0
    assert strategy.net_premium_paid_received == (1.0 * 1 * 100) - (1.0 * 1 * 100)


def test_put_vertical_spread_identification():
    """Tests correct identification of a Put Vertical Spread (e.g., Bear Put Spread: Long Put Higher Strike + Short Put Lower Strike)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date()

    portfolio = Portfolio(
        portfolio_id="test_put_spread",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option"],
        positions=[
            create_option("GOOG", "Put", "Long", 180.0, test_expiry, isin="GOOG-LP-180"), # Buy higher strike put
            create_option("GOOG", "Put", "Short", 170.0, test_expiry, isin="GOOG-SP-170"), # Sell lower strike put
        ],
    )

    tagged_options = tag_option_strategies(portfolio)

    assert len(tagged_options) == 1
    strategy = tagged_options[0]
    assert isinstance(strategy, OptionStrategy)
    assert strategy.strategy_name == "Put Vertical Spread"
    assert strategy.underlying_symbol == "GOOG"
    assert strategy.expiry_date == test_expiry
    assert len(strategy.legs) == 2
    # Long put premium (1.0 * 1 * 100) + Short put premium (-1.0 * 1 * 100) = 0.0
    assert strategy.net_premium_paid_received == (1.0 * 1 * 100) - (1.0 * 1 * 100)


def test_mixed_options_with_multi_leg_and_naked():
    """Tests a portfolio with a mix of multi-leg strategies and single-leg options."""
    test_expiry_spy = (datetime.now() + timedelta(days=90)).date()
    test_expiry_aapl = (datetime.now() + timedelta(days=60)).date()
    test_expiry_msft = (datetime.now() + timedelta(days=120)).date()

    portfolio = Portfolio(
        portfolio_id="test_mixed",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option", "Equity"],
        positions=[
            EquityPosition(
                type="Equity",
                symbol="AAPL",
                quantity=200,
                cio_rating="Buy",
                average_cost_price=170.0,
                instrument_currency="USD",
                market_value=35000.0,
                isin="US0378331005",
            ),
            # Long Straddle on SPY
            create_option("SPY", "Call", "Long", 400.0, test_expiry_spy, isin="SPY-LC-400-mixed"),
            create_option("SPY", "Put", "Long", 400.0, test_expiry_spy, isin="SPY-LP-400-mixed"),
            # Covered Call on AAPL (1 contract covered by 200 shares)
            create_option("AAPL", "Call", "Short", 180.0, test_expiry_aapl, isin="AAPL-SC-180-mixed"),

            # Options for MSFT:
            # 1. Short Put 440 (will form Short Strangle with Short Call 460)
            # 2. Long Call 450 (will be Long Call)
            # 3. Short Call 460 (will form Short Strangle with Short Put 440)
            create_option("MSFT", "Put", "Short", 440.0, test_expiry_msft, isin="MSFT-SP-440-mixed"),
            create_option("MSFT", "Call", "Long", 450.0, test_expiry_msft, isin="MSFT-LC-450-mixed"),
            create_option("MSFT", "Call", "Short", 460.0, test_expiry_msft, isin="MSFT-SC-460-mixed"),
        ],
    )

    results = tag_option_strategies(portfolio)

    # We expect 2 OptionStrategy objects (SPY Long Straddle, MSFT Short Strangle)
    # and 2 TaggedOptionPosition objects (AAPL Covered Call, MSFT Long Call)
    assert len(results) == 4

    spy_strategy = next((r for r in results if isinstance(r, OptionStrategy) and r.underlying_symbol == "SPY"), None)
    assert spy_strategy is not None
    assert spy_strategy.strategy_name == "Long Straddle"
    assert len(spy_strategy.legs) == 2
    assert spy_strategy.net_premium_paid_received == 200.0

    aapl_tagged = next((r for r in results if isinstance(r, TaggedOptionPosition) and r.symbol == "AAPL"), None)
    assert aapl_tagged is not None
    assert aapl_tagged.tag == "Covered Call"
    assert aapl_tagged.coverage_percent == 100.0

    msft_strangle_strategy = next((r for r in results if isinstance(r, OptionStrategy) and r.underlying_symbol == "MSFT"), None)
    assert msft_strangle_strategy is not None
    assert msft_strangle_strategy.strategy_name == "Short Strangle"
    assert len(msft_strangle_strategy.legs) == 2
    assert msft_strangle_strategy.net_premium_paid_received == -200.0

    msft_long_call_tagged = next((r for r in results if isinstance(r, TaggedOptionPosition) and r.symbol == "MSFT" and r.option_type == "Call" and r.position == "Long"), None)
    assert msft_long_call_tagged is not None
    assert msft_long_call_tagged.tag == "Long Call"
    assert msft_long_call_tagged.coverage_percent == 0.0


def test_option_not_tagged_if_processed_elsewhere():
    """Ensures an option is only tagged once by being part of a multi-leg strategy."""
    test_expiry = (datetime.now() + timedelta(days=90)).date()

    portfolio = Portfolio(
        portfolio_id="test_deduplication",
        portfolio_currency="USD",
        investment_horizon_years=5,
        risk_profile="Moderate",
        product_knowledge=["Option"],
        positions=[
            create_option("XYZ", "Call", "Long", 50.0, test_expiry, isin="XYZ-LC-50"),
            create_option("XYZ", "Put", "Long", 50.0, test_expiry, isin="XYZ-LP-50"),
        ],
    )

    results = tag_option_strategies(portfolio)
    assert len(results) == 1 # Expecting one OptionStrategy object
    strategy = results[0]
    assert isinstance(strategy, OptionStrategy)
    assert strategy.strategy_name == "Long Straddle"
    assert len(strategy.legs) == 2
    # The key here is that individual options within the straddle are not also returned as "Naked" TaggedOptionPosition.