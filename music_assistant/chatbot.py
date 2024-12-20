import gradio as gr
from music_assistant.objects import SpotifyObject
from music_assistant.prompts import agent_prompt_tpl
from music_assistant.agent import MusicAgent
from music_assistant.config import get_agent_settings
from music_assistant.tools import get_user_information_from_Spotify
from llama_index.core.tools import FunctionTool

from music_assistant.utils import save_user_information
SETTINGS = get_agent_settings()
agent = MusicAgent(agent_prompt_tpl).get_agent()

spotify_object = SpotifyObject()

def agent_response(message, history):
    return agent.chat(message).response


if __name__ == "__main__":
    spotify_object.set_spotify_credentials(SETTINGS.client_id, SETTINGS.client_secret, SETTINGS.redirect_uri)
    get_user_information_from_Spotify()
    demo = gr.ChatInterface(agent_response, type="messages")
    demo.launch()

