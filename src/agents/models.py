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
    max_stops:Optional[int] = Field(None, description="The maximum number of stops for the flight", ge=0, le=3)
    preferred_airlines:List[str] = Field(default_factory=list, description="The preferred airlines for the flight")

    flexible_dates:bool = Field(default=False, description="Whether the user is flexible with the dates of the flight")
    date_flexibility_days:int = Field(default=0, description="The number of days the user is flexible with the dates of the flight", ge=0, le=3)


    @validator('departure_date')
    def validate_departure_date(cls, v):
        """validate the departure date"""
        if v:
            try:
                date_obj = datetime.strptime(v, '%Y-%m-%d').date()
                if date_obj < date.today().date():
                    raise ValueError("Departure date cannot be in the past")
                return v
            except ValueError as e:
                if "does not match" in str(e):
                    raise ValueError("Departure date must be in YYYY-MM-DD format")
                raise e
        return v

    @validator('origin', 'destination')
    def validate_airport_codes(cls, v):
        """validate the airport codes"""
        if v:
            v = v.strip().upper()
