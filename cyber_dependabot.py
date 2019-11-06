import os
import datetime
import logging
from collections import Counter
from typing import Iterator, Callable
from concurrent.futures import ThreadPoolExecutor

from addict import Dict
import requests


import storage
import config


logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger()


def put(path: str) -> requests.models.Response:
    """
    Adapter of `requests.put()`, supplying github credentials.
    """
    GITHUB_TOKEN = config.get_value("token")
    ROOT_URL = "https://api.github.com"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.dorian-preview+json",
    }
    return requests.put(f"{ROOT_URL}{path}", headers=headers)


def get_topics(repo: Dict) -> list:
    repo_topics = []
    if repo.repositoryTopics:
        repo_topics = [
            topic_edge.node.topic.name for topic_edge in repo.repositoryTopics.edges
        ]

    return repo_topics


def enable_alert(repo: Dict) -> int:
    """
    Enable vulnerability alerts on a single repo.
    """

    no_security_advisories = ["mapit"]
    repo_topics = get_topics(repo)

    if os.environ.get("DRY_RUN") == "true":
        return 200
    elif repo.name in no_security_advisories:
        logger.info(f"Leaving {repo.name}, no-security-advisories value set.")
        return 204
    elif "no-security-advisories" in repo_topics:
        logger.info(f"Leaving {repo.name}, no-security-advisories value set.")
        return 204
    else:
        r = put(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
        logger.info(f"repo: {repo.name}, PUT: {r.status_code}, {r.text}")
        return r.status_code


def tmap(f: Callable, iterable: Iterator, size: int = 10) -> list:
    """
    Applies `f` in parallel Threads over `collection`.
    Pool `size` has a sensible default of 10.
    """
    with ThreadPoolExecutor(max_workers=size) as executor:
        return list(executor.map(f, iterable))


def enable_vulnerability_alerts() -> None:
    """
    Enables vulnerability alerts on every repo in repositories.json.
    """
    today = datetime.date.today().isoformat()
    repos = storage.read_json(f"{today}/data/repositories.json")

    repos = [Dict(r) for v in repos.values() for r in v]
    logger.info(f"Starting processing {len(repos)} repos...")
    results = tmap(enable_alert, repos)
    logger.info(Counter(results))


def lambda_handler(event, context):
    settings = config.load()

    if settings.aws_region:
        storage.set_region(config.get_value("aws_region"))

    if settings.storage:
        storage_options = config.get_value("storage")
        storage.set_options(storage_options)

    enable_vulnerability_alerts()
