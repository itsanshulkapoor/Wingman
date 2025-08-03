import pytest
from agents.models import FlightQuery, TripType, Airport

def test_flight_query_validation():
    valid_query = FlightQuery(origin="NYC", destination="LAX", departure_date="2024-01-01", return_date="2024-01-02", passengers=1, trip_type=TripType.ONE_WAY, budget=1000)

    assert valid_query.origin == "NYC"

    with pytest.raises(ValueError, match="past"):
        FlightQuery(origin="NYC", destination="LAX", departure_date="2024-01-01", return_date="2024-01-02", passengers=1, trip_type=TripType.ONE_WAY, budget=1000)

        # Test round trip validation
    with pytest.raises(ValueError, match="Round trip requires"):
        FlightQuery(
            origin="NYC",
            destination="LAX",
            trip_type=TripType.ROUND_TRIP
            # Missing return_date
        )

def test_airport_model():
    # Test IATA code validation
    airport = Airport(
        iata_code="lax",  # Should be converted to uppercase
        name="Los Angeles International",
        city="Los Angeles",
        country="United States",
        country_code="US"
    )
    assert airport.iata_code == "LAX"

def test_flight_offer_validation():
    # Test with minimal required fields
    # Test price validation
    # Test segment validation
    pass
