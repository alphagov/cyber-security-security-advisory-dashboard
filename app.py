import os
import sys
import json
import time
import datetime
import traceback
from collections import defaultdict, Counter
import warnings

from flask import Flask
from flask import render_template
from addict import Dict
import arrow
from arrow.factory import ArrowParseWarning

import pgraph
import repository_summarizer
import vulnerability_summarizer
import stats
import dependabot_api
import github_rest_client
import config
import storage


warnings.simplefilter("ignore", ArrowParseWarning)
app = Flask(__name__, static_url_path="/assets")
settings = config.load()

if settings.aws_region:
    storage.set_region(config.get_value("aws_region"))

if settings.storage:
    storage_options = config.get_value("storage")
    storage.set_options(storage_options)


@app.template_filter('iso_date')
def filter_iso_date(iso_date):
    """Convert a string to all caps."""
    parsed = arrow.get(iso_date,"YYYY-MM-DD")
    return parsed.format("DD/MM/YYYY")


def get_history():
    history_file = "all/data/history.json"

    default = Dict({
        "current": None,
        "alltime": {}
    })
    history = storage.read_json(history_file, default=default)

    print(str(history), sys.stderr)

    return history


def update_history(history):
    return storage.save_json("all/data/history.json", history)


def get_current_audit():
    try:
        history = get_history()
        current = history.current
    except FileNotFoundError:
        current = datetime.date.today().isoformat()
    return current


@app.cli.command("audit")
def cronable_vulnerability_audit():
    today = datetime.date.today().isoformat()

    # set status to inprogress in history
    history = get_history()
    history.alltime[today] = "in progress"
    update_history(history)

    # retrieve data from apis
    org = config.get_value("github_org")
    # todo - set maintenance mode
    repository_status = get_github_repositories_and_classify_by_status(org, today)
    refs_status = get_github_activity_refs_audit(org, today)
    prs_status = get_github_activity_prs_audit(org, today)
    dbot_status = get_dependabot_status(org, today)

    # analyse raw data
    ownership_status = analyse_repo_ownership(today)
    pr_status = analyse_pull_request_status(today)

    # build page template data
    build_route_data(today)

    # update current audit in history
    history.current = today
    history.alltime[today] = "complete"
    update_history(history)
    # todo - set enabled mode
    return True


@app.cli.command("alert-status")
def get_github_resolve_alert_status():
    today = datetime.date.today().isoformat()
    by_alert_status = defaultdict(list)

    repositories = storage.read_json(f"{today}/data/repositories.json")
    for repo in repositories["public"]:
        response = github_rest_client.get(
            f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts"
        )
        alerts_enabled = response.status_code == 204
        vulnerable = repo.vulnerabilityAlerts.edges

        if vulnerable:
            status = "vulnerable"
        elif alerts_enabled:
            status = "clean"
        else:
            status = "disabled"

        by_alert_status[status].append(repo)
        time.sleep(1)

    status = storage.save_json("all/data/alert_status.json", by_alert_status)
    return status


def get_github_repositories_and_classify_by_status(org, today):
    try:
        cursor = None
        last = False
        repository_list = []

        while not last:

            page = pgraph.query("all", org=org, nth=100, after=cursor)

            repository_list.extend(page.organization.repositories.nodes)
            last = not page.organization.repositories.pageInfo.hasNextPage
            cursor = page.organization.repositories.pageInfo.endCursor

        repositories_by_status = repository_summarizer.group_by_status(repository_list)
        save_to = f"{today}/data/repositories.json"
        updated = storage.save_json(save_to, repositories_by_status)

    except Exception as err:
        print(str(err), sys.stderr)
        updated = False
    return updated


def get_github_activity_refs_audit(org, today):
    try:
        cursor = None
        last = False
        repository_list = []

        while not last:

            page = pgraph.query("refs", org=org, nth=50, after=cursor)

            repository_list.extend(page.organization.repositories.nodes)
            last = not page.organization.repositories.pageInfo.hasNextPage
            cursor = page.organization.repositories.pageInfo.endCursor

        total = len(repository_list)
        print(f"Repository list count: {total}", sys.stderr)

        repository_lookup = {repo.name: repo for repo in repository_list}

        total = len(repository_lookup.keys())
        print(f"Repository lookup count: {total}", sys.stderr)

        updated = storage.save_json(f"{today}/data/activity_refs.json", repository_lookup)

    except Exception as err:
        print("Failed to run activity GQL: " + str(err), sys.stderr)
        updated = False
    return updated


