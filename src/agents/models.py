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
                if date_obj < date.today():
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
            if len(v) == 3:
                if not re.match(r'^[A-Z]{3}$', v):
                    raise ValueError('airport code must be 3 letters')
            elif len(v) < 2:
                raise ValueError('city name must be at least 2 letters')
        return v

    @root_validator
    def validate_trip_consistency(cls, values):
        """ross field validation for trip logic"""
        trip_type = values.get('trip_type')
        return_date = values.get('return_date')
        departure_date = values.get('departure_date')

        if trip_type == TripType.ROUND_TRIP and not return_date:
            raise ValueError('return date is required for multi-city trip')

        if departure_date and return_date:
            dep_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            ret_date = datetime.strptime(return_date, '%Y-%m-%d').date()
            if dep_date >= ret_date:
                raise ValueError('return date must be after departure date')

        passengers = values.get('passengers',1)
        passenger_types = values.get('passenger_types',[])
        if len(passenger_types) != passengers:
            values['passenger_types'] = [PassengerType.ADULT] * passengers

        return values

class Airport(BaseModel):
    iata_code: str = Field(..., description="The IATA code of the airport")
    icao_code: Optional[str] = Field(None, description="4-letter ICAO code")
    name: str = Field(..., description="Full airport name")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    country_code: str = Field(..., description="2-letter country code")
    timezone: Optional[str] = Field(None, description="Airport timezone")

    # Geographic coordinates
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")

    # Additional metadata
    terminals: Optional[int] = Field(None, description="Number of terminals")
    hub_airlines: List[str] = Field(default_factory=list, description="Hub airlines")

    @validator('iata_code')
    def validate_iata_code(cls, v):
        """validate the IATA code is formatted correctly"""
        v = v.upper().strip()
        if not re.match(r'^[A-Z]{3}$', v):
            raise ValueError('IATA code must be exactly 3 uppercase letters')
        return v

class FlightSegment(BaseModel):
    """Individual flight journey segment"""

     # Flight identification
    airline: str = Field(..., description="Airline name or code")
    airline_code: str = Field(..., description="2-letter airline code")
    flight_number: str = Field(..., description="Flight number")

    # Route information
    departure_airport: str = Field(..., description="Departure airport IATA code")
    arrival_airport: str = Field(..., description="Arrival airport IATA code")

    # Timing (ISO format for consistency)
    departure_time: str = Field(..., description="Departure time in ISO format")
    arrival_time: str = Field(..., description="Arrival time in ISO format")
    duration: str = Field(..., description="Flight duration (e.g., 'PT2H30M')")

    # Aircraft and service details
    aircraft_type: Optional[str] = Field(None, description="Aircraft model")
    cabin_class: CabinClass = Field(CabinClass.ECONOMY, description="Cabin class")

    # Operational details
    stops: int = Field(0, description="Number of stops", ge=0)
    layover_airports: List[str] = Field(default_factory=list)
    operating_airline: Optional[str] = Field(None, description="Operating airline if codeshare")

class FlightOffer(BaseModel):
    """
    Complete flight offer with pricing and segments.
    This is what your search_flights tool will return.
    """

    # Unique identifier for this offer
    offer_id: str = Field(..., description="Unique offer identifier")

    # Pricing information
    total_price: float = Field(..., description="Total price for all passengers")
    price_per_passenger: float = Field(..., description="Price per passenger")
    currency: str = Field("USD", description="Currency code")

    # Price breakdown
    base_fare: Optional[float] = Field(None, description="Base fare amount")
    taxes: Optional[float] = Field(None, description="Tax amount")
    fees: Optional[float] = Field(None, description="Additional fees")

    # Flight segments (outbound + return if applicable)
    outbound_segments: List[FlightSegment] = Field(..., description="Outbound flight segments")
    return_segments: List[FlightSegment] = Field(default_factory=list, description="Return flight segments")

    # Booking information
    booking_url: Optional[str] = Field(None, description="Direct booking URL")
    booking_class: str = Field("ECONOMY", description="Booking class")
    seats_available: Optional[int] = Field(None, description="Seats remaining")

    # Additional metadata
    is_refundable: bool = Field(False, description="Refund policy")
    baggage_included: bool = Field(False, description="Baggage inclusion")
    meal_service: bool = Field(False, description="Meal service available")

    # Search metadata
    search_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    validity_period: Optional[str] = Field(None, description="How long this offer is valid")

    @validator('offer_id')
    def validate_offer_id(cls, v):
        """Ensure offer ID is properly formatted"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Offer ID cannot be empty')
        return v.strip()

    @root_validator
    def validate_flight_logic(cls, values):
        """Validate flight offer consistency"""
        outbound = values.get('outbound_segments', [])
        return_segments = values.get('return_segments', [])

        if not outbound:
            raise ValueError('Flight offer must have at least one outbound segment')

        # Validate pricing logic
        total_price = values.get('total_price', 0)
        price_per_passenger = values.get('price_per_passenger', 0)

        if total_price > 0 and price_per_passenger > 0:
            # Basic sanity check - total should be >= per passenger
            if total_price < price_per_passenger:
                raise ValueError('Total price cannot be less than price per passenger')

        return values

class SearchResults(BaseModel):
    """
    Container for flight search results with metadata.
    This wraps the response from your flight search tool.
    """

    # Core results
    flights: List[FlightOffer] = Field(default_factory=list, description="Found flight offers")
    total_results: int = Field(0, description="Total number of flights found")

    # Search context
    search_id: str = Field(..., description="Unique search identifier")
    query_parameters: FlightQuery = Field(..., description="Original search query")

    # Metadata
    search_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    search_duration_ms: Optional[int] = Field(None, description="Search time in milliseconds")

    # API information
    api_provider: str = Field("amadeus", description="API provider used")
    api_calls_made: int = Field(1, description="Number of API calls for this search")

    # Result statistics
    min_price: Optional[float] = Field(None, description="Lowest price found")
    max_price: Optional[float] = Field(None, description="Highest price found")
    average_price: Optional[float] = Field(None, description="Average price")

    # Filtering applied
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    results_filtered_count: int = Field(0, description="Results removed by filtering")

    @root_validator
    def calculate_statistics(cls, values):
        """Auto-calculate price statistics"""
        flights = values.get('flights', [])

        if flights:
            prices = [flight.total_price for flight in flights]
            values['min_price'] = min(prices)
            values['max_price'] = max(prices)
            values['average_price'] = sum(prices) / len(prices)
            values['total_results'] = len(flights)

        return values

def create_sample_flight_query() -> FlightQuery:
    """create a sample flight query"""
    return FlightQuery(
        origin="LAX",
        destination="SFO",
        departure_date="2024-01-01",
        return_date="2024-01-02",
        passengers=1,
        trip_type=TripType.ONE_WAY,
        budget=1000,
    )

def validate_query_completness(query:FlightQuery) -> List[str]:
    """validate what is missing from the query"""
    missing = []

    if not query.origin:
        missing.append('origin')
    if not query.destination:
        missing.append('destination')
    if not query.departure_date:
        missing.append('departure_date')

    return missing
