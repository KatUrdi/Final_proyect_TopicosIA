import os
import json
from datetime import date, datetime
from music_assistant.models import (
    Playlist,
    PlaylistWithTracks,
    Song
)
from music_assistant.config import get_agent_settings

SETTINGS = get_agent_settings()


def custom_serializer(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_user_information(
    reservation: RestaurantReservation | TripReservation | HotelReservation,
):
    reservation_dict = reservation.model_dump()
    print(f"saving reservation: {reservation_dict}")
    reservations = []
    if os.path.exists(SETTINGS.log_file) and os.path.getsize(SETTINGS.log_file) > 0:
        with open(SETTINGS.log_file, "r") as file:
            try:
                reservations = json.load(file)
            except json.JSONDecodeError:
                reservation = []
    else:
        reservations = []
    reservation_dict["reservation_type"] = reservation.__class__.__name__
    reservations.append(reservation_dict)

    with open(SETTINGS.log_file, "w") as file:
        json.dump(reservations, file, indent=4, default=custom_serializer)

    print(f"saved reservation!")
