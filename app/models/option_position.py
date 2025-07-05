from pydantic import BaseModel, Field
from typing import Literal
from datetime import date
from .currency import ISOCurrency


class OptionPosition(BaseModel):
    """
    Represents an option contract position.
    """
    type: Literal["Option"] = Field(
        json_schema_extra={"description": "Discriminator for union types. Fixed value: 'Option'."}
    )

    symbol: str = Field(
        json_schema_extra={
            "description": "Underlying asset ticker symbol.",
            "example": "AAPL"
        }
    )

    option_type: Literal["Call", "Put"] = Field(
        json_schema_extra={"description": "Option type: Call (right to buy) or Put (right to sell)."}
    )

    strike: float = Field(
        json_schema_extra={
            "description": "Strike price at which the option can be exercised.",
            "example": 150.0
        },
        ge=0
    )

    expiry: date = Field( 
        json_schema_extra={
            "description": "Expiration date of the option (ISO 8601 format).",
            "example": "2025-12-19"
        }
    )

    position: Literal["Long", "Short"] = Field(
        json_schema_extra={"description": "Position type: Long (option buyer) or Short (option writer)."}
    )

    contracts: int = Field(
        json_schema_extra={
            "description": "Number of contracts held. Typically, 1 contract = 100 shares.",
            "example": 10
        },
        ge=0
    )

    price_at_purchase: float = Field(
        json_schema_extra={
            "description": "Premium paid or received per contract at the time of purchase.",
            "example": 2.50
        },
        ge=0
    )

    current_price: float = Field(
        json_schema_extra={
            "description": "Current market premium per contract.",
            "example": 3.20
        },
        ge=0
    )

    market_value: float = Field(
        json_schema_extra={
            "description": "Total market value = contracts × current_price × multiplier (usually 100).",
            "example": 3200.0
        },
        ge=0
    )

    isin: str = Field(
        json_schema_extra={
            "description": "International Securities Identification Number for listed options.",
            "example": "US0378331005"
        }
    )
    
    instrument_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency in which the option is denominated/traded.",
            "example": "USD"
        }
    )