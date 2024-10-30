from functools import cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_model: str = "gpt4o-mini"
    hf_embeddings_model: str = "intfloat/multilingual-e5-base"
    travel_guide_store_path: str = "travel_guide_store"
    travel_guide_data_path: str = "data"
    openai_api_key: str = "OPENAI_API_KEY"
    log_file: str = "trip.json"
    genius_api_key: str = "GENIUS_SECRET"
    client_id: str = "SPOTIFY_CLIENT_ID"
    client_secret: str = "SPOTIFY_CLIENT_SECRET"
    redirect_uri: str = "REDIRECT_URI"
    spotify_scope: str = "SPOTIFY_SCOPE"


@cache
def get_agent_settings() -> AgentSettings:
    return AgentSettings()
