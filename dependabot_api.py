import os
import json
import requests
from addict import Dict


import config


ROOT_URL = "https://api.dependabot.com"


HEADERS = {"Authorization": "Personal %s" % config.get_value("token")}


def get(path):
    url = ROOT_URL + path
    response = requests.get(url, headers=HEADERS)
    return response


def get_parsed(path):
    response = get(path)
    body = Dict(json.loads(response.text))
    return body.data


def get_repos_by_status(org):
    accounts = get_parsed("/accounts")
    states = ["active", "inactive"]
    repositories = {}
    for account in accounts:
        if account.attributes["github-login"] == org:
            for state in states:
                repositories[state] = get_parsed(
                    f"/repos?account-id={account.id}&account-type=org&installation-state={state}"
                )

    return repositories
