from pydantic import BaseModel, Field
from enum import Enum
from datetime import date, datetime
from typing import Optional


class Playlist(BaseModel):
    id: str
    name: str
    num_tracks: int


class Song(BaseModel):
    id:str
    name: str
    artist: str

class Artist(BaseModel):
    id: str
    name: str
    genres: list[str] | None


class PlaylistWithTracks(BaseModel):
    playlist: Playlist
    tracks: list[Song]

class UserInformationTopTracks(BaseModel):
    num: int
    top_tracks: list[Song]

class UserInformationTopArtists(BaseModel):
    num: int
    top_artists: list[Artist]

class UserInformationTopGenres(BaseModel):
    num: int
    top_genres: list[str]

class UserInformation(BaseModel):
    username: str
    date: date
    top_tracks: UserInformationTopTracks
    top_artists: UserInformationTopArtists
    top_genres: UserInformationTopGenres

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