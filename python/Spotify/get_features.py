from matplotlib.pyplot import axis
import pandas as pd
import requests as req
from urllib.parse import urlencode
import math as mt


def get_features(self, target="select"):
    sel_tracks = self.sel_tracks if target == "select" else self.reco_tracks
    features_uri = "https://api.spotify.com/v1/audio-features"
    headers = {
        "authorization": "Bearer {}".format(self.token)
    }
    cnt = mt.floor((len(sel_tracks) - 1) / 100) + 1

    features = pd.DataFrame()
    target_cols = ['id', 'danceability', 'energy', 'key', 'loudness', 'speechiness',
                   'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

    for _cnt in range(0, cnt):
        ids = ""
        for track_id in sel_tracks[_cnt * 100: (_cnt + 1) * 100]['trackId']:
            split_data = track_id.split(",")

            for _ in split_data:
                ids += "{},".format(_)

        ids = ids[:-1]

        query = urlencode({
            "ids": ids
        })

        res = req.get("{}?{}".format(features_uri, query), headers=headers)
        result = res.json()

        features = pd.concat([features, pd.DataFrame(
            result['audio_features'])[target_cols]], ignore_index=True)

    features.rename({"id": "trackId"}, axis=1, inplace=True)

    if target == "select":
        self.features = features
    else:
        self.reco_features = features
