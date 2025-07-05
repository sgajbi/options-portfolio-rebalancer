from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from .currency import ISOCurrency


class EquityPosition(BaseModel):
    """
    Represents an equity (stock) holding in a portfolio.
    """
    type: Literal["Equity"] = Field(json_schema_extra={"description": "Instrument type identifier (always 'Equity')."})
    
    symbol: str = Field(
        json_schema_extra={
            "description": "Ticker symbol of the equity instrument.",
            "example": "AAPL"
        }
    )
    
    quantity: int = Field(
        json_schema_extra={
            "description": "Number of shares currently held.",
            "example": 100
        },
        ge=0
    )
    
    cio_rating: Literal["Buy", "Hold", "Sell"] = Field(
        json_schema_extra={"description": "Chief Investment Office's investment recommendation for the equity."}
    )
    
    average_cost_price: float = Field(
        json_schema_extra={
            "description": "Average price per share at which the equity was purchased.",
            "example": 135.75
        },
        ge=0
    )
    
    instrument_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency in which the equity is denominated/traded.",
            "example": "USD"
        }
    )
    
    market_value: float = Field(
        json_schema_extra={
            "description": "Current market value of the position, calculated as quantity × current price.",
            "example": 14500.00
        },
        ge=0
    )
    
    isin: str = Field(
        json_schema_extra={
            "description": "International Securities Identification Number for the equity instrument.",
            "example": "US0378331005"
        }
    )