from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from .currency import ISOCurrency

 
 
class FXForwardPosition(BaseModel):
    type: Literal["FXForward"] = Field(
        json_schema_extra={"description": "Discriminator to identify instrument type. Fixed value: 'FXForward'."}
    )

    base_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency being bought or sold (e.g., 'EUR').",
            "example": "EUR"
        }
    )

    quote_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency used to quote the base currency (e.g., 'USD').",
            "example": "USD"
        }
    )

    notional: float = Field(
        json_schema_extra={
            "description": "Amount of base currency in the contract.",
            "example": 1_000_000.0
        },
        ge=0
    )

    side: Literal["Buy", "Sell"] = Field(
        json_schema_extra={"description": "Direction of trade from client’s perspective: Buy (buy base currency) or Sell (sell base currency)."}
    )

    trade_date: str = Field(
        json_schema_extra={
            "description": "Date on which the forward contract was agreed (ISO format).",
            "example": "2025-07-01"
        }
    )

    settlement_date: str = Field(
        json_schema_extra={
            "description": "Date on which the contract will be settled. Typically > T+2.",
            "example": "2025-09-01"
        }
    )

    forward_rate: float = Field(
        json_schema_extra={
            "description": "Agreed exchange rate for the forward settlement.",
            "example": 1.1100
        },
        ge=0
    )

    market_value: float = Field(
        json_schema_extra={
            "description": "Mark-to-market (MTM) value of the forward in instrument currency.",
            "example": 5000.0
        }
    )

    valuation_date: str = Field(
        json_schema_extra={
            "description": "Date as of which the market value is calculated (ISO format).",
            "example": "2025-07-04"
        }
    )

    instrument_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency in which the contract is valued, typically same as quote currency.",
            "example": "USD"
        }
    )

