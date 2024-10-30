from pydantic import BaseModel, Field
from enum import Enum
from datetime import date, datetime
from typing import Optional


class TripType(str, Enum):
    flight = "FLIGHT"
    bus = "BUS"


class TripReservation(BaseModel):
    trip_type: TripType
    date: date
    departure: str
    destination: str
    cost: int


class HotelReservation(BaseModel):
    checkin_date: date
    checkout_date: date
    hotel_name: str
    city: str
    cost: int


class RestaurantReservation(BaseModel):
    reservation_time: datetime
    restaurant: str
    city: str
    dish: str
    cost: int


class AgentAPIResponse(BaseModel):
    status: str
    agent_response: str
    timestamp: datetime = Field(default_factory=datetime.now)

class RecommendationRequest(BaseModel):
    object: str
    notes: Optional[list[str]] = Field(None)

class ReservationRequest(BaseModel):
    origin: str
    destination: str
    date: str

class HotelReservationRequest(BaseModel):
    checkin_date: str
    checkout_date: str
    hotel: str
    city: str

class RestaurantReservationRequest(BaseModel):
    date: str
    time: str
    restaurant: str
    city: str
    dish: Optional[str] = Field(None)