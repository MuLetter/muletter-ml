import pandas as pd
import requests as req
from urllib.parse import urlencode
import math as mt
from functools import reduce


@property
def get_genres(self):
    artists_uri = "https://api.spotify.com/v1/artists"

    genres = list()

    artist_list = list()
    seed_genres = list()
    for artist_id in self.sel_tracks['artistIds']:
        split_data = artist_id.split(",")

        for _ in split_data:
            if _ not in artist_list:
                artist_list.append(_)

    headers = {
        "authorization": "Bearer {}".format(self.token)
    }

    cnt = mt.floor((len(artist_list) - 1) / 50) + 1
    if cnt == 0:
        print(self.sel_tracks)

    one_genres = list()
    for _cnt in range(0, cnt):
        ids = ""
        for artist_id in artist_list[_cnt * 50: (_cnt + 1) * 50]:
            ids += "{},".format(artist_id)

        ids = ids[:-1]
        query = urlencode({
            "ids": ids
        })

        res = req.get("{}?{}".format(artists_uri, query), headers=headers)

        result = res.json()
        artists = result['artists']

        for artist in artists:
            _genres = artist['genres']
            _art_genres = list()

            for g in _genres:
                g_split = g.split(" ")
                if len(g_split) == 1:
                    g_split = g_split[0].split("-")
                for _ in g_split:
                    _art_genres.append(_)
                    one_genres.append(_)
            genres.append(_art_genres)

    count_group = pd.DataFrame(
        one_genres, columns=['genre']).reset_index().groupby('genre').count()
    count_group.columns = ['count']

    top_genre = count_group.sort_values(
        by=['count'], ascending=False).index.values[0]
    if top_genre == "k":
        top_genre = "k-pop"

    get_available_genres_uri = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    res = req.get(get_available_genres_uri, headers=headers)

    available_genres = res.json()['genres']

    for _g in genres:
        _seed_genres = list()
        for genre in _g:
            in_g = ""

            if genre in available_genres:
                in_g = genre
                if in_g in ['edm', 'house', 'electro', 'dance', 'alternative',
                            'soul', 'indie', 'metal', 'grunge', 'reggaeton',
                            'latino']:
                    in_g = ""
            elif ("k" in genre) | ("korean" in genre):
                in_g = "k-pop"
            # elif "r&b" in genre:
            #     in_g = "soul"
            elif "pop" in genre:
                in_g = "pop"
            elif "hip" in genre:
                in_g = "hip-hop"
            elif "rap" in genre:
                in_g = "hip-hop"

            if in_g != "":
                if in_g not in _seed_genres:
                    _seed_genres.append(in_g)

            if len(_seed_genres) == 5:
                break

        if len(_seed_genres) == 0:
            _seed_genres.append(top_genre)

        seed_genres.append(
            reduce(lambda acc, cur: acc +
                   ",{}".format(cur), _seed_genres, "")[1:]
        )

    rtn_genres = pd.DataFrame(artist_list, columns=['artistIds'])
    rtn_genres['genres'] = seed_genres

    self.genres = rtn_genres
