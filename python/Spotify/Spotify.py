from Spotify.get_reco_tracks import get_reco_tracks
from Spotify.get_genres import get_genres
from Spotify.get_features import get_features
from Spotify.get_token import get_token


class Spotify:
    def __init__(self, sel_tracks):
        self.sel_tracks = sel_tracks
        self.get_token()

    def get_features(self, target="select"):
        get_features(self, target=target)


Spotify.get_token = get_token
Spotify.get_genres = get_genres
Spotify.get_reco_tracks = get_reco_tracks
