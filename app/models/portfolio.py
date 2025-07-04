from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from typing_extensions import Annotated as TAnnotated
from pydantic import TypeAdapter



class EquityPosition(BaseModel):
    type: Literal["Equity"] = Field(..., description="Instrument type identifier (always 'Equity').")
    
    symbol: str = Field(
        ..., 
        description="Ticker symbol of the equity instrument.",
        example="AAPL"
    )
    
    quantity: int = Field(
        ..., 
        description="Number of shares currently held.",
        example=100
    )
    
    cio_rating: Literal["Buy", "Hold", "Sell"] = Field(
        ..., 
        description="Chief Investment Office's investment recommendation for the equity."
    )
    
    average_cost_price: float = Field(
        ..., 
        description="Average price per share at which the equity was purchased.",
        example=135.75,
        ge=0
    )
    
    instrument_currency: str = Field(
        ..., 
        description="Currency in which the equity is denominated/traded.",
        example="USD"
    )
    
    market_value: float = Field(
        ..., 
        description="Current market value of the position, calculated as quantity × current price.",
        example=14500.00,
        ge=0
    )
    
    isin: str = Field(
        ..., 
        description="International Securities Identification Number for the equity instrument.",
        example="US0378331005"
    )

class BondPosition(BaseModel):
    type: Literal["Bond"] = Field(
        ..., 
        description="Instrument type identifier (always 'Bond')."
    )

    symbol: str = Field(
        ..., 
        description="Bond identifier such as Bloomberg ticker or internal short code.",
        example="US10Y"
    )

    issuer: str = Field(
        ..., 
        description="Name of the issuing entity or government.",
        example="US Treasury"
    )

    face_value: float = Field(
        ..., 
        description="Face (par) value per bond unit.",
        example=1000.0,
        ge=0
    )

    coupon_rate: float = Field(
        ..., 
        description="Annual coupon rate in percentage.",
        example=2.5,
        ge=0
    )

    maturity_date: str = Field(
        ..., 
        description="Date when the bond matures and principal is repaid (ISO format).",
        example="2030-12-31"
    )

    quantity: int = Field(
        ..., 
        description="Number of bond units held.",
        example=10,
        ge=0
    )

    average_cost_price: float = Field(
        ..., 
        description="Average clean price paid for the bond, excluding accrued interest.",
        example=98.5,
        ge=0
    )

    instrument_currency: str = Field(
        ..., 
        description="Currency in which the bond is denominated.",
        example="USD"
    )

    market_value: float = Field(
        ..., 
        description="Current market value of the bond position, including accrued interest.",
        example=10234.5,
        ge=0
    )

    isin: str = Field(
        ..., 
        description="International Securities Identification Number of the bond.",
        example="US9128285M81"
    )

    coupon_frequency: Literal["Annual", "Semi-Annual", "Quarterly", "Monthly"] = Field(
        ..., 
        description="Frequency of coupon payments."
    )

    day_count_convention: Literal["30/360", "Actual/360", "Actual/365", "Actual/Actual"] = Field(
        ..., 
        description="Day count convention used to calculate accrued interest and coupon amounts."
    )

class OptionPosition(BaseModel):
    type: Literal["Option"] = Field(
        ..., 
        description="Discriminator for union types. Fixed value: 'Option'."
    )

    symbol: str = Field(
        ..., 
        description="Underlying asset ticker symbol.",
        example="AAPL"
    )

    option_type: Literal["Call", "Put"] = Field(
        ..., 
        description="Option type: Call (right to buy) or Put (right to sell)."
    )

    strike: float = Field(
        ..., 
        description="Strike price at which the option can be exercised.",
        example=150.0,
        ge=0
    )

    expiry: str = Field(
        ..., 
        description="Expiration date of the option (ISO 8601 format).",
        example="2025-12-19"
    )

    position: Literal["Long", "Short"] = Field(
        ..., 
        description="Position type: Long (option buyer) or Short (option writer)."
    )

    contracts: int = Field(
        ..., 
        description="Number of contracts held. Typically, 1 contract = 100 shares.",
        example=10,
        ge=0
    )

    price_at_purchase: float = Field(
        ..., 
        description="Premium paid or received per contract at the time of purchase.",
        example=2.50,
        ge=0
    )

    current_price: float = Field(
        ..., 
        description="Current market premium per contract.",
        example=3.20,
        ge=0
    )

    market_value: float = Field(
        ..., 
        description="Total market value = contracts × current_price × multiplier (usually 100).",
        example=3200.0,
        ge=0
    )

    isin: str = Field(
        ..., 
        description="International Securities Identification Number for listed options.",
        example="US0378331005"
    )

    instrument_currency: str = Field(
        ..., 
        description="Currency in which the option is denominated.",
        example="USD"
    )

