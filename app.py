import os
import json
import click
from flask import Flask
from flask import render_template

import pgraph
import repository_summarizer
import vulnerability_summarizer
import stats


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
        repositories_by_status = repository_summarizer.collate_by_status(
            repository_list
        )
        status_counts = stats.count_types(repositories_by_status)

        vulnerable_list = [
            node
            for node in repositories_by_status.public
            if node.vulnerabilityAlerts.edges
        ]
        vulnerable_count = len(vulnerable_list)
        vulnerable_by_severity = vulnerability_summarizer.collate_by_severity(
            vulnerable_list
        )
        severity_counts = stats.count_types(vulnerable_by_severity)
        severities = vulnerability_summarizer.get_severity_order()

        template_data = {
            "repositories": {"all": repo_count, "by_status": status_counts},
            "vulnerable": {
                "severities": severities,
                "all": vulnerable_count,
                "by_severity": severity_counts,
                "repositories": vulnerable_by_severity,
            },
        }

        with open("output/home.json", "w") as file:
            file.write(json.dumps(template_data, indent=2))

        updated = True
    except Exception as err:
        updated = False
    return updated


@app.route("/")
def route_home():
    try:
        with open("output/home.json", "r") as file:
            template_data = json.loads(file.read())
            return render_template("summary.html", data=template_data)
    except FileNotFoundError as err:
        pass  # handle error
