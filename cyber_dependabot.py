import os
import datetime
from collections import Counter
from typing import Iterator, Callable
from concurrent.futures import ThreadPoolExecutor
import logging

from addict import Dict
import requests

import storage
import config
from language_lookup import package_managers


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def post(path: str, body: str) -> requests.models.Response:
    """
    Adapter of `requests.post()`, supplying github credentials + JSON.
    """
    GITHUB_TOKEN = config.get_value("token")
    ROOT_URL = "https://api.dependabot.com"
    headers = {
        "Authorization": f"Personal {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.baptiste-preview+json",
    }
    full_path = ROOT_URL + path
    response = requests.post(full_path, headers=headers, json=body)

    logger.info(f"POST: path: {full_path}, response text: {response.text}")
    return response


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


def enable_all_dependabot() -> None:
    """
    Enables dependabot on every repo in repositories.json.
    """
    today = datetime.date.today().isoformat()
    repos = storage.read_json(f"{today}/data/repositories.json")

    repos = [Dict(r) for v in repos.values() for r in v]
    logger.info(f"Starting processing {len(repos)} repos...")
    results = tmap(enable_dependabot, repos)
    logger.info(Counter(results))


def lambda_handler(event, context):
    settings = config.load()

    if settings.aws_region:
        storage.set_region(config.get_value("aws_region"))

    if settings.storage:
        storage_options = config.get_value("storage")
        storage.set_options(storage_options)

    enable_vulnerability_alerts()


def enable_dependabot(repo: Dict) -> int:
    """
    Enabled dependabot on all whitelisted repos.
    """
    # https://github.com/dependabot/api-docs
    # https://api.github.com/repositories/1599151
    whitelist = ["cyber-security-tech-test"]
    blacklist = ["mapit"]
    repo_topics = get_topics(repo)

    if os.environ.get("DRY_RUN") == "true":
        return 200
    elif any(
        [
            repo.name in blacklist,
            "no-dependabot" in repo_topics,
            repo.isArchived,
            repo.name not in whitelist,
        ]
    ):
        logger.info(
            f"Leaving {repo.name}, no-dependabot value set or not in whitelist."
        )
        return 204
    elif repo.dependabotEnabledStatus:
        # This may need changing due to GitHub and dependabot API's not linking
        logger.info(f"Leaving {repo.name}, dependabot already enabled.")
        return 204
    else:
        if not repo.languages.nodes:
            return 422

        for lang in repo.languages.nodes:
            lang_package_manager = package_managers.get(lang.name)
            if not lang_package_manager:
                logger.info(
                    f"No package manager for lang: {lang.name}. Skipping {repo.name}"
                )
                continue

            body = {
                "repo-id": repo.databaseId,
                "update-schedule": "daily",
                "directory": "/",
                "account-id": "596977",
                "account-type": "org",
                "package-manager": lang_package_manager,
            }

            path = "/update_configs"

            r = post(path, body)
            logger.info(f"body: {body}")
            logger.info(f"repo: {repo.name}, POST: {r.status_code}, {r.text}")

            return r.status_code
