import json
import requests as req
import base64


def get_token(self):
    with open("auth.json") as json_file:
        json_data = json.load(json_file)

    client_data = "{}:{}".format(
        json_data['CLIENT_ID'],
        json_data['CLIENT_SECRET']
    )
    authorization = "Basic " + \
        base64.b64encode(client_data.encode('ascii')).decode("ascii")

    res = req.post("https://accounts.spotify.com/api/token",
                   data={
                       "grant_type": 'client_credentials'
                   },
                   headers={
                       'Authorization': authorization
                   })

    self.token = res.json()['access_token']
