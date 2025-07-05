from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from .currency import ISOCurrency


class FundPosition(BaseModel):
    type: Literal["Fund"] = Field(
        json_schema_extra={"description": "Instrument type discriminator; fixed value 'Fund'."}
    )
    fund_name: str = Field(
        json_schema_extra={
            "description": "Full name of the fund.",
            "example": "iShares MSCI World ETF"
        }
    )
    symbol: str = Field(
        json_schema_extra={
            "description": "Ticker symbol of the fund.",
            "example": "URTH"
        }
    )
    fund_type: Literal["Mutual Fund", "ETF", "Hedge Fund"] = Field(
        json_schema_extra={"description": "Category or type of the fund."}
    )
    quantity: float = Field(
        json_schema_extra={
            "description": "Number of units or shares held.",
            "example": 150.5
        },
        ge=0
    )
    nav_per_unit: float = Field(
        json_schema_extra={
            "description": "Net Asset Value per unit or share.",
            "example": 105.22
        },
        ge=0
    )
    average_cost_price: float = Field(
        json_schema_extra={
            "description": "Average acquisition cost per unit/share.",
            "example": 100.0
        },
        ge=0
    )
    market_value: float = Field(
        json_schema_extra={
            "description": "Current market value, calculated as quantity × current price.",
            "example": 15804.61
        },
        ge=0
    )
    isin: str = Field(
        json_schema_extra={
            "description": "International Securities Identification Number of the fund.",
            "example": "IE00B6R51Z18"
        }
    )
    instrument_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency in which the fund is denominated.",
            "example": "USD"
        }
    )

