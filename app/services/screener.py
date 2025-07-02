from typing import List, Dict
from ..models.portfolio import Portfolio


def tag_option_strategies(portfolio: Portfolio) -> List[Dict]:
    equity_map = {
        p.symbol: p.quantity
        for p in portfolio.positions
        if p.type == "Equity"
    }

    results = []

    for pos in portfolio.positions:
        if pos.type == "Option":
            symbol = pos.symbol
            contracts = pos.contracts
            option_type = pos.option_type
            position_type = pos.position

            option_exposure = contracts * 100
            equity_exposure = equity_map.get(symbol, 0)

            tag = "Naked"
            coverage = 0

            if position_type == "Short" and option_type == "Call":
                if equity_exposure > 0:
                    coverage = min(100, round((option_exposure / equity_exposure) * 100, 2))
                    tag = "Covered Call"
            elif position_type == "Long" and option_type == "Put":
                if equity_exposure > 0:
                    coverage = min(100, round((option_exposure / equity_exposure) * 100, 2))
                    tag = "Protective Put"

            results.append({
                "symbol": symbol,
                "option_type": option_type,
                "position": position_type,
                "strike": pos.strike,
                "expiry": pos.expiry,
                "tag": tag,
                "coverage_percent": coverage
            })

    return results
