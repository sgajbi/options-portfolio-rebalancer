import pytest
from app.models.portfolio import Portfolio, EquityPosition, OptionPosition
from app.services.screener import tag_option_strategies
from app.models.options import TaggedOptionPosition

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
    assert isinstance(result, TaggedOptionPosition)
    assert result.symbol == "AAPL"
    assert result.option_type == "Call"
    assert result.position == "Short"
    assert result.tag == "Covered Call"
    assert result.coverage_percent == 50.0

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
    assert isinstance(result, TaggedOptionPosition)
    assert result.symbol == "GOOG"
    assert result.option_type == "Put"
    assert result.position == "Long"
    assert result.tag == "Protective Put"
    assert result.coverage_percent == 50.0

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
    assert isinstance(result, TaggedOptionPosition)
    assert result.symbol == "AMZN"
    assert result.option_type == "Put"
    assert result.position == "Short"
    assert result.tag == "Naked"
    assert result.coverage_percent == 0.0