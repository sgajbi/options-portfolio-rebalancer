from fastapi import APIRouter
from typing import List, Union
from ..models.portfolio import Portfolio
from ..models.options import TaggedOptionPosition
from ..models.option_strategy import OptionStrategy 
from ..services.screener import tag_option_strategies

router = APIRouter()

@router.post("/screen", response_model=List[Union[TaggedOptionPosition, OptionStrategy]]) 
def screen_portfolio(portfolio: Portfolio) -> List[Union[TaggedOptionPosition, OptionStrategy]]: 
    """
    Analyzes a given portfolio to identify and tag various options strategies,
    such as Covered Calls, Protective Puts, and Naked options.
    """
    return tag_option_strategies(portfolio)