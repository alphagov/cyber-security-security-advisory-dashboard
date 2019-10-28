import os
import requests
import json


import config


def get(path):
    root_url = "https://api.github.com"
    headers = {
        "Authorization": "token %s" % config.get_value("token"),
        "Accept": "application/vnd.github.dorian-preview+json",
    }

    url = root_url + path
    response = requests.get(url, headers=headers)
    return response
