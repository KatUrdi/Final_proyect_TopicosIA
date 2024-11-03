import os
import json
from datetime import date, datetime
from music_assistant.models import (
    Playlist,
    PlaylistWithTracks,
    Song,
    Artist,
    UserInformationTopTracks,
    UserInformationTopGenres,
    UserInformationTopArtists,
    UserInformation,
)
from music_assistant.config import get_agent_settings

SETTINGS = get_agent_settings()


def custom_serializer(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_user_information(
    information: UserInformation
):
    information_dict = information.model_dump()
    information_dict["object_type"] = information.__class__.__name__
    information_dict["top_tracks"]["object_type"] = information.top_tracks.__class__.__name__
    information_dict["top_artists"]["object_type"] = information.top_artists.__class__.__name__
    information_dict["top_genres"]["object_type"] = information.top_genres.__class__.__name__
    print(f"saving user {SETTINGS.username} information: {information_dict}")
    filename = SETTINGS.username + ".json"
    print(f"filename: {filename} exists: {os.path.exists(filename)} ")
    user_information=[]
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r") as file:
            try:
                user_information = json.load(file)
            except json.JSONDecodeError:
                user_information = []
    else:
        user_information = []
    
    user_information.append(information_dict)

    with open(filename, "w") as file:
        json.dump(user_information, file, indent=4, default=custom_serializer)

    print(f"saved information!")
