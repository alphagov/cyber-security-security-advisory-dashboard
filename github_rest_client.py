import os
import requests
import json


ROOT_URL = "https://api.github.com"
HEADERS = {
    "Authorization": "token %s" % os.environ["TOKEN"],
    "Accept": "application/vnd.github.dorian-preview+json",
}


def get(path):
    url = ROOT_URL + path
    response = requests.get(url, headers=HEADERS)
    return response
