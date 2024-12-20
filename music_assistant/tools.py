import json
import spotipy
import os
from pathlib import Path
from random import randint
from datetime import date, datetime, time
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from music_assistant.rags import MusicRAG
from music_assistant.prompts import music_query_qa_tpl, music_query_description
from music_assistant.config import get_agent_settings
from music_assistant.models import (
    Playlist,
    PlaylistWithTracks,
    Song,
    Artist,
    Album,
    UserInformationTopTracks,
    UserInformationTopGenres,
    UserInformationTopArtists,
    UserInformation
)
from music_assistant.objects import SpotifyObject
from music_assistant.utils import save_user_information
import wikipediaapi
import lyricsgenius as lg

SETTINGS = get_agent_settings()
genius = lg.Genius(SETTINGS.genius_api_key)
genius.remove_section_headers = True
spotify_object = SpotifyObject()

def set_spotify_credentials(client_id: str, client_secret: str, redirect_uri: str):
    
    spotify_object.set_spotify_credentials(client_id, client_secret, redirect_uri)

music_query_tool = QueryEngineTool(
    query_engine=MusicRAG(
        store_path=SETTINGS.music_assistant_store_path,
        data_dir=SETTINGS.music_assistant_data_path,
        qa_prompt_tpl=music_query_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="music_assistant", description=music_query_description, return_direct=False
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

def create_Spotify_playlist(track_uris: list[str], playlist_name: str = "Music Assistant Recommendations", playlist_description: str = "Una playlist creada con Spotipy por el bot de Music Assistant"):
    """
        This function creates a new Spotify playlist for the authenticated user and adds specified tracks to it.

    ### Usage
    - Input: The function requires two inputs:
        1. **playlist_name**: The name you want to give to the new playlist.
        2. **tracks**: A list of strings, each is a uri that identifies a track that should be added to the playlist.
        3. **playlist_description** (optional): A brief description of the playlist's content or purpose.

    ### Output
    - The function returns a `Playlist` object representing the newly created playlist, including its ID, name, and the number of tracks added.

    ### Notes
    - This function is beneficial for users who wish to curate their own playlists based on specific themes, moods, or personal favorites.
    - IT CAN ONLY BE USED AFTER ASKING FOR THE PLAYLIST NAME AND PLAYLIST DESCRIPTION, AND GETTING THE LIST OF URIS.
    - Ask the user for the playlist name and description before using this tool.

    """
    sp = spotify_object.get_spotify_object()
    user_id = sp.current_user()['id']
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description=playlist_description)
    sp.playlist_add_items(playlist_id=new_playlist['id'], items=track_uris)
    return Playlist(id=new_playlist['id'], name=new_playlist['name'], num_tracks=len(track_uris))

create_Spotify_playlist_tool = FunctionTool.from_defaults(fn=create_Spotify_playlist, return_direct=False)

def show_all_Spotify_playlists():
    """
    This function retrieves and displays all playlists created by the authenticated Spotify user.

    ### Usage
    - Input: This function does not require any input parameters.

    ### Output
    - The function returns a list of `Playlist` objects, each containing the playlist ID, name, and the total number of tracks within each playlist.

    ### Notes
    - This tool is useful for users to view all their playlists and manage them effectively.
    """
    sp = spotify_object.get_spotify_object()
    user_playlists = sp.current_user_playlists()
    list_of_playlists = []
    for playlist in user_playlists['items']:
        list_of_playlists.append(Playlist(id=playlist['id'], name=playlist['name'], num_tracks=playlist['tracks']['total']))
    return list_of_playlists

show_all_Spotify_playlists_tool = FunctionTool.from_defaults(fn=show_all_Spotify_playlists, return_direct=False)

def show_specific_Spotify_playlist_tracks(playlist_id: str):
    """
    This function retrieves all the tracks from a specific Spotify playlist identified by its ID.

    ### Usage
    - Input: The function requires one input:
        1. **playlist_id**: The ID of the playlist whose tracks you want to retrieve.

    ### Output
    - The function returns a `PlaylistWithTracks` object containing the playlist details and a list of `Song` objects, each with information about the song and its lyrics.

    ### Notes
    - Use this tool to explore the contents of a specific playlist and get detailed information about each track, including lyrics.
    """
    sp = spotify_object.get_spotify_object()
    playlist_tracks = sp.playlist_tracks(playlist_id)
    list_of_tracks = []
    for track in playlist_tracks['items']:
        list_of_tracks.append(Song(id=track['track']['id'], name=track['track']['name'], artist=track['track']['artists'][0]['name']))
    return PlaylistWithTracks(id=playlist_id, total=playlist_tracks['total'], tracks=list_of_tracks)

show_specific_Spotify_playlist_tracks_tool = FunctionTool.from_defaults(fn=show_specific_Spotify_playlist_tracks, return_direct=False)

def get_artist_Spotify(id: str):
    """
       This function retrieves information about a specific artist from Spotify using their ID.

    ### Usage
    - Input: The function requires a dictionary with the artist's information:
        1. **id**: The Spotify ID of the artist you want to query.
        2. **name**: The name of the artist.

    ### Output
    - The function returns an `Artist` object containing the artist's ID and name.

    ### Notes
    - This tool is useful for obtaining detailed information about an artist, which can be used for further queries or data display.

    """
    sp = spotify_object.get_spotify_object()
    artist = sp.artist(id)
    return Artist(id=artist['id'], name=artist['name'], genres=artist['genres'])

get_artist_Spotify_tool = FunctionTool.from_defaults(fn=get_artist_Spotify, return_direct=False)

def get_several_artists_Spotify(ids: list[str]):
    """
    This function retrieves information about multiple artists from Spotify using their respective IDs.

    ### Usage
    - Input: The function requires one input:
        1. **ids**: A list of Spotify IDs for the artists you want to query.

    ### Output
    - The function returns a list of `Artist` objects, each containing the artist's ID, name, and genres.

    ### Notes
    - This function is beneficial for retrieving information on several artists simultaneously, especially for display or comparison purposes.
    """
    sp = spotify_object.get_spotify_object()
    artists = sp.artists(ids)
    list_of_artists = []
    for artist in artists['artists']:
        list_of_artists.append(Artist(id=artist['id'], name=artist['name'], genres=artist['genres']))
    return list_of_artists

get_several_artists_Spotify_tool = FunctionTool.from_defaults(fn=get_several_artists_Spotify, return_direct=False)

def get_user_information_from_Spotify():

    '''
    This function retrieves user information from Spotify and stores it in a JSON file.
    If the file already exists, it is skipped.

    ### Usage
    - Input: This function does not require any input parameters.
    ### Output: 
    This function does not return any output. It stores user information in a JSON file.

    ### Notes
    - This function is useful for storing user information in a JSON file for future use.
    - It can only be executed if a json file with the same name as the username DOES NOT exist.
    - If the file already exists, it is skipped.
    - If it is skipped, you should use read_saved_user_Spotify_information_tool '''

    filename = SETTINGS.username + ".json"
    if not (os.path.exists(filename)):
    
        sp = spotify_object.get_spotify_object()
        time_ranges = ['short_term', 'medium_term', 'long_term']
        song_ids = []
        songs = []
        artists = []
        user_top_tracks = []
        artists_ids_set = set()

        for time_range in time_ranges:
            results = sp.current_user_top_tracks(limit=50, offset=0, time_range=time_range)
            for song in results['items']:
                if song['id'] in song_ids:
                    continue
                song_ids.append(song['id']) 
                songs.append(song['name'])
                artists.append(song['artists'][0]['name'])
                artists_ids_set.add(song['artists'][0]['id'])
                
                user_top_tracks.append(Song(id=song['id'], name=song['name'], artist=song['artists'][0]['name']))

        if len(artists_ids_set) > 50:
            artists_ids_set = list(artists_ids_set)[:50]

        user_top_artists = get_several_artists_Spotify(list(artists_ids_set))

        user_top_genres = [genre for artist in user_top_artists for genre in artist.genres]
        user_top_genres = set(user_top_genres)

        user_top_tracks_list = [Song(id=song.id, name=song.name, artist=song.artist) for song in user_top_tracks]

        user_top_tracks = UserInformationTopTracks(
        num=len(user_top_tracks_list),  
        top_tracks=user_top_tracks_list
        )

        user_top_artists = UserInformationTopArtists(
            num=len(user_top_artists),
            top_artists=user_top_artists
        )

        user_top_genres_list = list(user_top_genres)

        user_top_genres = UserInformationTopGenres(
            num=len(user_top_genres_list),
            top_genres=user_top_genres_list
            )

        user_information = UserInformation(
            username=SETTINGS.username,
            date=date.today(),
            top_tracks=user_top_tracks,
            top_artists=user_top_artists,
            top_genres=user_top_genres
        )

        save_user_information(user_information)

        return user_information


get_user_information_tool = FunctionTool.from_defaults(fn=get_user_information_from_Spotify, return_direct=False)

def read_saved_user_Spotify_information() -> str:
    """
    Reads user information from Spotify from a JSON file and generates a string for the AI agent to easily read it.
    This user information contains the user's top tracks, top artists, and top genres.
    You can safely assume these are the user's favorite songs, artists, and genres.

    ### Usage
    - Input: None
    
    ###Output:
    - str: A formatted string including all the user's Spotify data that was saved.
    
    ### Notes
    - Assumes the JSON file matches the structure of the UserInformation model.
    """
    file_path = SETTINGS.username+ SETTINGS.log_file
    file = Path(file_path)
    if not file.is_file():
        return "Error: User data file not found."

    with open(file_path, "r") as file:
        user_data_list = json.load(file)

    summary = "User Spotify Information:\n\n"

    for user_data in user_data_list:

        # General Information
        summary += f"[Username: {user_data.get('username', 'N/A')}\n"
        summary += f"Date of Data Collection: {user_data.get('date', 'N/A')}\n\n"
        
        # Top Tracks
        top_tracks = user_data.get('top_tracks', {})
        summary += f"Top {top_tracks.get('num', 0)} Tracks:\n"
        for track in top_tracks.get('top_tracks', []):
            summary += f"  - ID: {track.get('id')}, Name: {track.get('name')} by {track.get('artist')}\n"
        summary += "\n"

        # Top Artists
        top_artists = user_data.get('top_artists', {})
        summary += f"Top {top_artists.get('num', 0)} Artists:\n"
        for artist in top_artists.get('top_artists', []):
            summary += f"  - ID: {artist.get('id')}, Name: {artist.get('name')} (Genres: {', '.join(artist.get('genres', [])) if artist.get('genres') else 'N/A'})\n"
        summary += "\n"

        # Top Genres
        top_genres = user_data.get('top_genres', {})
        summary += f"Top {top_genres.get('num', 0)} Genres:\n"
        for genre in top_genres.get('top_genres', []):
            summary += f"  - {genre}\n"

        summary += "]\n"

    return summary

read_saved_user_Spotify_information_tool = FunctionTool.from_defaults(fn=read_saved_user_Spotify_information, return_direct=False)


def get_recommendations_Spotify(seed_artists: list[str] | None = None, seed_genres: list[str] | None = None, seed_tracks: list[str] | None = None) -> list[str]:
    """
    This function gets recommended tracks from Spotify based on seed artists, genres, and/or tracks.
    IT DOES NOT CREATE A PLAYLIST. IT JUST RETURNS A LIST OF TRACKS.
    The output is a list of uri strings that identify each recommended track and should be passed to the `create_Spotify_playlist` function.

    ### Usage
    - Input: This function accepts up to three optional parameters, at least one of which must be provided as a valid list:
        1. **seed_artists** (list[str] | None): A list of Spotify artist IDs to seed recommendations. *Use artist IDs from user data.* *Pick 5 artists at random, unless specified otherwise* *Send the artist ids as a list of strings. NOT AS A COMMA SEPARATED STRING*
        2. **seed_genres** (list[str] | None): A list of genres to seed recommendations. *Directly use genre names.* *Pick 5 genres at random, unless specified otherwise* *Send the genre names as a list of strings. NOT AS A COMMA SEPARATED STRING*
        3. **seed_tracks** (list[str] | None): A list of Spotify track IDs to seed recommendations. *Use track IDs from user data.* *Pick 5 tracks at random, unless specified otherwise* *Send the track ids as a list of strings. NOT AS A COMMA SEPARATED STRING*
    
    ### Output
    - The function returns an array of uri strings that identify each recommended track.

    ### Notes
    - This tool should be used after reading the user's data.
    - The Spotify API requires at least one valid seed parameter to generate recommendations.
    - This function retrieves recommended tracks based on the provided seed(s). You must use another tool to create the playlist with the tracks.
    - Ensure the Spotify authorization object is properly initialized for user-specific actions.
    - You should select 5 artists, 5 songs, and/or 5 genres according to their saved Spotify data.
    """

    if not any([seed_artists, seed_genres, seed_tracks]):
        raise ValueError("At least one of seed_artists, seed_genres, or seed_tracks must be provided and not None.")

    sp = spotify_object.get_spotify_object()

    recommendations = sp.recommendations(seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks, limit=50)
    track_uris = [track['uri'] for track in recommendations['tracks']]

    return track_uris

get_recommendations_Spotify_tool = FunctionTool.from_defaults(fn=get_recommendations_Spotify, return_direct=False)

def search_Spotify( type: str,artist: str | None = None, album: str | None = None, track: str | None = None, genre: str | None = None, limit: int = 10) -> list[str]:
    """
    This function searches Spotify for tracks, artists, and albums based on the provided query.

    ### Usage
    - Input: This function requires one input:
        1. **type** (str): The type of search to be performed. Can be "track", "artist", or "album". NOTHING ELSE. This is a required parameter. If you're building a playlist, use "track" to get a list or URI's.
        2. **artist** (str | None): The name of the artist to search for.
        3. **album** (str | None): The name of the album to search for.
        4. **track** (str | None): The name of the track to search for.
        5. **genre** (str | None): The name of the genre to search for.
        6. **limit** (int): The maximum number of search results to return. Default is 10. The minimum is 1. The maximum is 50. For a playlist, I suggest you give limit a value of 20, unless otherwise specified by the user.

    ### Output
    - The function returns an array of uri strings that identify each search result.

    ### Notes
    - This function searches Spotify for tracks, artists, and albums based on the provided query.
    - At least one of the parameters **artist**, **album**, **track** or **genre** must be provided and not None.
    """

    sp = spotify_object.get_spotify_object()
    terms_for_query = []
    if(artist):
        terms_for_query.append(f"artist:{artist}")
    if(album):
        terms_for_query.append(f"album:{album}")
    if(track):
        terms_for_query.append(f"track:{track}")
    if(genre):
        terms_for_query.append(f"genre:{genre}")
    query = " ".join(terms_for_query)

    result = sp.search(q=query, type=type)

    list_uris=[]

    if(type == "track"):
        list_uris= [track['uri'] for track in result['tracks']['items']]
    if(type == "artist"):
        list_uris= [artist['uri'] for artist in result['artists']['items']]
    if(type == "album"):
        list_uris= [album['uri'] for album in result['albums']['items']]

    return list_uris


search_Spotify_tool = FunctionTool.from_defaults(fn=search_Spotify, return_direct=False)

def get_album_Spotify(album_uri: str) -> Album:
    """
    This function retrieves the tracks in an album and album information from Spotify.

    ### Usage
    - Input: This function requires one input:
        1. **album_uri** (str): The URI of the album to retrieve tracks from. This is a required parameter.

    ### Output
    - The function returns an `Album` object containing the album details and a list of `Song` objects, each with information about the song.

    ### Notes
    - This function retrieves the tracks in an album from Spotify.
    - The Spotify authorization object is required for this function.
    """

    sp = spotify_object.get_spotify_object()

    results_album = sp.album(album_uri)
    album = Album(
        name=results_album['name'],
        artist=results_album['artists'][0]['name'],
        id=results_album['id'],
        tracks=[Song(id= track['id'], name=track['name'], artist=track['artists'][0]['name']) for track in results_album['tracks']['items']],
    )
    return album

get_album_Spotify_tool = FunctionTool.from_defaults(fn=get_album_Spotify, return_direct=False)