class FXSpotPosition(BaseModel):
    type: Literal["FXSpot"] = Field(
        ..., 
        description="Discriminator to identify instrument type. Fixed value: 'FXSpot'."
    )

    base_currency: str = Field(
        ..., 
        description="Currency being bought or sold (e.g., 'EUR').",
        example="EUR"
    )

    quote_currency: str = Field(
        ..., 
        description="Currency used to price the base currency (e.g., 'USD').",
        example="USD"
    )

    notional: float = Field(
        ..., 
        description="Amount of base currency involved in the transaction.",
        example=1_000_000.0,
        ge=0
    )

    side: Literal["Buy", "Sell"] = Field(
        ..., 
        description="Direction of the trade from the client's perspective: Buy (buy base currency) or Sell (sell base currency)."
    )

    trade_date: str = Field(
        ..., 
        description="Date on which the FX trade was booked (ISO format).",
        example="2025-07-01"
    )

    settlement_date: str = Field(
        ..., 
        description="Date when the FX trade is settled, typically T+2.",
        example="2025-07-03"
    )

    spot_rate: float = Field(
        ..., 
        description="Agreed exchange rate for the spot trade.",
        example=1.1050,
        ge=0
    )

    market_value: float = Field(
        ..., 
        description="Market value in quote currency: notional × spot_rate.",
        example=1_105_000.0,
        ge=0
    )

    valuation_date: str = Field(
        ..., 
        description="Date as of which the market value is calculated.",
        example="2025-07-04"
    )

    instrument_currency: str = Field(
        ..., 
        description="Currency in which the instrument is valued (typically same as quote currency).",
        example="USD"
    )


class FXForwardPosition(BaseModel):
    type: Literal["FXForward"] = Field(
        ..., 
        description="Discriminator to identify instrument type. Fixed value: 'FXForward'."
    )

    base_currency: str = Field(
        ..., 
        description="Currency being bought or sold (e.g., 'EUR').",
        example="EUR"
    )

    quote_currency: str = Field(
        ..., 
        description="Currency used to quote the base currency (e.g., 'USD').",
        example="USD"
    )

    notional: float = Field(
        ..., 
        description="Amount of base currency in the contract.",
        example=1_000_000.0,
        ge=0
    )

    side: Literal["Buy", "Sell"] = Field(
        ..., 
        description="Direction of trade from client’s perspective: Buy (buy base currency) or Sell (sell base currency)."
    )

    trade_date: str = Field(
        ..., 
        description="Date on which the forward contract was agreed (ISO format).",
        example="2025-07-01"
    )

    settlement_date: str = Field(
        ..., 
        description="Date on which the contract will be settled. Typically > T+2.",
        example="2025-09-01"
    )

    forward_rate: float = Field(
        ..., 
        description="Agreed exchange rate for the forward settlement.",
        example=1.1100,
        ge=0
    )

    market_value: float = Field(
        ..., 
        description="Mark-to-market (MTM) value of the forward in instrument currency.",
        example=5000.0
    )

    valuation_date: str = Field(
        ..., 
        description="Date as of which the market value is calculated (ISO format).",
        example="2025-07-04"
    )

    instrument_currency: str = Field(
        ..., 
        description="Currency in which the contract is valued, typically same as quote currency.",
        example="USD"
    )



class FXSwapPosition(BaseModel):
    type: Literal["FXSwap"] = Field(
        ..., description="Instrument type discriminator, fixed as 'FXSwap'."
    )
    base_currency: str = Field(
        ..., description="Currency being bought/sold in the near leg.",
        example="EUR"
    )
    quote_currency: str = Field(
        ..., description="Currency used to price the base currency.",
        example="USD"
    )
    notional: float = Field(
        ..., description="Amount of base currency in the swap.",
        example=1_000_000.0,
        ge=0
    )
    side: Literal["Buy", "Sell"] = Field(
        ..., description="Trade direction from the client’s perspective.",
        example="Buy"
    )
    trade_date: str = Field(
        ..., description="Date trade was executed (ISO format).",
        example="2025-07-01"
    )
    near_leg_settlement_date: str = Field(
        ..., description="Settlement date for the near leg (spot leg).",
        example="2025-07-03"
    )
    far_leg_settlement_date: str = Field(
        ..., description="Settlement date for the far leg (forward leg).",
        example="2025-08-01"
    )
    near_leg_rate: float = Field(
        ..., description="FX rate agreed for near leg settlement.",
        example=1.1050,
        ge=0
    )
    far_leg_rate: float = Field(
        ..., description="FX rate agreed for far leg settlement.",
        example=1.1100,
        ge=0
    )
    market_value: float = Field(
        ..., description="Combined mark-to-market value of both legs in instrument currency.",
        example=10_000.0
    )
    valuation_date: str = Field(
        ..., description="Date when MTM valuation is performed (ISO format).",
        example="2025-07-04"
    )
    instrument_currency: str = Field(
        ..., description="Currency in which market_value is expressed, usually quote currency.",
        example="USD"
    )




