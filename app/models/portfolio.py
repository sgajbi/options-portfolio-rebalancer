from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated
from typing_extensions import Annotated as TAnnotated
from pydantic import TypeAdapter

class EquityPosition(BaseModel):
    type: Literal["Equity"]
    symbol: str
    quantity: int
    cio_rating: Literal["Buy", "Hold", "Sell"]

class OptionPosition(BaseModel):
    type: Literal["Option"]
    symbol: str
    option_type: Literal["Call", "Put"]
    strike: float
    expiry: str
    position: Literal["Long", "Short"]
    contracts: int

# Discriminated Union using 'type' field
Position = Annotated[Union[EquityPosition, OptionPosition], Field(discriminator='type')]

class Portfolio(BaseModel):
    client_id: str
    investment_horizon_years: int
    risk_profile: Literal["Conservative", "Moderate", "Aggressive"]
    product_knowledge: List[str]
    positions: List[Position]
