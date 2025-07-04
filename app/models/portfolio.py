from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from typing_extensions import Annotated as TAnnotated
from pydantic import TypeAdapter


# -------------------------
# Equity Instrument
# -------------------------
class EquityPosition(BaseModel):
    type: Literal["Equity"]
    symbol: str                                    # Ticker symbol (e.g., "AAPL")
    quantity: int                                  # Number of shares held
    cio_rating: Literal["Buy", "Hold", "Sell"]     # CIO (Chief Investment Office) rating/view
    average_cost_price: float                      # Average acquisition cost per share
    instrument_currency: str                       # Currency the stock is traded in (e.g., "USD")
    market_value: float                            # Market value = quantity × current price
    isin: str                                      # International Securities Identification Number (e.g., "US0378331005")


# -------------------------
# Bond Instrument
# -------------------------
class BondPosition(BaseModel):
    type: Literal["Bond"]
    symbol: str                                     # Bond identifier (e.g., "US10Y" or Bloomberg Ticker)
    issuer: str                                     # Issuing entity (e.g., "US Treasury")
    face_value: float                               # Nominal/par value per unit (e.g., 1000)
    coupon_rate: float                              # Annual coupon % (e.g., 2.5)
    maturity_date: str                              # ISO format maturity date (e.g., "2030-12-31")
    quantity: int                                   # Number of bonds held
    average_cost_price: float                       # Avg clean price paid (excludes accrued interest)
    instrument_currency: str                        # Denomination currency (e.g., "USD")
    market_value: float                             # Current market value of the bond position
    isin: str                                       # Unique identifier for the bond (e.g., "US9128285M81")
    coupon_frequency: Literal["Annual", "Semi-Annual", "Quarterly", "Monthly"]  # Coupon payment frequency
    day_count_convention: Literal[
        "30/360", "Actual/360", "Actual/365", "Actual/Actual"
    ]                                               # Day count convention used for coupon calculation


# -------------------------
# Option Instrument
# -------------------------
class OptionPosition(BaseModel):
    type: Literal["Option"]                       # Discriminator for union types, fixed as "Option"
    symbol: str                                  # Underlying asset symbol, e.g., "AAPL"
    option_type: Literal["Call", "Put"]          # Option type: Call (right to buy) or Put (right to sell)
    strike: float                                # Strike price at which the option can be exercised, e.g., 150.0
    expiry: str                                  # Expiration date of the option in ISO format, e.g., "2025-12-19"
    position: Literal["Long", "Short"]           # Option position: Long (buyer) or Short (writer)
    contracts: int                               # Number of contracts held, where 1 contract typically equals 100 shares
    price_at_purchase: float                      # Option premium paid or received per contract at purchase, e.g., 2.50
    current_price: float                          # Current option premium per contract, e.g., 3.20
    market_value: float                           # Total market value = contracts × current_price × contract multiplier (usually 100)
    isin: str                                    # International Securities Identification Number for listed options, e.g., "US0378331005"
    instrument_currency: str                      # Currency in which option is denominated, e.g., "USD"



# -------------------------
# FX Spot
# -------------------------
class FXSpotPosition(BaseModel):
    type: Literal["FXSpot"]                        # Discriminator, fixed value "FXSpot"
    base_currency: str                             # Currency being bought or sold, e.g., "EUR"
    quote_currency: str                            # Currency used to price base currency, e.g., "USD"
    notional: float                                # Amount of base currency being exchanged, e.g., 1_000_000.0
    side: Literal["Buy", "Sell"]                   # Direction of the trade from the client's perspective ("Buy" base or "Sell" base)
    trade_date: str                                # Trade booking date in ISO format, e.g., "2025-07-01"
    settlement_date: str                           # Date FX settlement occurs (usually T+2), e.g., "2025-07-03"
    spot_rate: float                               # Agreed FX rate for the spot transaction, e.g., 1.1050
    market_value: float                            # Value of the notional in quote currency (notional × spot_rate), e.g., 1_105_000.0
    valuation_date: str                            # Date as of which market_value is calculated, e.g., "2025-07-04"
    instrument_currency: str                       # Currency in which the instrument is valued, typically same as quote_currency, e.g., "USD"



# -------------------------
# FX Forward
# -------------------------
class FXForwardPosition(BaseModel):
    type: Literal["FXForward"]                     # Discriminator, fixed as "FXForward"
    base_currency: str                             # Currency being bought or sold, e.g., "EUR"
    quote_currency: str                            # Currency used to price the base currency, e.g., "USD"
    notional: float                                # Amount of base currency in the contract, e.g., 1_000_000.0
    side: Literal["Buy", "Sell"]                   # Direction of trade from client perspective ("Buy" base or "Sell" base)
    trade_date: str                                # Trade booking date (ISO format), e.g., "2025-07-01"
    settlement_date: str                           # Forward settlement date (usually > T+2), e.g., "2025-09-01"
    forward_rate: float                            # Agreed FX rate for the forward settlement, e.g., 1.1100
    market_value: float                            # Mark-to-market value of the forward contract in instrument_currency, e.g., 5_000.0
    valuation_date: str                            # Date when market_value is calculated, e.g., "2025-07-04"
    instrument_currency: str                       # Currency for valuation, usually same as quote_currency, e.g., "USD"