class TimeDepositPosition(BaseModel):
    type: Literal["TimeDeposit"] = Field(
        ..., 
        description="Discriminator for instrument type; fixed value 'TimeDeposit'."
    )
    currency: str = Field(
        ..., 
        description="Currency of the time deposit.",
        example="USD"
    )
    principal: float = Field(
        ..., 
        description="Initial amount deposited.",
        example=100000.0,
        ge=0
    )
    interest_rate: float = Field(
        ..., 
        description="Annual interest rate in percent.",
        example=3.5,
        ge=0
    )
    start_date: str = Field(
        ..., 
        description="Start date of the deposit (ISO 8601 format).",
        example="2025-01-01"
    )
    maturity_date: str = Field(
        ..., 
        description="Date when the deposit matures (ISO 8601 format).",
        example="2026-01-01"
    )
    interest_type: Literal["Simple", "Compound"] = Field(
        "Simple",
        description="Interest calculation method.",
        example="Simple"
    )
    compounding_frequency: Literal["Monthly", "Quarterly", "Annually", "None"] = Field(
        "None",
        description="Frequency of compounding interest, if applicable.",
        example="None"
    )
    accrued_interest: float = Field(
        ..., 
        description="Interest accrued up to the valuation date.",
        example=1500.0,
        ge=0
    )
    market_value: float = Field(
        ..., 
        description="Total value of the deposit (principal + accrued interest).",
        example=101500.0,
        ge=0
    )
    valuation_date: str = Field(
        ..., 
        description="Date at which accrued interest and market value are calculated.",
        example="2025-07-04"
    )
    instrument_currency: str = Field(
        ..., 
        description="Currency in which the instrument is valued (usually same as `currency`).",
        example="USD"
    )



class FundPosition(BaseModel):
    type: Literal["Fund"] = Field(
        ..., 
        description="Instrument type discriminator; fixed value 'Fund'."
    )
    fund_name: str = Field(
        ..., 
        description="Full name of the fund.",
        example="iShares MSCI World ETF"
    )
    symbol: str = Field(
        ..., 
        description="Ticker symbol of the fund.",
        example="URTH"
    )
    fund_type: Literal["Mutual Fund", "ETF", "Hedge Fund"] = Field(
        ..., 
        description="Category or type of the fund."
    )
    quantity: float = Field(
        ..., 
        description="Number of units or shares held.",
        example=150.5,
        ge=0
    )
    nav_per_unit: float = Field(
        ..., 
        description="Net Asset Value per unit or share.",
        example=105.22,
        ge=0
    )
    average_cost_price: float = Field(
        ..., 
        description="Average acquisition cost per unit/share.",
        example=100.0,
        ge=0
    )
    market_value: float = Field(
        ..., 
        description="Current market value, calculated as quantity × current price.",
        example=15804.61,
        ge=0
    )
    isin: str = Field(
        ..., 
        description="International Securities Identification Number of the fund.",
        example="IE00B6R51Z18"
    )
    instrument_currency: str = Field(
        ..., 
        description="Currency in which the fund is denominated.",
        example="USD"
    )


Position = Annotated[
    Union[
        EquityPosition,
        OptionPosition,
        BondPosition,
        FXSpotPosition,
        FXForwardPosition,
        FXSwapPosition,
        TimeDepositPosition,
        FundPosition
    ],
    Field(discriminator='type')
]


class Portfolio(BaseModel):
    portfolio_id: str = Field(
        ..., 
        description=(
            "Unique identifier for the portfolio. "
            "Example: 'PORT123456' or a GUID like 'af6e2d34-9012-41cd-8b9e-ff1a1e587e21'"
        ),
        example="PORT123456"
    )

    portfolio_currency: str = Field(
        ..., 
        description=(
            "Base currency of the portfolio used for normalization and reporting. "
            "All position-level market values may be converted to this currency."
        ),
        example="USD"
    )

    investment_horizon_years: int = Field(
        ..., 
        description=(
            "Client's intended investment time horizon in years. "
            "Helps in determining suitable asset allocation and portfolio strategy."
        ),
        example=5,
        ge=0
    )

    risk_profile: Literal["Conservative", "Moderate", "Aggressive"] = Field(
        ..., 
        description="Investor's risk appetite classification. Used for suitability rules and portfolio optimization."
    )

    product_knowledge: List[str] = Field(
        ..., 
        description=(
            "List of financial instruments or asset types the client is familiar with. "
            "Used in suitability and regulatory checks."
        ),
        example=["Equity", "Bond", "FXForward", "TimeDeposit"]
    )

    positions: List[Position] = Field(
        ..., 
        description=(
            "All current holdings in the portfolio across supported asset classes. "
            "Each position is represented as a discriminated union (e.g., EquityPosition, BondPosition, etc.)."
        )
    )