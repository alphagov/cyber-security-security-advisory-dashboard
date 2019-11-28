import os
import datetime
from collections import Counter
from typing import Iterator, Callable
from concurrent.futures import ThreadPoolExecutor

from addict import Dict
import requests


import storage
import config

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

    repo_topics = get_topics(repo)
    repos_to_ignore = [
        repo.name in ["mapit"],
        "no-security-advisories" in repo_topics,
        repo.isArchived,
    ]

    if os.environ.get("DRY_RUN") == "true":
        return 200
    elif any(repos_to_ignore):
        logger.info(f"Leaving {repo.name}, no-security-advisories value set.")
        return 204
    elif repo.securityAdvisoriesEnabledStatus:
        logger.info(f"Leaving {repo.name}, security-advisories already enabled.")
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


# def update_config(repo):
#     # https://github.com/dependabot/api-docs
#     # https://api.github.com/repositories/1599151
#     if not repo.languages.nodes:
#         return

#     for lang in repo.languages.nodes:
#         if not (pm := package_managers.get(lang.name, None)):
#             print(f'Skipping {repo.name}, lang: {lang.name}')
#             continue

#         config = {
#             "repo-id": repo.databaseId,
#             "update-schedule": "daily",
#             "directory": "/",
#             "account-id": "596977",
#             "account-type": "org",
#             "package-manager": pm,
#         }

#         root_url = "https://api.dependabot.com"

#         headers = {
#             "Authorization": f'Personal {os.environ.get("SP_TOKEN", "")}',
#             "Accept": "application/vnd.github.baptiste-preview+json",
#         }
#         r = requests.post(root_url + "/update_configs", headers=headers, json=config)

#         print(f'repo: {repo.name}, config: {lang.name}, r: {r.text}')


enable_vulnerability_alerts()
