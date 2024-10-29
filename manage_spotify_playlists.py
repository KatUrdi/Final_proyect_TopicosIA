import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configuración de autenticación
client_id = '881c27bda6e04b05be063f48f8c6bca1'
client_secret = 'c887a7b3e2404cd883805f4fb71153ab'
redirect_uri = 'http://localhost:7860/'  # Cambia esto si es necesario

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='playlist-read-private playlist-modify-private'  # Incluye ambos scopes
))

# Obtener las playlists del usuario autenticado
user_playlists = sp.current_user_playlists()

# Imprimir las playlists
print("Tus playlists:")
for playlist in user_playlists['items']:
    print(f"Nombre: {playlist['name']}, ID: {playlist['id']}")

# Obtener el usuario actual
user_id = sp.current_user()['id']

# Crear una nueva playlist
playlist_name = "Playlist Python"
playlist_description = "Una playlist creada con Spotipy"
new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description=playlist_description)
print(f"Playlist creada: {new_playlist['name']} con ID: {new_playlist['id']}")

# URIs de canciones que quieres agregar a la playlist
track_uris = [
    'spotify:track:4cOdK2wGLETKBW3PvgPWqT',  # Reemplaza estos URIs por los de las canciones que prefieras
    'spotify:track:1301WleyT98MSxVHPZCA6M'
]

# Agregar canciones a la nueva playlist
sp.playlist_add_items(playlist_id=new_playlist['id'], items=track_uris)
print("Canciones agregadas a la playlist.")
