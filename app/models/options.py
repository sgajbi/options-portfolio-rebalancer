from pydantic import BaseModel, Field
from typing import Literal

class TaggedOptionPosition(BaseModel):
    """
    Represents an option position with its identified strategy tag and coverage.
    """
    symbol: str = Field(..., description="Underlying asset ticker symbol.")
    option_type: Literal["Call", "Put"] = Field(..., description="Type of the option: Call or Put.")
    position: Literal["Long", "Short"] = Field(..., description="Position type: Long (buyer) or Short (writer).")
    strike: float = Field(..., description="Strike price of the option.")
    expiry: str = Field(..., description="Expiration date of the option in ISO format (YYYY-MM-DD).")
    tag: Literal["Naked", "Covered Call", "Protective Put"] = Field(..., description="Identified option strategy tag.")
    coverage_percent: float = Field(..., ge=0.0, le=100.0, description="Percentage of the option's notional covered by underlying equity. 0 for naked, 100 for fully covered.")