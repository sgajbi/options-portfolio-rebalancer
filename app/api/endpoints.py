from fastapi import APIRouter
from typing import List 
from ..models.portfolio import Portfolio
from ..models.options import TaggedOptionPosition 
from ..services.screener import tag_option_strategies

router = APIRouter()

@router.post("/screen", response_model=List[TaggedOptionPosition])
def screen_portfolio(portfolio: Portfolio) -> List[TaggedOptionPosition]:
    """
    Analyzes a given portfolio to identify and tag various options strategies,
    such as Covered Calls, Protective Puts, and Naked options.
    """
    return tag_option_strategies(portfolio)