from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from .currency import ISOCurrency

  
class FXSwapPosition(BaseModel):
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
    trade_date: str = Field(
        json_schema_extra={
            "description": "Date trade was executed (ISO format).",
            "example": "2025-07-01"
        }
    )
    near_leg_settlement_date: str = Field(
        json_schema_extra={
            "description": "Settlement date for the near leg (spot leg).",
            "example": "2025-07-03"
        }
    )
    far_leg_settlement_date: str = Field(
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
    valuation_date: str = Field(
        json_schema_extra={
            "description": "Date when MTM valuation is performed (ISO format).",
            "example": "2025-07-04"
        }
    )
    instrument_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency in which market_value is expressed, usually quote currency.",
            "example": "USD"
        }
    )
