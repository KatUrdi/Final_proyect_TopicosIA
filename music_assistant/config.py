from functools import cache
from pydantic_settings import BaseSettings

class AgentSettings(BaseSettings):
    openai_model: str = "gpt4o-mini"
    hf_embeddings_model: str = "intfloat/multilingual-e5-base"
    music_assistant_store_path: str = "libros_embeddings"
    music_assistant_data_path: str = "data"
    openai_api_key: str = "OPENAI_API_KEY"
    log_file: str = ".json"
    genius_api_key: str = "GENIUS_SECRET"
    client_id: str = "SPOTIFY_CLIENT_ID"
    client_secret: str = "SPOTIFY_CLIENT_SECRET"
    redirect_uri: str = "REDIRECT_URI"
    spotify_scope: str = "SPOTIFY_SCOPE"
    username: str = "USERNAME"

    class Config:
        env_file = ".env"
        extra = "allow"

@cache
def get_agent_settings() -> AgentSettings:
    return AgentSettings()