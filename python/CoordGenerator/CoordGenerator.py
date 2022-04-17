import math as mt
import numpy as np
from pymongo import MongoClient as mc
from bson import ObjectId

quadrant_check = [[1, 1], [1, -1], [-1, -1], [-1, 1]]


def get_quadrant(angle):
    chk_angle = [0, 90, 180, 270]
    if angle in chk_angle:
        return -1
    else:
        if angle < 90:
            return 0
        elif angle < 180:
            return 1
        elif angle < 270:
            return 2
        elif angle < 360:
            return 3


def check_guadrant(angle, point):
    if angle == 0:
        return [0, point[1]]
    elif angle == 90:
        return [point[1], 0]
    elif angle == 180:
        return [0, point[1] * -1]
    elif angle == 270:
        return [point[1] * -1, 0]


def get_coord(data):
    K = len(data)
    angles = np.array([x/float(K)*(2*mt.pi) for x in range(K)])
    non_zero_labels = data != 0

    x = angles[non_zero_labels]
    y = data[non_zero_labels]

    point = np.array([[x[i], y[i]] for i, _ in enumerate(x)])
    point = point.reshape(-1, 2)

    for idx, pt in enumerate(point):
        rad = pt[0]
        ang = rad / mt.pi * 180

        dis = pt[1]
        quad = get_quadrant(ang)
        if quad == -1:
            point[idx] = check_guadrant(ang, pt)
        else:
            if (ang < 90) or \
                    (ang > 180 and ang < 270):
                ang = 90 - (ang % 90)
            else:
                ang = ang % 90
            rad = ang * mt.pi / 180

            quad = quadrant_check[quad]
            x = dis * mt.cos(rad) * quad[0]  # get X
            y = dis * mt.sin(rad) * quad[1]  # get Y

            point[idx] = [x, y]

    return point.sum(axis=0)


class CoordGenerator:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).TestMuLetter
        self.seed_zone = self.conn.SeedZone
        self.mail = self.conn.mail
        self.mail_box = self.conn.MailBox
        self.cluster_zone = self.conn.ClusterZone

    def all_remake_coords(self):
        K = self.cluster_zone.find().sort("version", -1)[0]['K']

        mail_boxes = self.mail_box.find()
        for mail_box in mail_boxes:
            self.make_coords(mail_box["_id"])

    def make_coords(self, mail_box_id):
        K = self.cluster_zone.find().sort("version", -1)[0]['K']

        mail_box_id = ObjectId(mail_box_id) if type(
            mail_box_id) == str else mail_box_id
        mail_box = self.mail_box.find_one({
            "_id": mail_box_id
        })

        tracks = mail_box['tracks']
        label_cnt = np.zeros(K)
        for track in tracks:
            trackId = track['trackId']
            res = self.seed_zone.find_one({
                "trackId": trackId
            })
            label = res['label']
            label_cnt[label] += 1

        label_per = (label_cnt / label_cnt.sum()
                     * 100).round().astype("int")
        x, y = get_coord(label_per).astype("float64")
        self.mail_box.update_one({
            "_id": mail_box_id,
        }, {
            "$set": {
                "point": {
                    "x": x,
                    "y": y
                }
            }
        })
