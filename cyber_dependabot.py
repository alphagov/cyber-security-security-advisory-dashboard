import os
import datetime
import logging
from multiprocessing import Pool
from collections import Counter
from typing import Iterator, Callable

from addict import Dict
import requests

import storage
import config


def pmap(f: Callable, collection: Iterator, size: int = 10) -> list:
    """
    Applies `f` in parallel over `collection`.
    Pool `size` has a sensible default of 10.
    """
    with Pool(size) as p:
        return p.map(f, collection)


def put(path: str) -> requests.models.Response:
    """
    Adapter of `requests.put()`, supplying github credentials.
    """
    ENCRYPTED_GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
    DECRYPTED_GITHUB_TOKEN = boto3.client('kms').decrypt(
        CiphertextBlob=b64decode(ENCRYPTED_GITHUB_TOKEN)
    )['Plaintext']
    ROOT_URL = "https://api.github.com"
    headers = {
        "Authorization": f'token {DECRYPTED_GITHUB_TOKEN}',
        "Accept": "application/vnd.github.dorian-preview+json",
    }
    return requests.put(f"{ROOT_URL}{path}", headers=headers)


def enable_alert(repo: Dict) -> int:
    """
    Enable vulnerability alerts on a single repo.
    """

    if os.environ.get("DRY_RUN") == "true":
        return 200
    else:
        r = put(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
        logging.info(f"repo: {repo.name}, PUT: {r.status_code}, {r.text}")
        return r.status_code


def enable_vulnerability_alerts() -> None:
    """
    Enables vulnerability alerts on every repo in repositories.json.
    """
    today = datetime.date.today().isoformat()
    repos = storage.read_json(f"{today}/data/repositories.json")

    repos = [Dict(r) for v in repos.values() for r in v]
    logging.info(f"Starting processing {len(repos)} repos...")
    results = pmap(enable_alert, repos)
    logging.info(Counter(results))


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
        level=logging.INFO,
    )

    settings = config.load()

    if settings.aws_region:
        storage.set_region(config.get_value("aws_region"))

    if settings.storage:
        storage_options = config.get_value("storage")
        storage.set_options(storage_options)

    logging.basicConfig(level=logging.INFO)

    enable_vulnerability_alerts()
