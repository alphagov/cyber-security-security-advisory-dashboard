import sys
import json
import time
import traceback
from collections import defaultdict
from flask import Flask
from flask import render_template
from addict import Dict
import pgraph
import repository_summarizer
import vulnerability_summarizer
import stats
import github_rest_client


app = Flask(__name__, static_url_path="/assets")


@app.cli.command("audit")
def cronable_audit():

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


@app.cli.command("alert-status")
def resolve_alert_status():
    by_alert_status = defaultdict(list)
    with open("output/repositories.json", "r") as repositories_file:
        repositories = Dict(json.loads(repositories_file.read()))
        for repo in repositories["public"]:
            response = github_rest_client.get(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
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
    by_alert_status = {
        "public": {}
    }
    with open("output/alert_status.json", "r") as status_file:
        alert_statuses = json.loads(status_file.read())

        for status,repos in alert_statuses.items():
            by_alert_status["public"][status] = len(repos)

    with open("output/count_alert_status.json", "w") as alert_counts_file:
        alert_counts_file.write(json.dumps(by_alert_status, indent=2))


@app.route("/")
def route_home():
    try:
        with open("output/home.json", "r") as template_file:
            template_data = json.loads(template_file.read())
            return render_template("summary.html", data=template_data)
    except FileNotFoundError as err:
        return render_template("error.html", message="Something went wrong.")


@app.route("/alert-status")
def route_alert_status():
    try:
        with open("output/count_alert_status.json", "r") as template_file:
            template_data = json.loads(template_file.read())
            return render_template("alert_status.html", data=template_data)
    except FileNotFoundError as err:
        return render_template("error.html", message="Something went wrong.")
