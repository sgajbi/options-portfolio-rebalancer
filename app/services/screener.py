from typing import List, Dict, Tuple, Union
from collections import defaultdict
from ..models.portfolio import Portfolio
from ..models.equity_position import EquityPosition
from ..models.options import TaggedOptionPosition
from ..models.option_position import OptionPosition
from ..models.option_strategy import OptionStrategy 
import uuid 

OPTION_MULTIPLIER = 100

def _calculate_net_premium(options: List[OptionPosition]) -> float:
    """Calculates the net premium paid/received for a list of option positions."""
    net_premium = 0.0
    for op in options:
        transaction_value = op.price_at_purchase * op.contracts * OPTION_MULTIPLIER
        if op.position == "Long":
            net_premium += transaction_value
        else: 
            net_premium -= transaction_value
    return net_premium

def _identify_straddles(
    options_list: List[OptionPosition],
    processed_option_ids: set
) -> List[OptionStrategy]: 
    """
    Identifies Straddle strategies within a list of options.
    A straddle involves buying/selling both a call and a put with the same strike and expiry on the same underlying.
    """
    results: List[OptionStrategy] = [] 
    
    calls = [op for op in options_list if op.option_type == "Call" and op.isin not in processed_option_ids]
    puts = [op for op in options_list if op.option_type == "Put" and op.isin not in processed_option_ids]
    
    # Sorting is not strictly necessary for correctness here, but can help with consistency if processing order matters for ISINs
    calls.sort(key=lambda x: x.strike)
    puts.sort(key=lambda x: x.strike)

    matched_straddles = []
    for call in calls:
        for put in puts:
            if (call.symbol == put.symbol and 
                call.expiry == put.expiry and 
                call.strike == put.strike and
                call.position == put.position):
                
                if call.isin not in processed_option_ids and put.isin not in processed_option_ids:
                    matched_straddles.append((call, put))
    
    for call, put in matched_straddles:
        strategy_name = f"{call.position} Straddle"
        
        strategy_id = str(uuid.uuid4())

        results.append(
            OptionStrategy(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                underlying_symbol=call.symbol,
                expiry_date=call.expiry,
                legs=[call, put],
                net_premium_paid_received=_calculate_net_premium([call, put])
            )
        )
        processed_option_ids.add(call.isin)
        processed_option_ids.add(put.isin)
            
    return results

def _identify_strangles(
    options_list: List[OptionPosition],
    processed_option_ids: set
) -> List[OptionStrategy]: 
    """
    Identifies Strangle strategies within a list of options.
    A strangle involves buying/selling both a call and a put with different strikes
    but same expiry on the same underlying, where the call strike is higher than the put strike.
    """
    results: List[OptionStrategy] = [] 

    calls = [op for op in options_list if op.option_type == "Call" and op.isin not in processed_option_ids]
    puts = [op for op in options_list if op.option_type == "Put" and op.isin not in processed_option_ids]
    
    calls.sort(key=lambda x: x.strike)
    puts.sort(key=lambda x: x.strike)

    matched_strangles = []
    for call in calls:
        for put in puts:
            # Check for same underlying, same expiry, different strikes, same position (both long or both short), and call strike > put strike
            if (call.symbol == put.symbol and 
                call.expiry == put.expiry and 
                call.strike > put.strike and
                call.position == put.position):
                

                if call.isin not in processed_option_ids and put.isin not in processed_option_ids:
                    matched_strangles.append((call, put))
                
    for call, put in matched_strangles:
        strategy_name = f"{call.position} Strangle"
        strategy_id = str(uuid.uuid4()) 

        results.append(
            OptionStrategy(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                underlying_symbol=call.symbol,
                expiry_date=call.expiry,
                legs=[call, put],
                net_premium_paid_received=_calculate_net_premium([call, put])
            )
        )
        processed_option_ids.add(call.isin)
        processed_option_ids.add(put.isin)

    return results

def _identify_vertical_spreads(
    options_list: List[OptionPosition],
    processed_option_ids: set
) -> List[OptionStrategy]:
    """
    Identifies Vertical Spread strategies within a list of options.
    Looks for two options of the same type and same expiry, but different strikes and opposite positions.
    """
    results: List[OptionStrategy] = [] # Changed to OptionStrategy

    remaining_options_for_spread = [op for op in options_list if op.isin not in processed_option_ids]
    remaining_options_for_spread.sort(key=lambda x: x.strike)

    matched_spreads = []
    for i in range(len(remaining_options_for_spread)):
        for j in range(i + 1, len(remaining_options_for_spread)):
            option1 = remaining_options_for_spread[i]
            option2 = remaining_options_for_spread[j]

            if (option1.symbol == option2.symbol and
                option1.expiry == option2.expiry and
                option1.option_type == option2.option_type and 
                option1.strike != option2.strike): 
                
                # Opposite positions (Long and Short)
                if (option1.position == "Long" and option2.position == "Short") or \
                   (option1.position == "Short" and option2.position == "Long"):
                    
                    # Ensure options haven't been processed yet
                    if option1.isin not in processed_option_ids and option2.isin not in processed_option_ids:
                        matched_spreads.append((option1, option2))
            
    for option1, option2 in matched_spreads:
        strategy_name = f"{option1.option_type} Vertical Spread" 
        strategy_id = str(uuid.uuid4()) 

        results.append(
            OptionStrategy(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                underlying_symbol=option1.symbol,
                expiry_date=option1.expiry,
                legs=[option1, option2],
                net_premium_paid_received=_calculate_net_premium([option1, option2])
            )
        )
        processed_option_ids.add(option1.isin)
        processed_option_ids.add(option2.isin)
    
    return results

