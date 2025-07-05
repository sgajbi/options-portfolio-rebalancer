from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from .currency import ISOCurrency


class BondPosition(BaseModel):
    type: Literal["Bond"] = Field(
        json_schema_extra={"description": "Instrument type identifier (always 'Bond')."}
    )

    symbol: str = Field(
        json_schema_extra={
            "description": "Bond identifier such as Bloomberg ticker or internal short code.",
            "example": "US10Y"
        }
    )

    issuer: str = Field(
        json_schema_extra={
            "description": "Name of the issuing entity or government.",
            "example": "US Treasury"
        }
    )

    face_value: float = Field(
        json_schema_extra={
            "description": "Face (par) value per bond unit.",
            "example": 1000.0
        },
        ge=0
    )

    coupon_rate: float = Field(
        json_schema_extra={
            "description": "Annual coupon rate in percentage.",
            "example": 2.5
        },
        ge=0
    )

    maturity_date: str = Field(
        json_schema_extra={
            "description": "Date when the bond matures and principal is repaid (ISO format).",
            "example": "2030-12-31"
        }
    )

    quantity: int = Field(
        json_schema_extra={
            "description": "Number of bond units held.",
            "example": 10
        },
        ge=0
    )

    average_cost_price: float = Field(
        json_schema_extra={
            "description": "Average clean price paid for the bond, excluding accrued interest.",
            "example": 98.5
        },
        ge=0
    )

    instrument_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency in which the bond is denominated.",
            "example": "USD"
        }
    )

    market_value: float = Field(
        json_schema_extra={
            "description": "Current market value of the bond position, including accrued interest.",
            "example": 10234.5
        },
        ge=0
    )

    isin: str = Field(
        json_schema_extra={
            "description": "International Securities Identification Number of the bond.",
            "example": "US9128285M81"
        }
    )

    coupon_frequency: Literal["Annual", "Semi-Annual", "Quarterly", "Monthly"] = Field(
        json_schema_extra={"description": "Frequency of coupon payments."}
    )

    day_count_convention: Literal["30/360", "Actual/360", "Actual/365", "Actual/Actual"] = Field(
        json_schema_extra={"description": "Day count convention used to calculate accrued interest and coupon amounts."}
    )