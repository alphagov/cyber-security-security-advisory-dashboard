import sys
import json
import time
import traceback
from collections import defaultdict, Counter
import warnings

import click
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

warnings.simplefilter("ignore", ArrowParseWarning)
app = Flask(__name__, static_url_path="/assets")


@app.cli.command("audit")
def cronable_vulnerability_audit():

    try:
        cursor = None
        last = False
        repository_list = []

        while not last:

            page = pgraph.query("all", nth=100, after=cursor)

            repository_list.extend(page.organization.repositories.nodes)
            last = not page.organization.repositories.pageInfo.hasNextPage
            cursor = page.organization.repositories.pageInfo.endCursor

        repo_count = len(repository_list)
        repositories_by_status = repository_summarizer.group_by_status(repository_list)
        status_counts = stats.count_types(repositories_by_status)

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
        }

        with open("output/repositories.json", "w") as repositories_file:
            repositories_file.write(json.dumps(repositories_by_status, indent=2))

        with open("output/home.json", "w") as route_file:
            route_file.write(json.dumps(template_data, indent=2))

        updated = True
    except Exception as err:
        updated = False
    return updated


@app.cli.command("activity_refs")
def activity_refs_audit():
    try:
        cursor = None
        last = False
        repository_list = []

        while not last:

            page = pgraph.query("refs", nth=50, after=cursor)

            repository_list.extend(page.organization.repositories.nodes)
            last = not page.organization.repositories.pageInfo.hasNextPage
            cursor = page.organization.repositories.pageInfo.endCursor


        total = len(repository_list)
        print(f"Repository list count: {total}", sys.stderr)

        repository_lookup = {repo.name: repo for repo in repository_list}

        total = len(repository_lookup.keys())
        print(f"Repository lookup count: {total}", sys.stderr)

        with open("output/activity_refs.json", "w") as repositories_file:
            repositories_file.write(json.dumps(repository_lookup, indent=2))

        updated = True
    except Exception as err:
        print("Failed to run activity GQL: " + str(err), sys.stderr)
        updated = False
    return updated


@app.cli.command("activity_prs")
def activity_prs_audit():
    try:
        cursor = None
        last = False
        repository_list = []

        while not last:

            page = pgraph.query("prs", nth=100, after=cursor)

            repository_list.extend(page.organization.repositories.nodes)
            last = not page.organization.repositories.pageInfo.hasNextPage
            cursor = page.organization.repositories.pageInfo.endCursor


        total = len(repository_list)
        print(f"Repository list count: {total}", sys.stderr)

        repository_lookup = {repo.name: repo for repo in repository_list}

        total = len(repository_lookup.keys())
        print(f"Repository lookup count: {total}", sys.stderr)

        with open("output/activity_prs.json", "w") as repositories_file:
            repositories_file.write(json.dumps(repository_lookup, indent=2))

        updated = True
    except Exception as err:
        print("Failed to run activity GQL: " + str(err), sys.stderr)
        updated = False
    return updated


@app.cli.command("dependabot-status")
@click.argument("org")
def dependabot_status(org):
    try:
        updated = False
        data = dependabot_api.get_repos_by_status(org)
        counts = stats.count_types(data)
        output = Dict()
        output.counts = counts
        output.repositories = data

        with open("output/dependabot_status.json", "w") as data_file:
            data_file.write(json.dumps(output, indent=2))
            updated = True
    except Exception:
        updated = False

    return updated


@app.cli.command("alert-status")
def resolve_alert_status():
    by_alert_status = defaultdict(list)
    with open("output/repositories.json", "r") as repositories_file:
        repositories = Dict(json.loads(repositories_file.read()))
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

    with open("output/alert_status.json", "w") as status_file:
        status_file.write(json.dumps(by_alert_status, indent=2))


@app.cli.command("build-routes")
def build_routes():
    by_alert_status = {"public": {}}
    with open("output/alert_status.json", "r") as status_file:
        alert_statuses = json.loads(status_file.read())

        for status, repos in alert_statuses.items():
            by_alert_status["public"][status] = len(repos)

    with open("output/count_alert_status.json", "w") as alert_counts_file:
        alert_counts_file.write(json.dumps(by_alert_status, indent=2))


@app.cli.command("repo-owners")
def repo_owners():
    list_owners = defaultdict(list)
    list_topics = defaultdict(list)
    with open("output/repositories.json", "r") as repositories_file:
        repositories = Dict(json.loads(repositories_file.read()))
    for repo in repositories["public"]:

        if repo.repositoryTopics.edges:
            for topics in repo.repositoryTopics.edges:
                list_owners[repo.name].append(topics.node.topic.name)
                list_topics[topics.node.topic.name].append(repo.name)
    with open("output/owners.json", "w") as owners_file:
        owners_file.write(json.dumps(list_owners, indent=2))

    with open("output/topics.json", "w") as topics_file:
        topics_file.write(json.dumps(list_topics, indent=2))


@app.cli.command("pr-status")
def pr_status():
    now = arrow.utcnow()
    with open("output/activity_prs.json", "r") as repositories_file:
        repositories = Dict(json.loads(repositories_file.read()))
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
                pr_final_status = f"Last pull request more than a year ago ({pr_status})"
            elif reference_date < now.shift(months=-1):
                pr_final_status = f"Last pull request more than a month ago ({pr_status})"
            elif reference_date < now.shift(weeks=-1):
                pr_final_status = f"Last pull request more than a week ago ({pr_status})"
            else:
                pr_final_status = f"Last pull request this week ({pr_status})"

        repo.pr_final_status = pr_final_status
    with open("output/activity_prs.json", "w") as repositories_file:
        repositories_file.write(json.dumps(repositories, indent=2))


@app.route("/")
def route_home():
    try:
        with open("output/home.json", "r") as home_template_data_file:
            repo_stats = json.loads(home_template_data_file.read())
        return render_template("summary.html", data=repo_stats)
    except FileNotFoundError as err:
        return render_template("error.html", message="Something went wrong.")


@app.route("/alert-status")
def route_alert_status():
    try:
        with open("output/count_alert_status.json", "r") as status_file:
            alert_status = json.loads(status_file.read())
        return render_template("alert_status.html", data=alert_status)
    except FileNotFoundError as err:
        return render_template("error.html", message="Something went wrong.")


@app.route("/repo-owners")
def route_owners():
    try:
        with open("output/topics.json", "r") as topics_file:
            topics = json.loads(topics_file.read())
        with open("teams.json", "r") as teams_file:
            teams = json.loads(teams_file.read())
        with open("output/activity_prs.json", "r") as repositories_file:
            repositories = Dict(json.loads(repositories_file.read()))

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
            "repo_owners.html",
            other_topics=other_topics,
            team_dict=team_dict,
            repositories=repositories,
        )
    except FileNotFoundError as err:
        return render_template("error.html", message="Something went wrong.")
