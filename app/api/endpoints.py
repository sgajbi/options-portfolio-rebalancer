from fastapi import APIRouter
from ..models.portfolio import Portfolio
from ..services.screener import tag_option_strategies

router = APIRouter()

@router.post("/screen")
def screen_portfolio(portfolio: Portfolio):
    return tag_option_strategies(portfolio)