# -------------------------
# FX Swap
# -------------------------
class FXSwapPosition(BaseModel):
    type: Literal["FXSwap"]                         # Discriminator, fixed as "FXSwap"
    base_currency: str                              # Currency being bought/sold in the near leg, e.g., "EUR"
    quote_currency: str                             # Currency used to price the base currency, e.g., "USD"
    notional: float                                 # Amount of base currency in the swap, e.g., 1_000_000.0
    side: Literal["Buy", "Sell"]                    # Direction of the trade from client's perspective, e.g., "Buy"
    trade_date: str                                 # Date trade was executed (ISO format), e.g., "2025-07-01"
    near_leg_settlement_date: str                   # Settlement date for near leg (spot leg), e.g., "2025-07-03"
    far_leg_settlement_date: str                    # Settlement date for far leg (forward leg), e.g., "2025-08-01"
    near_leg_rate: float                            # FX rate agreed for near leg settlement, e.g., 1.1050
    far_leg_rate: float                             # FX rate agreed for far leg settlement, e.g., 1.1100
    market_value: float                             # Combined mark-to-market value of both legs in instrument_currency, e.g., 10_000.0
    valuation_date: str                             # Date MTM valuation is done, e.g., "2025-07-04"
    instrument_currency: str                        # Currency in which market_value is expressed, usually quote_currency, e.g., "USD"



# -------------------------
# Time Deposit
# -------------------------
class TimeDepositPosition(BaseModel):
    type: Literal["TimeDeposit"]                        # Discriminator, fixed as "TimeDeposit"
    currency: str                                       # Currency of the deposit, e.g., "USD"
    principal: float                                   # Initial amount deposited, e.g., 100000.0
    interest_rate: float                               # Annual interest rate (in percent), e.g., 3.5
    start_date: str                                    # Start date of the deposit (ISO format), e.g., "2025-01-01"
    maturity_date: str                                 # Date when deposit matures, e.g., "2026-01-01"
    interest_type: Literal["Simple", "Compound"] = "Simple"   # Interest calculation method, default "Simple"
    compounding_frequency: Literal["Monthly", "Quarterly", "Annually", "None"] = "None"  # Frequency of compounding if compound interest
    accrued_interest: float                            # Interest accrued up to valuation date, e.g., 1500.0
    market_value: float                                # Total value = principal + accrued interest, e.g., 101500.0
    valuation_date: str                                # Date at which market_value and accrued_interest are calculated, e.g., "2025-07-04"
    instrument_currency: str                           # Currency in which instrument is valued, usually same as `currency`, e.g., "USD"



# -------------------------
# Fund (Mutual/ETF/Hedge)
# -------------------------
class FundPosition(BaseModel):
    type: Literal["Fund"]                           # Discriminator for union, fixed as "Fund"
    fund_name: str                                  # Full name of the fund, e.g., "iShares MSCI World ETF"
    symbol: str                                    # Ticker symbol of the fund, e.g., "URTH"
    fund_type: Literal["Mutual Fund", "ETF", "Hedge Fund"]  # Fund category/type
    quantity: float                                # Number of units/shares held, e.g., 150.5
    nav_per_unit: float                            # Net Asset Value per unit/share, e.g., 105.22
    average_cost_price: float                      # Average acquisition cost per unit
    market_value: float                            # Calculated as quantity × current_price, e.g., 15,804.61
    isin: str                                     # International Securities Identification Number, e.g., "IE00B6R51Z18"
    instrument_currency: str                       # Currency in which the fund is denominated, e.g., "USD"




# -------------------------
# Discriminated Union of Positions
# -------------------------
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


# -------------------------
# Portfolio
# -------------------------
class Portfolio(BaseModel):
    portfolio_id: str
    """
    Unique identifier for the portfolio.
    Example: "PORT123456" or a GUID like "af6e2d34-9012-41cd-8b9e-ff1a1e587e21"
    """

    portfolio_currency: str
    """
    Base currency of the portfolio used for normalization and reporting.
    All position-level market values may be converted to this currency.
    Example: "USD"
    """

    investment_horizon_years: int
    """
    Client's intended investment time horizon in years.
    Helps in determining suitable asset allocation and portfolio strategy.
    Example: 5
    """

    risk_profile: Literal["Conservative", "Moderate", "Aggressive"]
    """
    Investor's risk appetite classification.
    Used for suitability rules and portfolio optimization.
    """

    product_knowledge: List[str]
    """
    List of financial instruments or asset types the client is familiar with.
    Used in suitability and regulatory checks.
    Example: ["Equity", "Bond", "FXForward", "TimeDeposit"]
    """

    positions: List[Position]
    """
    All current holdings in the portfolio across supported asset classes.
    Each position is represented as a discriminated union (e.g., EquityPosition, BondPosition, etc.).
    """
