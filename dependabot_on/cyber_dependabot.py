import os
import datetime
import json
import logging
from multiprocessing import Pool
from collections import Counter

from addict import Dict
import requests

logging.basicConfig(level=logging.INFO)
ROOT_URL = "https://api.github.com"


def pmap(f, collection, size=10):
    """
    Applies `f` in parallel over `collection`.
    Pool `size` has a sensible default of 10.
    """
    with Pool(size) as p:
        return p.map(f, collection)


def put(path, data=None):
    """
    Adapter of `requests.put()`, supplying github credentials.
    """
    headers = {
        "Authorization": f'token {os.environ.get("TOKEN", "")}',
        "Accept": "application/vnd.github.dorian-preview+json",
    }
    return requests.put(f"{ROOT_URL}{path}", headers=headers)


def enable_alert(repo):
    """
    Enable vulnerability alerts on a single repo.
    """
    r = put(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
    logging.info(f"repo: {repo.name}, PUT: {r.status_code}, {r.text}")
    return r.status_code


def enable_vulnerability_alerts():
    """
    Enables vulnerability alerts on every repo in repositories.json.
    """
    today = datetime.date.today().isoformat()
    with open(f"output/{today}/data/repositories.json", "r") as f:
        repos = json.load(f)

    repos = [Dict(r) for v in repos.values() for r in v]
    logging.info(f"Starting processing {len(repos)} repos...")
    results = pmap(enable_alert, repos)
    logging.info(Counter(results))


enable_vulnerability_alerts()
