import requests
import os
import json
from addict import Dict
import logging


ROOT_URL = "https://api.github.com"


def put(path, data=None):
    """
    Adapter of `requests.put()`, supplying github credentials.
    """
    headers = {
        "Authorization": f'token {os.environ.get("TOKEN", "")}',
        "Accept": "application/vnd.github.dorian-preview+json",
    }
    return requests.put(f"{ROOT_URL}{path}", headers=headers)


def enable_vulnerability_alerts():
    """
    Enables vulnerability alerts on every repo in repositories.json.
    """
    with open("repositories.json", "r") as f:
        repos = json.load(f)

    repos = [Dict(r) for v in repos.values() for r in v]

    for repo in repos:
        r = put(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
        print(f"repo: {repo.name}, PUT: {r.status_code}, {r.text}")


enable_vulnerability_alerts()
