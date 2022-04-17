from KMeans import KMeans
from DataPreprocessing import make_norm
from CoordGenerator import CoordGenerator

from sklearn.metrics.pairwise import euclidean_distances as euc
import pandas as pd
import numpy as np
import datetime as dt
from pymongo import MongoClient as mc


class SeedZoneController:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).TestMuLetter
        self.seed_zone = self.conn.SeedZone
        self.mail_box = self.conn.MailBox
        self.cluster_zone = self.conn.ClusterZone
        self.coord_gen = CoordGenerator()

    def make_new_cluster(self):
        _seed_features = self.seed_zone.find({}, {
            "_id": 0,
            "label": 0
        })
        seed_features = pd.DataFrame([_ for _ in _seed_features])
        self.seed_features = seed_features

        norm_info, norm_features = make_norm(seed_features, get_norm_info=True)
        self.norm_info = norm_info
        self.norm_features = norm_features

        kmeans = KMeans(
            datas=norm_features
        )
        kmeans.run(early_stop_cnt=5,
                   ecv_check_count=20)
        kmeans.sorting_ver_2()
        music_label = pd.DataFrame(norm_features['trackId'])
        music_label['label'] = kmeans.clusters
        self.music_label = music_label
        self.kmeans = kmeans

        _k_features = list()
        for k_pat in kmeans.K_pattern:
            _k_features.append(k_pat.tolist())

        # Save Cluster Info
        cluster_zone_doc = dict({
            "version": self.cluster_zone.estimated_document_count() + 1,
            "normInfo": norm_info,
            "features": _k_features,
            "ecv": kmeans.ecv,
            "K": len(_k_features),
            "createdAt": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        })
        self.cluster_zone.insert_one(cluster_zone_doc)

        for _, label_info in music_label.iterrows():
            track_id, label = label_info

            self.seed_zone.update_one({
                "trackId": track_id
            }, {
                "$set": {
                    "label": label
                }
            })

        self.coord_gen.all_remake_coords()

    def set_label(self, features):
        row = features.copy()

        cluster_info = self.cluster_zone.find().sort("version", -1)[0]
        norm_info = cluster_info['normInfo']
        k_features = cluster_info['features']
        cols = row.index.values[1:]

        for col in cols:
            row[col] = (row[col] - norm_info[col]['min']) / \
                (norm_info[col]['max'] - norm_info[col]['min'])

        feature = np.expand_dims(row.values[1:], axis=0)
        euc_chk = euc(feature, k_features)

        label = int(euc_chk.argmin())

        self.seed_zone.update_one({
            "trackId": row["trackId"]
        }, {
            "$set": {
                "label": label
            }
        })