def get_github_activity_prs_audit(org, today):
    try:
        cursor = None
        last = False
        repository_list = []

        while not last:

            page = pgraph.query("prs", org=org, nth=100, after=cursor)

            repository_list.extend(page.organization.repositories.nodes)
            last = not page.organization.repositories.pageInfo.hasNextPage
            cursor = page.organization.repositories.pageInfo.endCursor

        total = len(repository_list)
        print(f"Repository list count: {total}", sys.stderr)

        repository_lookup = {repo.name: repo for repo in repository_list}

        total = len(repository_lookup.keys())
        print(f"Repository lookup count: {total}", sys.stderr)

        updated = storage.save_json(f"{today}/data/activity_prs.json", repository_lookup)

    except Exception as err:
        print("Failed to run activity GQL: " + str(err), sys.stderr)
        updated = False
    return updated


def get_dependabot_status(org, today):
    try:
        updated = False
        data = dependabot_api.get_repos_by_status(org)
        counts = stats.count_types(data)
        output = Dict()
        output.counts = counts
        output.repositories = data

        updated = storage.save_json(f"{today}/data/dependabot_status.json", output)
    except Exception:
        updated = False

    return updated


def analyse_repo_ownership(today):
    list_owners = defaultdict(list)
    list_topics = defaultdict(list)
    repositories = storage.read_json(f"{today}/data/repositories.json")
    for repo in repositories["public"]:

        if repo.repositoryTopics.edges:
            for topics in repo.repositoryTopics.edges:
                list_owners[repo.name].append(topics.node.topic.name)
                list_topics[topics.node.topic.name].append(repo.name)

    owner_status = storage.save_json(f"{today}/data/owners.json", list_owners)
    topic_status = storage.save_json(f"{today}/data/topics.json", list_topics)
    return owner_status and topic_status


def analyse_pull_request_status(today):
    now = arrow.utcnow()
    repositories = storage.read_json(f"{today}/data/activity_prs.json")
    for repo_name, repo in repositories.items():

        pr_final_status = "No pull requests in this repository"

        if repo.pullRequests.edges:
            node = repo.pullRequests.edges[0].node

            if node.merged:
                reference_date = arrow.get(node.mergedAt)
                pr_status = "merged"
            elif node.closed:
                reference_date = arrow.get(node.closedAt)
                pr_status = "closed"
            else:
                reference_date = arrow.get(node.createdAt)
                pr_status = "open"

            if reference_date < now.shift(years=-1):
                pr_final_status = (
                    f"Last pull request more than a year ago ({pr_status})"
                )
            elif reference_date < now.shift(months=-1):
                pr_final_status = (
                    f"Last pull request more than a month ago ({pr_status})"
                )
            elif reference_date < now.shift(weeks=-1):
                pr_final_status = (
                    f"Last pull request more than a week ago ({pr_status})"
                )
            else:
                pr_final_status = f"Last pull request this week ({pr_status})"

        repo.pr_final_status = pr_final_status

    status = storage.save_json(f"{today}/data/activity_prs.json", repositories)
    return status


def build_route_data(today):
    route_data_overview_repositories_by_status(today)
    route_data_overview_alert_status(today)


def route_data_overview_repositories_by_status(today):
    repositories_by_status = storage.read_json(f"{today}/data/repositories.json")
    status_counts = stats.count_types(repositories_by_status)
    repo_count = sum(status_counts.values())

    vulnerable_list = [
        node
        for node in repositories_by_status.public
        if node.vulnerabilityAlerts.edges
    ]
    vulnerable_count = len(vulnerable_list)
    vulnerable_by_severity = vulnerability_summarizer.group_by_severity(
        vulnerable_list
    )
    severity_counts = stats.count_types(vulnerable_by_severity)
    severities = vulnerability_summarizer.SEVERITIES

    template_data = {
        "repositories": {"all": repo_count, "by_status": status_counts},
        "vulnerable": {
            "severities": severities,
            "all": vulnerable_count,
            "by_severity": severity_counts,
            "repositories": vulnerable_by_severity,
        },
        "updated": today
    }

    home_status = storage.save_json(f"{today}/routes/overview.json", template_data)
    return home_status


