from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from enum import Enum
import re


class TripType(str, Enum):
    """
    Enum for type of trips.
    """
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"
    MULTI_CITY = "multi_city"

class PassengerType(str, Enum):
    """type of passenger flying"""
    ADULT="adult"
    CHILD="child"
    INFANT="infant"

class CabinClass(str, Enum):
    """type of cabin class"""
    ECONOMY="economy"
    PREMIUM_ECONOMY="premium_economy"
    BUSINESS="business"
    FIRST="first"


class FlightQuery(BaseModel):
    """Model for a users flight query"""

    origin:Optional[str] = Field(None, description="The origin of the flight")
    destination:Optional[str] = Field(None, description="The destination of the flight")


    departure_date:Optional[str] = Field(None, description="The departure date of the flight in YYYY-MM-DD format, regex: ^\\d{4}-\\d{2}-\\d{2}$")

    return_date:Optional[str] = Field(None, description="The return date of the flight in YYYY-MM-DD format, regex: ^\\d{4}-\\d{2}-\\d{2}$")

    passengers:int = Field(default=1, description="The number of passengers flying", ge=1, le=9)
    passenger_types:List[PassengerType] = Field(default_factory=lambda: [PassengerType.ADULT], description="The type of passengers flying")

    budget:Optional[float] = Field(None, description="The budget for the flight in USD", ge=0)
    currency:str =Field(default='USD', description="The currency of the budget")

    trip_type:TripType = Field(default=TripType.ONE_WAY, description="The type of trip")

    cabin_class:CabinClass = Field(default=CabinClass.ECONOMY, description="The cabin class of the flight")
