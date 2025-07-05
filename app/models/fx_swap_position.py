from pydantic import BaseModel, Field
from typing import Literal
from datetime import date 
from .currency import ISOCurrency


class FXSwapPosition(BaseModel):
    """
    Represents a Foreign Exchange (FX) Swap contract position.
    """
    type: Literal["FXSwap"] = Field(
        json_schema_extra={"description": "Instrument type discriminator, fixed as 'FXSwap'."}
    )
    base_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency being bought/sold in the near leg.",
            "example": "EUR"
        }
    )
    quote_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency used to price the base currency.",
            "example": "USD"
        }
    )
    notional: float = Field(
        json_schema_extra={
            "description": "Amount of base currency in the swap.",
            "example": 1_000_000.0
        },
        ge=0
    )
    side: Literal["Buy", "Sell"] = Field(
        json_schema_extra={
            "description": "Trade direction from the client’s perspective.",
            "example": "Buy"
        }
    )
    trade_date: date = Field( 
        json_schema_extra={
            "description": "Date trade was executed (ISO format).",
            "example": "2025-07-01"
        }
    )
    near_leg_settlement_date: date = Field( 
        json_schema_extra={
            "description": "Settlement date for the near leg (spot leg).",
            "example": "2025-07-03"
        }
    )
    far_leg_settlement_date: date = Field( 
        json_schema_extra={
            "description": "Settlement date for the far leg (forward leg).",
            "example": "2025-08-01"
        }
    )
    near_leg_rate: float = Field(
        json_schema_extra={
            "description": "FX rate agreed for near leg settlement.",
            "example": 1.1050
        },
        ge=0
    )
    far_leg_rate: float = Field(
        json_schema_extra={
            "description": "FX rate agreed for far leg settlement.",
            "example": 1.1100
        },
        ge=0
    )
    market_value: float = Field(
        json_schema_extra={
            "description": "Combined mark-to-market value of both legs in instrument currency.",
            "example": 10_000.0
        }
    )
    valuation_date: date = Field( 
        json_schema_extra={
            "description": "Date as of which the market value is calculated.",
            "example": "2025-07-01"
        }
    )