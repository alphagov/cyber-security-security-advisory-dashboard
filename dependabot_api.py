import os
import json
import requests
from addict import Dict


import config


def get(path):
    root_url = "https://api.dependabot.com"
    headers = {"Authorization": "Personal %s" % config.get_value("token")}

    url = root_url + path
    response = requests.get(url, headers=headers)
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
