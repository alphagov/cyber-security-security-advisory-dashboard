import requests
import os
import json
from pprint import pprint
from addict import Dict
import logging
from language_lookup import package_managers


ROOT_URL = "https://api.github.com"

def get(path):
    headers = {
        "Authorization": f'token {os.environ.get("SP_TOKEN", "")}',
        "Accept": "application/vnd.github.dorian-preview+json",
    }
    return requests.get(f"{ROOT_URL}{path}", headers=headers)


def put(path, data=None):
    headers = {
        "Authorization": f'token {os.environ.get("SP_TOKEN", "")}',
        "Accept": "application/vnd.github.dorian-preview+json",
    }
    return requests.put(f"{ROOT_URL}{path}", headers=headers)


def enable_vulnerability_alerts():
    with open("repositories.json", "r") as f:
        repos = json.load(f)

    repos = [Dict(r) for v in repos.values() for r in v]

    logging.debug(set([lang.name for repo in repos for lang in repo.languages.nodes]))

    for repo in repos:

        if "cyber" in repo.name or "cst" in repo.name or "csw" in repo.name:
            update_config(repo)

            r = get(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
            print(f"repo: {repo.name}, GET: {r.status_code}, {r.text}")

            r = put(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
            print(f"repo: {repo.name}, PUT: {r.status_code}, {r.text}")

            r = get(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
            print(f"repo: {repo.name}, GET: {r.status_code}, {r.text}")


def update_config(repo):
    # https://github.com/dependabot/api-docs
    # https://api.github.com/repositories/1599151
    if not repo.languages.nodes:
        return

    for lang in repo.languages.nodes:
        if not (pm := package_managers.get(lang.name, None)):
            print(f'Skipping {repo.name}, lang: {lang.name}')
            continue

        config = {
            "repo-id": repo.databaseId,
            "update-schedule": "daily",
            "directory": "/",
            "account-id": "596977",
            "account-type": "org",
            "package-manager": pm,
        }

        root_url = "https://api.dependabot.com"

        headers = {
            "Authorization": f'Personal {os.environ.get("SP_TOKEN", "")}',
            "Accept": "application/vnd.github.baptiste-preview+json",
        }
        r = requests.post(root_url + "/update_configs", headers=headers, json=config)

        print(f'repo: {repo.name}, config: {lang.name}, r: {r.text}')


enable_vulnerability_alerts()
