from pydantic import BaseModel, Field
from typing import List, Literal
from .currency import ISOCurrency
from .positions import Position
 

class Portfolio(BaseModel):
    portfolio_id: str = Field(
        ..., 
        json_schema_extra={
            "description": (
                "Unique identifier for the portfolio. "
                "Example: 'PORT123456' or a GUID like 'af6e2d34-9012-41cd-8b9e-ff1a1e587e21'"
            ),
            "example": "PORT123456"
        }
    )

    portfolio_currency: ISOCurrency = Field(
        ..., 
        json_schema_extra={
            "description": (
                "Base currency of the portfolio used for normalization and reporting. "
                "All position-level market values may be converted to this currency."
            ),
            "example": "USD"
        }
    )

    investment_horizon_years: int = Field(
        ..., 
        json_schema_extra={
            "description": (
                "Client's intended investment time horizon in years. "
                "Helps in determining suitable asset allocation and portfolio strategy."
            ),
            "example": 5
        },
        ge=0
    )

    risk_profile: Literal["Conservative", "Moderate", "Aggressive"] = Field(
        ..., 
        json_schema_extra={"description": "Investor's risk appetite classification. Used for suitability rules and portfolio optimization."}
    )

    product_knowledge: List[str] = Field(
        ..., 
        json_schema_extra={
            "description": (
                "List of financial instruments or asset types the client is familiar with. "
                "Used in suitability and regulatory checks."
            ),
            "example": ["Equity", "Bond", "FXForward", "TimeDeposit"]
        }
    )

    positions: List[Position] = Field(
        ..., 
        json_schema_extra={
            "description": (
                "All current holdings in the portfolio across supported asset classes. "
                "Each position is represented as a discriminated union (e.g., EquityPosition, BondPosition, etc.)."
            )
        }
    )