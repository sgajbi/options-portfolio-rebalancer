from pydantic import BaseModel
from enum import Enum

class ISOCurrency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    AUD = "AUD"
    CAD = "CAD"
    SGD = "SGD"
    INR = "INR"