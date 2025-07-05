from pydantic import BaseModel, Field
from typing import Literal
from datetime import date
from .currency import ISOCurrency


class FXSpotPosition(BaseModel):
    """
    Represents an FX Spot (Foreign Exchange Spot) trade position.
    """
    type: Literal["FXSpot"] = Field(
        json_schema_extra={"description": "Discriminator to identify instrument type. Fixed value: 'FXSpot'."}
    )

    base_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency being bought or sold (e.g., 'EUR').",
            "example": "EUR"
        }
    )

    quote_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency used to price the base currency (e.g., 'USD').",
            "example": "USD"
        }
    )

    notional: float = Field(
        json_schema_extra={
            "description": "Amount of base currency involved in the transaction.",
            "example": 1_000_000.0
        },
        ge=0
    )

    side: Literal["Buy", "Sell"] = Field(
        json_schema_extra={"description": "Direction of the trade from the client's perspective: Buy (buy base currency) or Sell (sell base currency)."}
    )

    trade_date: date = Field( 
        json_schema_extra={
            "description": "Date on which the FX trade was booked (ISO format).",
            "example": "2025-07-01"
        }
    )

    settlement_date: date = Field( 
        json_schema_extra={
            "description": "Date when the FX trade is settled, typically T+2.",
            "example": "2025-07-03"
        }
    )

    spot_rate: float = Field(
        json_schema_extra={
            "description": "Agreed exchange rate for the spot trade.",
            "example": 1.1050
        },
        ge=0
    )

    market_value: float = Field(
        json_schema_extra={
            "description": "Market value in quote currency: notional × spot_rate.",
            "example": 1_105_000.0
        },
        ge=0
    )

    valuation_date: date = Field( 
        json_schema_extra={
            "description": "Date as of which the market value is calculated (ISO format).",
            "example": "2025-07-01"
        }
    )