def route_data_overview_alert_status(today):

    by_alert_status = {"public": {}}
    alert_statuses = storage.read_json(f"all/data/alert_status.json")
    for status, repos in alert_statuses.items():
        by_alert_status["public"][status] = len(repos)

    status = storage.save_json(f"{today}/routes/count_alert_status.json", by_alert_status)
    return status


def get_header():
    org_name = config.get_value("github_org").title()
    return {
        "app_name": f"{org_name} Audit"
    }


def get_error_data(message):
    return {
        "header": get_header(),
        "content": {
            "title": message
        },
        "message": message
    }


@app.route("/")
def route_home():
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()

        content = {
            "title": "Introduction",
            "org": config.get_value("github_org")
        }
        footer = {
            "updated": today
        }
        return render_template("pages/home.html",
                               header=get_header(),
                               content=content,
                               footer=footer)
    except FileNotFoundError as err:
        return render_template("pages/error.html", **get_error_data("Something went wrong."))


@app.route("/overview")
def route_overview():
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        content = {
            "title": "Overview"
        }
        footer = {
            "updated": today
        }
        repo_stats = storage.read_json(f"{today}/routes/overview.json")
        return render_template("pages/overview.html",
                               header=get_header(),
                               content=content,
                               footer=footer,
                               data=repo_stats)
    except FileNotFoundError as err:
        return render_template("pages/error.html", **get_error_data("Something went wrong."))


@app.route("/overview/repository-status")
def route_overview_repository_status():
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        content = {
            "title": "Overview - Repository status"
        }
        footer = {
            "updated": today
        }
        repo_stats = storage.read_json(f"{today}/routes/overview.json")
        return render_template("pages/overview_repository_status.html",
                               header=get_header(),
                               content=content,
                               footer=footer,
                               data=repo_stats)
    except FileNotFoundError as err:
        return render_template("pages/error.html", **get_error_data("Something went wrong."))


@app.route("/overview/repository-vulnerabilities")
def route_overview_repository_vulnerabilities():
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        content = {
            "title": "Overview - Repository vulnerabilities",
            "org": config.get_value("github_org")
        }
        footer = {
            "updated": today
        }
        repo_stats = storage.read_json(f"{today}/routes/overview.json")
        return render_template("pages/overview_repository_vulnerabilities.html",
                               header=get_header(),
                               content=content,
                               footer=footer,
                               data=repo_stats)
    except FileNotFoundError as err:
        return render_template("pages/error.html", **get_error_data("Something went wrong."))


@app.route("/overview/alert-status")
def route_alert_status():
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        content = {
            "title": "Overview - Alert status"
        }
        footer = {
            "updated": today
        }

        alert_status = storage.read_json(f"{today}/routes/count_alert_status.json")
        return render_template("pages/overview_alert_status.html",
                               header=get_header(),
                               content=content,
                               footer=footer,
                               data=alert_status)
    except FileNotFoundError as err:
        return render_template("pages/error.html", **get_error_data("Something went wrong."))


@app.route("/by-repository")
def route_owners():
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        content = {
            "title": "By repository"
        }
        footer = {
            "updated": today
        }
        topics = storage.read_json(f"{today}/data/topics.json")
        repositories = storage.read_json(f"{today}/data/activity_prs.json")

        # This one can't currently use storage because it's
        # outside the output folder and not written to S3.
        with open("teams.json", "r") as teams_file:
            teams = json.loads(teams_file.read())

        team_dict = defaultdict(set)
        for team in teams.keys():
            for repos in topics[team]:
                team_dict[team].add(repos)

        other_topics = {
            topic_name: topics[topic_name]
            for topic_name in set(topics.keys()) - set(teams.keys())
        }

        total = len([*repositories.keys()])
        print(f"Count of repos in lookup: {total}", sys.stderr)

        return render_template(
            "pages/repo_owners.html",
            header=get_header(),
            content=content,
            footer=footer,
            other_topics=other_topics,
            team_dict=team_dict,
            repositories=repositories,
        )
    except FileNotFoundError as err:
        return render_template("pages/error.html", **get_error_data("Something went wrong."))
