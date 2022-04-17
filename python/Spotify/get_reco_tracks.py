import pandas as pd
import numpy as np
import requests as req
from urllib.parse import urlencode
from functools import reduce


def get_reco_tracks(self, og=None):
    for idx, _st in self.sel_tracks.copy().iterrows():
        artist_list = _st['artistIds'].split(",")

        if len(artist_list) > 1:
            self.sel_tracks.drop([idx], axis=0, inplace=True)
            for _art in artist_list:
                _copy_st = _st.copy()
                _copy_st['artistIds'] = _art
                self.sel_tracks = self.sel_tracks.append(
                    _copy_st, ignore_index=True
                )
    try:
        seed_info = pd.merge(
            left=self.sel_tracks, right=self.features, how='inner', on='trackId')
        seed_info = pd.merge(left=seed_info, right=self.genres,
                             how='inner', on='artistIds')
    except:
        return

    del seed_info['artistNames']
    del seed_info['trackName']
    seed_info.rename(columns={"trackId": "tracks"}, inplace=True)
    seed_info.rename(columns={"artistIds": "artists"}, inplace=True)

    # target cols 13 (except popularity)
    feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                    'key', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
    target_cols = list()
    rename_cols = dict()

    for col in feature_cols:
        target_col = "target_{}".format(col)
        rename_cols[col] = target_col

        target_cols.append(target_col)

    seed_cols = ['tracks', 'artists']
    for col in seed_cols:
        seed_col = "seed_{}".format(col)
        seed_info.rename(columns={
            col: seed_col
        }, inplace=True)

    seed_info.rename(columns=rename_cols, inplace=True)

    feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                    'key', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
    target_cols = list()
    rename_cols = dict()

    for col in feature_cols:
        target_col = "target_{}".format(col)
        rename_cols[col] = target_col

        target_cols.append(target_col)

    seed_cols = ['tracks', 'artists', 'genres']
    for col in seed_cols:
        seed_col = "seed_{}".format(col)
        seed_info.rename(columns={
            col: seed_col
        }, inplace=True)

    seed_info.rename(columns=rename_cols, inplace=True)

    _reco_tracks = np.array([])

    for seed_idx in range(len(seed_info)):
        reco_uri = "https://api.spotify.com/v1/recommendations"

        seed_dict = seed_info.iloc[seed_idx].to_dict()
        seed_dict['market'] = "KR"
        seed_dict['limit'] = 100

        query = urlencode(seed_dict)
        headers = {
            "authorization": "Bearer {}".format(self.token)
        }
        try:
            res = req.get("{}?{}".format(reco_uri, query), headers=headers)
            result = res.json()

            _tmp = np.array([])
            for track in result['tracks']:
                _id = track['id']
                _name = track['name']
                album = track['album']
                duration_ms = track['duration_ms']
                images = album["images"]

                if len(images) == 0:
                    _image = ""
                else:
                    _image = images[0]['url']

                artist_list = album['artists']
                artists = reduce(
                    lambda acc, cur: cur[1]['name'] if cur[0] == 0 else acc +
                    "," + cur[1]['name'],
                    enumerate(artist_list),
                    ""
                )
                artists_id = reduce(
                    lambda acc, cur: cur[1]['id'] if cur[0] == 0 else acc +
                    "," + cur[1]['id'],
                    enumerate(artist_list),
                    ""
                )
                _reco_tracks = np.append(_reco_tracks,
                                         [_id, _name, artists_id,
                                             artists, _image, duration_ms]
                                         )
        except:
            return res

    _reco_tracks = _reco_tracks.reshape(-1, 6)
    reco_tracks = pd.DataFrame(_reco_tracks, columns=[
                               'trackId', 'trackName', 'artistIds', 'artistNames', 'image', 'duration'])

    # 중복제거
    except_overlap_cols = [
        _ not in self.sel_tracks['trackId'].values for _ in reco_tracks['trackId']]
    reco_tracks = reco_tracks[except_overlap_cols]
    reco_tracks.drop_duplicates("trackId", inplace=True)

    if og is not None:
        reco_tracks = reco_tracks[[
            _ not in og['trackId'].values for _ in reco_tracks['trackId']]]

    self.reco_tracks = reco_tracks
