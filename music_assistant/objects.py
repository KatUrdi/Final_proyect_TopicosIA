import spotipy
from spotipy.oauth2 import SpotifyOAuth
from music_assistant.config import get_agent_settings

SETTINGS = get_agent_settings()

class SpotifyObject:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SETTINGS.client_id,
            client_secret=SETTINGS.client_secret,
            redirect_uri=SETTINGS.redirect_uri,
            scope=SETTINGS.spotify_scope #TODO: Añadir mas scopes para poder ver albumes, canciones mas escuchadas, informacion de artista, album y canciones
        ))
    
    def set_spotify_credentials(self, client_id: str, client_secret: str, redirect_uri: str):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SETTINGS.spotify_scope #TODO: Añadir mas scopes para poder ver albumes, canciones mas escuchadas, informacion de artista, album y canciones
        ))
    
    def get_spotify_object(self):
        return self.sp