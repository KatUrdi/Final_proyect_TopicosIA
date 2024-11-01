from llama_index.core import PromptTemplate
from llama_index.core.agent import ReActAgent
from music_assistant.tools import (
    music_query_tool,
    wikipedia_tool,
    lyrics_genius_tool,
    create_Spotify_playlist_tool,
    show_all_Spotify_playlists_tool,
    show_specific_Spotify_playlist_tracks_tool,
    get_artist_Spotify_tool,
    get_several_artists_Spotify_tool,
    get_user_information_tool
)

class MusicAgent:
    def __init__(self, system_prompt: PromptTemplate | None = None):
        self.agent = ReActAgent.from_tools(
            [
                music_query_tool,
                wikipedia_tool,
                lyrics_genius_tool,
                create_Spotify_playlist_tool,
                show_all_Spotify_playlists_tool,
                show_specific_Spotify_playlist_tracks_tool,
                get_artist_Spotify_tool,
                get_several_artists_Spotify_tool,
                get_user_information_tool
            ],
            verbose=True,
        )
        if system_prompt is not None:
            self.agent.update_prompts({"agent_worker:system_prompt": system_prompt})

    def get_agent(self) -> ReActAgent:
        return self.agent
