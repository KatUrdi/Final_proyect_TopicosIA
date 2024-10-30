import json
import spotipy
from random import randint
from datetime import date, datetime, time
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from music_assistant.rags import MusicRAG
from music_assistant.prompts import music_query_qa_tpl, music_query_description
from music_assistant.config import get_agent_settings
from music_assistant.models import (
    TripReservation,
    TripType,
    HotelReservation,
    RestaurantReservation,
)
from music_assistant.objects import SpotifyObject
#from music_assistant.utils import save_reservation
import wikipediaapi
import lyricsgenius as lg

SETTINGS = get_agent_settings()
genius = lg.Genius(SETTINGS.genius_api_key)
spotify_object = SpotifyObject()

def set_spotify_credentials(client_id: str, client_secret: str, redirect_uri: str):
    spotify_object.set_spotify_credentials(client_id, client_secret, redirect_uri)

music_query_tool = QueryEngineTool(
    query_engine=MusicRAG(
        store_path=SETTINGS.travel_guide_store_path,
        data_dir=SETTINGS.travel_guide_data_path,
        qa_prompt_tpl=music_query_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="travel_guide", description=music_query_description, return_direct=False
    ),
)

def get_wikipedia_page(lookup_term: str) -> str:
    """
    This tool is designed to retrieve the Wikipedia page for a given term. It allows the user to search for general information about artists, songs, albums, music genres, and other music-related topics.

    ### Usage
    - Input: The tool requires one input:
        1. **lookup_term**: The term to search for in Wikipedia (e.g., a song, an album, an artist, a music genre, discography, music labels, etc.).

    ### Output
    - The tool returns the full text of the Wikipedia page if found. If not, it returns a message saying no page was found.

    ### Notes
    - Use this tool to provide detailed background information or context about artists, songs, music genres, albums, etc. The input to the tool is the term that the user is interested in or other terms related to the topic.
    """
    user_agent = 'MusicChatbot/1.0 (https://www.upb.edu/)'
    wiki_wiki = wikipediaapi.Wikipedia(user_agent,'en')
    page = wiki_wiki.page(lookup_term)
    
    if page.exists():
        return page.text
    else:
        return f"No Wikipedia page found for {lookup_term}."

wikipedia_tool = FunctionTool.from_defaults(fn=get_wikipedia_page, return_direct=False)

def get_lyrics_from_genius(song_title: str, artist_name: str) -> str:
    """
    This tool is designed to retrieve the lyrics for a given song.

    ### Usage
    - Input: The tool requires two inputs:
        1. **song_title**: The title of the song.
        2. **artist_name**: The name of the artist.

    ### Output
    - The tool returns the lyrics of the song if found. If not, it returns a message saying no lyrics were found.

    ### Notes
    - Use this tool to provide detailed lyrics about a song. The input to the tool is the title of the song and the name of the artist.
    """
    try:
        song = genius.search_song(song_title, artist_name)
        if song:
            return song.lyrics
        else:
            return None
    except Exception as e:
        print(f"Error fetching lyrics for {song_title} by {artist_name}: {e}")
        return None

lyrics_genius_tool = FunctionTool.from_defaults(fn=get_lyrics_from_genius, return_direct=False)

def create_Spotify_playlist(playlist_name: str, playlist_description: str, track_uris: list[str]):
    sp = spotify_object.get_spotify_object()
    user_id = sp.current_user()['id']
    playlist_description = "Una playlist creada con Spotipy"
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description=playlist_description)
    sp.playlist_add_items(playlist_id=new_playlist['id'], items=track_uris)

create_Spotify_playlist_tool = FunctionTool.from_defaults(fn=create_Spotify_playlist, return_direct=False)

