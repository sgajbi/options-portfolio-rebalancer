from typing import List, Dict, Tuple
from collections import defaultdict
from ..models.portfolio import Portfolio
from ..models.equity_position import EquityPosition
from ..models.options import TaggedOptionPosition
from ..models.option_position import OptionPosition
from datetime import date # Add this import for type hinting and clarity

OPTION_MULTIPLIER = 100

def _identify_straddles(
    options_list: List[OptionPosition],
    processed_option_ids: set
) -> List[TaggedOptionPosition]:
    """
    Identifies Straddle strategies within a list of options.
    A straddle involves buying/selling both a call and a put with the same strike and expiry on the same underlying.
    """
    results: List[TaggedOptionPosition] = []

    calls = [op for op in options_list if op.option_type == "Call" and op.isin not in processed_option_ids]
    puts = [op for op in options_list if op.option_type == "Put" and op.isin not in processed_option_ids]

    calls.sort(key=lambda x: x.strike)
    puts.sort(key=lambda x: x.strike)

    matched_straddles = []
    for call in calls:
        for put in puts:
            # Added expiry and symbol check for robust identification
            if (call.strike == put.strike and
                call.position == put.position and
                call.expiry == put.expiry and
                call.symbol == put.symbol): 
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

    return results

def _identify_strangles(
    options_list: List[OptionPosition],
    processed_option_ids: set
) -> List[TaggedOptionPosition]:
    """
    Identifies Strangle strategies within a list of options.
    A strangle involves buying/selling both a call and a put with different strikes
    but same expiry on the same underlying, where the call strike is higher than the put strike.
    """
    results: List[TaggedOptionPosition] = []

    calls = [op for op in options_list if op.option_type == "Call" and op.isin not in processed_option_ids]
    puts = [op for op in options_list if op.option_type == "Put" and op.isin not in processed_option_ids]

    calls.sort(key=lambda x: x.strike)
    puts.sort(key=lambda x: x.strike)

    matched_strangles = []
    for call in calls:
        for put in puts:
            # Check for different strikes, same position (both long or both short),
            # and call strike > put strike, same expiry, same symbol
            if (call.strike > put.strike and
                call.position == put.position and
                call.expiry == put.expiry and # Added expiry check
                call.symbol == put.symbol and # Added symbol check
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

    return results

def _identify_vertical_spreads(
    options_list: List[OptionPosition],
    processed_option_ids: set
) -> List[TaggedOptionPosition]:
    """
    Identifies Vertical Spread strategies within a list of options.
    Looks for two options of the same type and same expiry, but different strikes and opposite positions.
    """
    results: List[TaggedOptionPosition] = []

    remaining_options_for_spread = [op for op in options_list if op.isin not in processed_option_ids]
    remaining_options_for_spread.sort(key=lambda x: x.strike)

    matched_spreads = []
    for i in range(len(remaining_options_for_spread)):
        for j in range(i + 1, len(remaining_options_for_spread)):
            option1 = remaining_options_for_spread[i]
            option2 = remaining_options_for_spread[j]

            # Ensure they are on the same underlying symbol and have the same expiry
            if (option1.symbol == option2.symbol and
                option1.expiry == option2.expiry and # Added expiry check
                option1.option_type == option2.option_type and
                option1.strike != option2.strike): # Strikes must be different for a spread

                if (option1.position == "Long" and option2.position == "Short") or \
                   (option1.position == "Short" and option2.position == "Long"):

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

        option_exposure_shares = contracts * OPTION_MULTIPLIER
        equity_held_shares = equity_map.get(symbol, 0)

        tag: str = "Naked" # Default to Naked
        coverage: float = 0.0

        if option_exposure_shares > 0: # Avoid division by zero
            if position_type == "Short" and option_type == "Call":
                # A short call needs to be covered by equity
                coverage = min(100.0, round((equity_held_shares / option_exposure_shares) * 100, 2))
                if coverage >= 100.0: # Only fully covered calls are "Covered Call"
                    tag = "Covered Call"
                else: # Partially covered or not covered
                    tag = "Naked" if coverage == 0.0 else "Partially Covered Call" # Introduce "Partially Covered Call"
            elif position_type == "Long" and option_type == "Put":
                # A long put protects an equity holding
                coverage = min(100.0, round((equity_held_shares / option_exposure_shares) * 100, 2))
                if coverage >= 100.0: # Only fully covered puts are "Protective Put"
                    tag = "Protective Put"
                else: # Partially covered or not covered
                    tag = "Naked" if coverage == 0.0 else "Partially Protective Put" # Introduce "Partially Protective Put"
            # For other cases (Long Call, Short Put), they are generally naked unless part of a spread/multi-leg.
            # The default "Naked" tag will apply if no specific strategy is identified by multi-leg.
            elif position_type == "Long" and option_type == "Call": # Explicitly tag long calls not part of spreads as naked
                tag = "Naked" 
            elif position_type == "Short" and option_type == "Put": # Explicitly tag short puts not part of spreads as naked
                tag = "Naked" 
        else: # If contracts is 0, it's not a valid option position for exposure calculations
            tag = "Invalid Option Position" # Or handle as an error/skip

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
    # Changed type hint for inner dictionary key from str to date
    options_by_symbol_expiry: Dict[str, Dict[date, List[OptionPosition]]] = defaultdict(lambda: defaultdict(list)) 

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
    # Process multi-leg strategies first as they take precedence

    # Iterate through a copy of keys to allow modification of options_by_symbol_expiry if needed,
    # though processed_option_ids is the primary mechanism for avoiding re-processing.

    # 1. Identify Straddles (Long or Short)
    for symbol, expiries in options_by_symbol_expiry.items():
        # Iterate over items to get both expiry date and list of options
        for expiry_date, options_list_for_expiry in expiries.items(): # Changed expiry to expiry_date for clarity
            straddle_results = _identify_straddles(options_list_for_expiry, processed_option_ids)
            results.extend(straddle_results)

    # 2. Identify Strangles (Long or Short)
    for symbol, expiries in options_by_symbol_expiry.items():
        for expiry_date, options_list_for_expiry in expiries.items(): # Changed expiry to expiry_date for clarity
            strangle_results = _identify_strangles(options_list_for_expiry, processed_option_ids)
            results.extend(strangle_results)

    # 3. Identify Spreads (Vertical)
    for symbol, expiries in options_by_symbol_expiry.items():
        for expiry_date, options_list_for_expiry in expiries.items(): # Changed expiry to expiry_date for clarity
            spread_results = _identify_vertical_spreads(options_list_for_expiry, processed_option_ids)
            results.extend(spread_results)

    # 4. Process remaining single-leg options (Covered Call, Protective Put, Naked)
    # This must be done *after* all multi-leg strategies have been identified
    # because options part of multi-leg strategies should not be tagged as single-leg.
    single_leg_results = _process_single_leg_options(all_options_list, processed_option_ids, equity_map)
    results.extend(single_leg_results)

    return results