import pytest
from app.models.portfolio import Portfolio, EquityPosition, OptionPosition
from app.services.screener import tag_option_strategies

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
    assert results[0]["symbol"] == "AAPL"
    assert results[0]["option_type"] == "Call"
    assert results[0]["position"] == "Short"
    assert results[0]["tag"] == "Covered Call"
    assert results[0]["coverage_percent"] == 50.0 # 500 shares / 1000 shares equity = 50%

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
    assert results[0]["symbol"] == "GOOG"
    assert results[0]["option_type"] == "Put"
    assert results[0]["position"] == "Long"
    assert results[0]["tag"] == "Protective Put"
    assert results[0]["coverage_percent"] == 50.0 # 100 shares / 200 shares equity = 50%