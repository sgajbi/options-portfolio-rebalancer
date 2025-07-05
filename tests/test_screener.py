import pytest
from app.models.portfolio import Portfolio 
from app.models.option_position import OptionPosition
from app.models.equity_position import EquityPosition
from app.services.screener import tag_option_strategies
from app.models.options import TaggedOptionPosition
from datetime import datetime, timedelta, date # Import date


def create_option(
    symbol: str, 
    option_type: str, 
    position: str, 
    strike: float, 
    expiry: date, # Changed from str to date
    contracts: int = 1,
    isin: str = None
) -> OptionPosition:
    if isin is None:
        # Generate a simple unique ISIN for testing. Convert expiry to string for ISIN generation.
        isin = f"{symbol}-{option_type}-{strike}-{expiry.strftime('%Y-%m-%d')}-{position}-{contracts}-{datetime.now().microsecond}"

    return OptionPosition(
        type="Option",
        symbol=symbol,
        option_type=option_type,
        strike=strike,
        expiry=expiry, # expiry is already a date object here
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
                "expiry": "2026-12-31", # This will be converted to date by Pydantic
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
    assert isinstance(result, TaggedOptionPosition)
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
                "expiry": "2026-06-30", # This will be converted to date by Pydantic
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
    assert isinstance(result, TaggedOptionPosition)
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
                "expiry": "2025-09-20", # This will be converted to date by Pydantic
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
    assert isinstance(result, TaggedOptionPosition)
    assert result.symbol == "TSLA"
    assert result.option_type == "Call"
    assert result.position == "Short"
    assert result.tag == "Naked"
    assert result.coverage_percent == 0.0

def test_tag_naked_put_no_equity():
    """
    Test that a long put option with no underlying equity (and thus no protective put context) is tagged as 'Naked'.
    This test is more about confirming the default 'Naked' for other option types/positions.
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
                "expiry": "2025-10-17", # This will be converted to date by Pydantic
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
    assert isinstance(result, TaggedOptionPosition)
    assert result.symbol == "AMZN"
    assert result.option_type == "Put"
    assert result.position == "Short"
    assert result.tag == "Naked"
    assert result.coverage_percent == 0.0


def test_long_straddle_identification():
    """Tests correct identification of a Long Straddle (Long Call + Long Put, same strike, same expiry)."""
    # Create test_expiry as a date object
    test_expiry = (datetime.now() + timedelta(days=90)).date() 
    
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
    
    # Sort for consistent assertion order
    tagged_options.sort(key=lambda x: (x.symbol, x.option_type, x.strike, x.expiry))

    assert len(tagged_options) == 2
    
    assert tagged_options[0].symbol == "SPY"
    assert tagged_options[0].option_type == "Call"
    assert tagged_options[0].position == "Long"
    assert tagged_options[0].strike == 400.0
    # Direct comparison of date objects
    assert tagged_options[0].expiry == test_expiry 
    assert tagged_options[0].tag == "Long Straddle"
    assert tagged_options[0].coverage_percent == 0.0

    assert tagged_options[1].symbol == "SPY"
    assert tagged_options[1].option_type == "Put"
    assert tagged_options[1].position == "Long"
    assert tagged_options[1].strike == 400.0
    # Direct comparison of date objects
    assert tagged_options[1].expiry == test_expiry
    assert tagged_options[1].tag == "Long Straddle"
    assert tagged_options[1].coverage_percent == 0.0

def test_short_straddle_identification():
    """Tests correct identification of a Short Straddle (Short Call + Short Put, same strike, same expiry)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date() # Changed to date object
    
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
    tagged_options.sort(key=lambda x: (x.symbol, x.option_type, x.strike, x.expiry))

    assert len(tagged_options) == 2
    assert tagged_options[0].tag == "Short Straddle"
    assert tagged_options[1].tag == "Short Straddle"


def test_long_strangle_identification():
    """Tests correct identification of a Long Strangle (Long Call + Long Put, different strikes, same expiry)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date() # Changed to date object
    
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
    tagged_options.sort(key=lambda x: (x.symbol, x.option_type, x.strike, x.expiry))

    assert len(tagged_options) == 2
    # Call will come first due to sorting by option_type
    assert tagged_options[0].symbol == "QQQ" and tagged_options[0].option_type == "Call" and tagged_options[0].tag == "Long Strangle"
    assert tagged_options[1].symbol == "QQQ" and tagged_options[1].option_type == "Put" and tagged_options[1].tag == "Long Strangle"


def test_short_strangle_identification():
    """Tests correct identification of a Short Strangle (Short Call + Short Put, different strikes, same expiry)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date() # Changed to date object
    
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
    tagged_options.sort(key=lambda x: (x.symbol, x.option_type, x.strike, x.expiry))

    assert len(tagged_options) == 2
    assert tagged_options[0].tag == "Short Strangle"
    assert tagged_options[1].tag == "Short Strangle"


def test_call_vertical_spread_identification():
    """Tests correct identification of a Call Vertical Spread (e.g., Bull Call Spread: Long Call Lower Strike + Short Call Higher Strike)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date() # Changed to date object
    
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
    tagged_options.sort(key=lambda x: (x.symbol, x.option_type, x.strike, x.expiry))

    assert len(tagged_options) == 2
    assert tagged_options[0].tag == "Call Vertical Spread"
    assert tagged_options[1].tag == "Call Vertical Spread"


def test_put_vertical_spread_identification():
    """Tests correct identification of a Put Vertical Spread (e.g., Bear Put Spread: Long Put Higher Strike + Short Put Lower Strike)."""
    test_expiry = (datetime.now() + timedelta(days=90)).date() # Changed to date object
    
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
    tagged_options.sort(key=lambda x: (x.symbol, x.option_type, x.strike, x.expiry))

    assert len(tagged_options) == 2
    assert tagged_options[0].tag == "Put Vertical Spread"
    assert tagged_options[1].tag == "Put Vertical Spread"


def test_mixed_options_with_multi_leg_and_naked():
    """Tests a portfolio with a mix of multi-leg strategies and naked options,
    including one that forms a Short Strangle and another that remains Naked."""
    test_expiry_spy = (datetime.now() + timedelta(days=90)).date() # Changed to date object
    test_expiry_aapl = (datetime.now() + timedelta(days=60)).date() # Changed to date object
    test_expiry_msft = (datetime.now() + timedelta(days=120)).date() # Changed to date object

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
            # 2. Long Call 450 (will be Naked)
            # 3. Short Call 460 (will form Short Strangle with Short Put 440)
            create_option("MSFT", "Put", "Short", 440.0, test_expiry_msft, isin="MSFT-SP-440-mixed"),
            create_option("MSFT", "Call", "Long", 450.0, test_expiry_msft, isin="MSFT-LC-450-mixed"),
            create_option("MSFT", "Call", "Short", 460.0, test_expiry_msft, isin="MSFT-SC-460-mixed"),
        ],
    )

    tagged_options = tag_option_strategies(portfolio)
    # Sort for consistent assertion order, useful for debugging
    tagged_options.sort(key=lambda x: (x.symbol, x.option_type, x.strike, x.expiry, x.position))

    assert len(tagged_options) == 6 # Expecting 2 for SPY, 1 for AAPL, 3 for MSFT

    # Assert SPY (Long Straddle)
    spy_options = [o for o in tagged_options if o.symbol == "SPY"]
    assert len(spy_options) == 2
    assert all(o.tag == "Long Straddle" for o in spy_options)

    # Assert AAPL (Covered Call)
    aapl_options = [o for o in tagged_options if o.symbol == "AAPL"]
    assert len(aapl_options) == 1
    assert aapl_options[0].tag == "Covered Call"
    assert aapl_options[0].coverage_percent == 100.0 

    # Assert MSFT breakdown
    msft_options = [o for o in tagged_options if o.symbol == "MSFT"]
    assert len(msft_options) == 3
    
    # Expected: One Short Strangle (2 options) and one Naked (1 option)
    short_strangle_options = [o for o in msft_options if o.tag == "Short Strangle"]
    naked_options = [o for o in msft_options if o.tag == "Naked"]

    assert len(short_strangle_options) == 2
    assert len(naked_options) == 1

    # Verify the specific options tagged as Short Strangle
    # The Short Put 440 and Short Call 460 form the Short Strangle
    strangle_put = next((o for o in short_strangle_options if o.option_type == "Put" and o.strike == 440.0), None)
    strangle_call = next((o for o in short_strangle_options if o.option_type == "Call" and o.strike == 460.0), None)
    
    assert strangle_put is not None
    assert strangle_call is not None

    # Verify the specific option tagged as Naked
    # The Long Call 450 should be Naked
    naked_long_call = next((o for o in naked_options if o.option_type == "Call" and o.position == "Long" and o.strike == 450.0), None)
    assert naked_long_call is not None
    assert naked_long_call.tag == "Naked"
    assert naked_long_call.coverage_percent == 0.0 # Naked options have 0 coverage

def test_option_not_tagged_if_processed_elsewhere():
    """Ensures an option is only tagged once even if it matches multiple simple rules."""
    test_expiry = (datetime.now() + timedelta(days=90)).date() # Changed to date object
    
    # This scenario is specifically for Straddles/Strangles/Spreads logic,
    # where an option might *look* naked if considered alone, but is part of a multi-leg.
    # The `processed_option_ids` set handles this.
    
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
    
    tagged_options = tag_option_strategies(portfolio)
    assert len(tagged_options) == 2
    assert all(o.tag == "Long Straddle" for o in tagged_options)
    # The key here is that neither option should be tagged as "Naked" in addition to "Long Straddle".
    # The `processed_option_ids` set should ensure this.