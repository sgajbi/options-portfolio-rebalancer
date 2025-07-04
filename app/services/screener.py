from typing import List
from ..models.portfolio import Portfolio, EquityPosition, OptionPosition
from ..models.options import TaggedOptionPosition

def tag_option_strategies(portfolio: Portfolio) -> List[TaggedOptionPosition]:
    """
    Analyzes option positions within a portfolio to identify and tag common strategies
    like Covered Calls and Protective Puts, and calculates hedge coverage.
    """
    equity_map = {
        p.symbol: p.quantity
        for p in portfolio.positions
        if isinstance(p, EquityPosition) 
    }

    results: List[TaggedOptionPosition] = []

    for pos in portfolio.positions:
        if isinstance(pos, OptionPosition):
            symbol = pos.symbol
            contracts = pos.contracts
            option_type = pos.option_type
            position_type = pos.position
            strike = pos.strike
            expiry = pos.expiry

            option_exposure = contracts * 100
            equity_exposure = equity_map.get(symbol, 0)

            tag: Literal["Naked", "Covered Call", "Protective Put"] = "Naked"
            coverage: float = 0.0

            if position_type == "Short" and option_type == "Call":
                if equity_exposure > 0:
                    coverage = min(100.0, round((option_exposure / equity_exposure) * 100, 2))
                    tag = "Covered Call"
            elif position_type == "Long" and option_type == "Put":
                if equity_exposure > 0:
                    coverage = min(100.0, round((option_exposure / equity_exposure) * 100, 2))
                    tag = "Protective Put"


            results.append(
                TaggedOptionPosition(
                    symbol=symbol,
                    option_type=option_type,
                    position=position_type,
                    strike=strike,
                    expiry=expiry,
                    tag=tag,
                    coverage_percent=coverage
                )
            )

    return results