from typing import List, Dict
from collections import defaultdict
from ..models.portfolio import Portfolio
from ..models.equity_position import EquityPosition
from ..models.options import TaggedOptionPosition
from ..models.option_position import OptionPosition


def tag_option_strategies(portfolio: Portfolio) -> List[TaggedOptionPosition]:
    """
    Analyzes option positions within a portfolio to identify and tag common strategies
    like Covered Calls, Protective Puts, Straddles, Strangles, and Spreads.
    """
    equity_map = {
        p.symbol: p.quantity
        for p in portfolio.positions
        if isinstance(p, EquityPosition)
    }

    # Group options by symbol and then by expiry for easier identification of multi-leg strategies
    options_by_symbol_expiry: Dict[str, Dict[str, List[OptionPosition]]] = defaultdict(lambda: defaultdict(list))
    
    # Store all options in a flat list to keep track of already processed options
    all_options_list: List[OptionPosition] = []

    for pos in portfolio.positions:
        if isinstance(pos, OptionPosition):
            options_by_symbol_expiry[pos.symbol][pos.expiry].append(pos)
            all_options_list.append(pos)

    results: List[TaggedOptionPosition] = []
    
    # Keep track of options that have been tagged as part of a multi-leg strategy
    # to avoid double-tagging them as 'Naked' or other single-leg strategies.
    processed_option_ids = set() 

    # --- Strategy Identification Logic ---

    # 1. Identify Straddles (Long or Short)
    # A straddle involves buying/selling both a call and a put with the same strike and expiry on the same underlying.
    for symbol, expiries in options_by_symbol_expiry.items():
        for expiry, options_list_for_expiry in expiries.items(): # Renamed to avoid confusion
            calls = [op for op in options_list_for_expiry if op.option_type == "Call" and op.isin not in processed_option_ids]
            puts = [op for op in options_list_for_expiry if op.option_type == "Put" and op.isin not in processed_option_ids]
            

            # Sort by strike for easier matching
            calls.sort(key=lambda x: x.strike)
            puts.sort(key=lambda x: x.strike)

            # Look for exact strike matches
            matched_straddles = []
            for call in calls:
                for put in puts:
                    if call.strike == put.strike and call.position == put.position:
                        # Ensure both legs haven't been processed yet
                        if call.isin not in processed_option_ids and put.isin not in processed_option_ids:
                            matched_straddles.append((call, put))
            
            for call, put in matched_straddles:
                tag_name = f"{call.position} Straddle"
                results.append(
                    TaggedOptionPosition(
                        symbol=call.symbol,
                        option_type=call.option_type,
                        position=call.position,
                        strike=call.strike,
                        expiry=call.expiry,
                        tag=tag_name,
                        coverage_percent=0.0 # Straddles typically have no equity coverage
                    )
                )
                results.append(
                    TaggedOptionPosition(
                        symbol=put.symbol,
                        option_type=put.option_type,
                        position=put.position,
                        strike=put.strike,
                        expiry=put.expiry,
                        tag=tag_name,
                        coverage_percent=0.0
                    )
                )
                processed_option_ids.add(call.isin)
                processed_option_ids.add(put.isin)

    # 2. Identify Strangles (Long or Short)
    # A strangle involves buying/selling both a call and a put with different strikes but same expiry on the same underlying.
    # The call strike is higher than the put strike.
    for symbol, expiries in options_by_symbol_expiry.items():
        for expiry, options_list_for_expiry in expiries.items():
            calls = [op for op in options_list_for_expiry if op.option_type == "Call" and op.isin not in processed_option_ids]
            puts = [op for op in options_list_for_expiry if op.option_type == "Put" and op.isin not in processed_option_ids]
            
            calls.sort(key=lambda x: x.strike)
            puts.sort(key=lambda x: x.strike)

            matched_strangles = []
            for call in calls:
                for put in puts:
                    # Check for different strikes, same position (both long or both short), and call strike > put strike
                    if (call.strike > put.strike and 
                        call.position == put.position and 
                        call.isin not in processed_option_ids and 
                        put.isin not in processed_option_ids):
                        matched_strangles.append((call, put))
                        
            for call, put in matched_strangles:
                tag_name = f"{call.position} Strangle"
                results.append(
                    TaggedOptionPosition(
                        symbol=call.symbol,
                        option_type=call.option_type,
                        position=call.position,
                        strike=call.strike,
                        expiry=call.expiry,
                        tag=tag_name,
                        coverage_percent=0.0
                    )
                )
                results.append(
                    TaggedOptionPosition(
                        symbol=put.symbol,
                        option_type=put.option_type,
                        position=put.position,
                        strike=put.strike,
                        expiry=put.expiry,
                        tag=tag_name,
                        coverage_percent=0.0
                    )
                )
                processed_option_ids.add(call.isin)
                processed_option_ids.add(put.isin)

    # 3. Identify Spreads (Vertical) - Simplified
    # Looks for two options of the *same type* and *same expiry*, but *different strikes* and *opposite positions*.
    for symbol, expiries in options_by_symbol_expiry.items():
        for expiry, options_list_for_expiry in expiries.items():
            # Filter options not yet processed
            remaining_options_for_spread = [op for op in options_list_for_expiry if op.isin not in processed_option_ids]
            
            # Sort by strike
            remaining_options_for_spread.sort(key=lambda x: x.strike)

            matched_spreads = []
            for i in range(len(remaining_options_for_spread)):
                for j in range(i + 1, len(remaining_options_for_spread)):
                    option1 = remaining_options_for_spread[i]
                    option2 = remaining_options_for_spread[j]

                    # Check if they are of the same type (Call/Call or Put/Put)
                    if option1.option_type == option2.option_type:
                        # Check if they have opposite positions (Long/Short)
                        if (option1.position == "Long" and option2.position == "Short") or \
                           (option1.position == "Short" and option2.position == "Long"):
                            
                            # Check if both haven't been processed
                            if option1.isin not in processed_option_ids and option2.isin not in processed_option_ids:
                                matched_spreads.append((option1, option2))
            
            for option1, option2 in matched_spreads:
                tag_name = f"{option1.option_type} Vertical Spread" # Simplified naming
                results.append(
                    TaggedOptionPosition(
                        symbol=option1.symbol,
                        option_type=option1.option_type,
                        position=option1.position,
                        strike=option1.strike,
                        expiry=option1.expiry,
                        tag=tag_name,
                        coverage_percent=0.0
                    )
                )
                results.append(
                    TaggedOptionPosition(
                        symbol=option2.symbol,
                        option_type=option2.option_type,
                        position=option2.position,
                        strike=option2.strike,
                        expiry=option2.expiry,
                        tag=tag_name,
                        coverage_percent=0.0
                    )
                )
                processed_option_ids.add(option1.isin)
                processed_option_ids.add(option2.isin)
    
    # 4. Process remaining single-leg options (Covered Call, Protective Put, Naked)
    # This loop now only processes options that haven't been identified as part of a multi-leg strategy.
    for pos in all_options_list: # Iterate through the original flat list of all options
        if pos.isin in processed_option_ids:
            continue # Skip options already processed in multi-leg strategies

        symbol = pos.symbol
        contracts = pos.contracts
        option_type = pos.option_type
        position_type = pos.position
        strike = pos.strike
        expiry = pos.expiry

        option_exposure = contracts * 100
        equity_exposure = equity_map.get(symbol, 0)

        tag: str = "Naked" # Default to Naked
        coverage: float = 0.0

        if position_type == "Short" and option_type == "Call":
            if equity_exposure > 0 and option_exposure > 0:
                coverage = min(100.0, round((equity_exposure / option_exposure) * 100, 2))
                tag = "Covered Call"
            # If no equity, it remains "Naked" as initialized.
        elif position_type == "Long" and option_type == "Put":
            if equity_exposure > 0 and option_exposure > 0:
                coverage = min(100.0, round((equity_exposure / option_exposure) * 100, 2))
                tag = "Protective Put"
            # If no equity, it remains "Naked" as initialized.

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