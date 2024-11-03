from functools import cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()

class AgentSettings(BaseSettings):
    openai_model: str = "gpt4o-mini"
    hf_embeddings_model: str = "intfloat/multilingual-e5-base"
    music_assistant_store_path: str = "libros_embeddings"
    music_assistant_data_path: str = "data"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "default_openai_key")  # Cambia el valor por defecto si es necesario
    log_file: str = ".json"
    genius_api_key: str = os.getenv("GENIUS_SECRET", "default_genius_key")  # Cambia el valor por defecto si es necesario
    client_id: str = os.getenv("SPOTIFY_CLIENT_ID", "default_client_id")  # Cambia el valor por defecto si es necesario
    client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET", "default_client_secret")  # Cambia el valor por defecto si es necesario
    redirect_uri: str = os.getenv("REDIRECT_URI", "http://127.0.0.1:7860/")  # Cambia el valor por defecto si es necesario
    spotify_scope: str = os.getenv("SPOTIFY_SCOPE", "default_scope")  # Cambia el valor por defecto si es necesario
    username: str = os.getenv("USERNAME", "default_username")  # Cambia el valor por defecto si es necesario

    class Config:
        env_file = ".env"
        extra = "allow"

@cache
def get_agent_settings() -> AgentSettings:
    return AgentSettings()
