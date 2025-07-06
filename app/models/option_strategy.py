from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union # <--- Add Union here
from datetime import date
from .option_position import OptionPosition

class OptionStrategy(BaseModel):
    """
    Represents an identified multi-leg option strategy.
    """
    strategy_id: str = Field(
        json_schema_extra={"description": "Unique identifier for the strategy instance."}
    )
    strategy_name: Literal[
        "Long Straddle",
        "Short Straddle",
        "Long Strangle",
        "Short Strangle",
        "Call Vertical Spread",
        "Put Vertical Spread",
        # Add other multi-leg strategies here if needed in the future
    ] = Field(json_schema_extra={"description": "Name of the identified option strategy."})
    underlying_symbol: str = Field(
        json_schema_extra={"description": "The common underlying asset ticker symbol for all legs."}
    )
    expiry_date: date = Field(
        json_schema_extra={"description": "The common expiration date for all legs of the strategy."}
    )
    legs: List[OptionPosition] = Field(
        json_schema_extra={"description": "List of individual option positions forming this strategy."}
    )
    net_premium_paid_received: float = Field(
        json_schema_extra={"description": "Net premium paid (positive) or received (negative) for the entire strategy."}
    )
    max_profit: Union[float, Literal["Unlimited"]] = Field( 
        ..., #
        json_schema_extra={"description": "Maximum potential profit for the strategy. Can be 'Unlimited'."}
    )
    max_loss: Union[float, Literal["Unlimited"]] = Field( 
        ..., 
        json_schema_extra={"description": "Maximum potential loss for the strategy. Can be 'Unlimited'."}
    )
    upper_breakeven_point: Optional[float] = Field(
        None, json_schema_extra={"description": "Upper breakeven point of the strategy, if applicable."}
    )
    lower_breakeven_point: Optional[float] = Field(
        None, json_schema_extra={"description": "Lower breakeven point of the strategy, if applicable."}
    )