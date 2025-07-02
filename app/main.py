from fastapi import FastAPI
from .api.endpoints import router as portfolio_router

app = FastAPI()

app.include_router(portfolio_router, prefix="/api")
