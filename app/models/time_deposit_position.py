from pydantic import BaseModel, Field
from typing import Literal
from .currency import ISOCurrency

   

class TimeDepositPosition(BaseModel):
    type: Literal["TimeDeposit"] = Field(
        json_schema_extra={"description": "Discriminator for instrument type; fixed value 'TimeDeposit'."}
    )
    currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency of the time deposit.",
            "example": "USD"
        }
    )
    principal: float = Field(
        json_schema_extra={
            "description": "Initial amount deposited.",
            "example": 100000.0
        },
        ge=0
    )
    interest_rate: float = Field(
        json_schema_extra={
            "description": "Annual interest rate in percent.",
            "example": 3.5
        },
        ge=0
    )
    start_date: str = Field(
        json_schema_extra={
            "description": "Start date of the deposit (ISO 8601 format).",
            "example": "2025-01-01"
        }
    )
    maturity_date: str = Field(
        json_schema_extra={
            "description": "Date when the deposit matures (ISO 8601 format).",
            "example": "2026-01-01"
        }
    )
    interest_type: Literal["Simple", "Compound"] = Field(
        "Simple", 
        json_schema_extra={
            "description": "Interest calculation method.",
            "example": "Simple"
        }
    )
    compounding_frequency: Literal["Monthly", "Quarterly", "Annually", "None"] = Field(
        "None",
        json_schema_extra={
            "description": "Frequency of compounding interest, if applicable.",
            "example": "None"
        }
    )
    accrued_interest: float = Field(
        json_schema_extra={
            "description": "Interest accrued up to the valuation date.",
            "example": 1500.0
        },
        ge=0
    )
    market_value: float = Field(
        json_schema_extra={
            "description": "Total value of the deposit (principal + accrued interest).",
            "example": 101500.0
        },
        ge=0
    )
    valuation_date: str = Field(
        json_schema_extra={
            "description": "Date at which accrued interest and market value are calculated.",
            "example": "2025-07-04"
        }
    )
    instrument_currency: ISOCurrency = Field(
        json_schema_extra={
            "description": "Currency in which the instrument is valued (usually same as `currency`).",
            "example": "USD"
        }
    )

