import os
import requests
import json


import config


ROOT_URL = "https://api.github.com"
HEADERS = {
    "Authorization": "token %s" % config.get_value("token"),
    "Accept": "application/vnd.github.dorian-preview+json",
}


def get(path):
    url = ROOT_URL + path
    response = requests.get(url, headers=HEADERS)
    return response
