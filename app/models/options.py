from pydantic import BaseModel, Field
from typing import Literal
from datetime import date 


class TaggedOptionPosition(BaseModel):
    """
    Represents an option position with its identified strategy tag and coverage.
    This model is now primarily for single-leg classifications.
    """
    symbol: str = Field(json_schema_extra={"description": "Underlying asset ticker symbol."})
    option_type: Literal["Call", "Put"] = Field(json_schema_extra={"description": "Type of the option: Call or Put."})
    position: Literal["Long", "Short"] = Field(json_schema_extra={"description": "Position type: Long (buyer) or Short (writer)."})
    strike: float = Field(json_schema_extra={"description": "Strike price of the option."})
    expiry: date = Field(json_schema_extra={"description": "Expiration date of the option in ISO format (YYYY-MM-DD)."})
    tag: Literal[
        "Naked", 
        "Covered Call", 
        "Protective Put",
        "Partially Covered Call",
        "Partially Protective Put", 
        "Long Call",
        "Short Put" 
    ] = Field(json_schema_extra={"description": "Identified option strategy tag for single legs."})
    coverage_percent: float = Field(ge=0.0, le=100.0, json_schema_extra={"description": "Percentage of the option's notional covered by underlying equity. 0 for naked, 100 for fully covered."})