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

class Album(BaseModel):
    id: str
    name: str
    artist: str
    tracks: list[Song]


class PlaylistWithTracks(BaseModel):
    id: str
    total: int
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