def _process_single_leg_options(
    all_options_list: List[OptionPosition],
    processed_option_ids: set,
    equity_map: Dict[str, int]
) -> List[TaggedOptionPosition]:
    """
    Processes single-leg option positions, tagging them as Covered Call, Protective Put, or Naked.
    """
    results: List[TaggedOptionPosition] = []
    for pos in all_options_list: # Iterate through the original flat list of all options
        if pos.isin in processed_option_ids:
            continue # Skip options already processed in multi-leg strategies

        symbol = pos.symbol
        contracts = pos.contracts
        option_type = pos.option_type
        position_type = pos.position
        strike = pos.strike
        expiry = pos.expiry

        # Default tags for single-leg options that aren't part of multi-leg strategies
        tag: Literal["Naked", "Covered Call", "Protective Put", "Partially Covered Call", "Partially Protective Put", "Long Call", "Short Put"] = "Naked"
        coverage: float = 0.0

        option_exposure_shares = contracts * OPTION_MULTIPLIER
        equity_held_shares = equity_map.get(symbol, 0)

        # Logic for Covered Call and Protective Put
        if option_exposure_shares > 0: # Avoid division by zero
            if position_type == "Short" and option_type == "Call":
                coverage = min(100.0, round((equity_held_shares / option_exposure_shares) * 100, 2))
                if coverage == 100.0:
                    tag = "Covered Call"
                elif coverage > 0:
                    tag = "Partially Covered Call"
            elif position_type == "Long" and option_type == "Put":
                coverage = min(100.0, round((equity_held_shares / option_exposure_shares) * 100, 2))
                if coverage == 100.0:
                    tag = "Protective Put"
                elif coverage > 0:
                    tag = "Partially Protective Put"
            elif position_type == "Long" and option_type == "Call":
                tag = "Long Call" # Explicitly tag Long Calls not part of multi-leg
            elif position_type == "Short" and option_type == "Put":
                tag = "Short Put" # Explicitly tag Short Puts not part of multi-leg
            
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


def tag_option_strategies(portfolio: Portfolio) -> List[Union[TaggedOptionPosition, OptionStrategy]]: # Changed return type
    """
    Analyzes option positions within a portfolio to identify and tag common strategies
    like Covered Calls, Protective Puts, Straddles, Strangles, and Spreads.
    Returns a list of identified OptionStrategy objects for multi-leg strategies
    and TaggedOptionPosition objects for single-leg options.
    """
    equity_map = {
        p.symbol: p.quantity
        for p in portfolio.positions
        if isinstance(p, EquityPosition)
    }

    # Group options by symbol and then by expiry for easier identification of multi-leg strategies
    options_by_symbol_expiry: Dict[str, Dict[date, List[OptionPosition]]] = defaultdict(lambda: defaultdict(list))
    
    # Store all options in a flat list to keep track of already processed options
    all_options_list: List[OptionPosition] = []

    for pos in portfolio.positions:
        if isinstance(pos, OptionPosition):
            # Ensure expiry is a date object for consistent keying
            if isinstance(pos.expiry, str):
                pos.expiry = datetime.strptime(pos.expiry, "%Y-%m-%d").date()
            options_by_symbol_expiry[pos.symbol][pos.expiry].append(pos)
            all_options_list.append(pos)

    results: List[Union[TaggedOptionPosition, OptionStrategy]] = [] # Changed results list type
    
    # Keep track of options that have been tagged as part of a multi-leg strategy
    # to avoid double-tagging them as 'Naked' or other single-leg strategies.
    processed_option_ids = set()

    # --- Strategy Identification Logic ---
    # These functions now return OptionStrategy objects directly
    for symbol, expiries in options_by_symbol_expiry.items():
        for expiry, options_list_for_expiry in expiries.items():
            # Identify Straddles
            straddle_strategies = _identify_straddles(options_list_for_expiry, processed_option_ids)
            results.extend(straddle_strategies)

            # Identify Strangles (pass a fresh list of options for the current symbol/expiry that haven't been processed)
            strangle_strategies = _identify_strangles(options_list_for_expiry, processed_option_ids)
            results.extend(strangle_strategies)

            # Identify Spreads
            spread_strategies = _identify_vertical_spreads(options_list_for_expiry, processed_option_ids)
            results.extend(spread_strategies)
    
    # 4. Process remaining single-leg options (Covered Call, Protective Put, Naked, Long Call, Short Put)
    single_leg_results = _process_single_leg_options(all_options_list, processed_option_ids, equity_map)
    results.extend(single_leg_results)

    return results