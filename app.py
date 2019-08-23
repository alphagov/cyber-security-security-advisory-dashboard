from flask import Flask
from flask import render_template

import pgraph

app = Flask(__name__, static_url_path="/assets")


@app.route("/")
def hello_world():

    cursor = None
    last = False
    vulnerability_list = []
    repository_list = []

    while not last:

        if cursor:
            page = pgraph.query("all", nth=100, after=cursor)
        else:
            page = pgraph.query("all", nth=100)

        repository_list.extend(page.organization.repositories.nodes)
        # page = repositories.organization.repositories.nodes
        last = not page.organization.repositories.pageInfo.hasNextPage
        cursor = page.organization.repositories.pageInfo.endCursor

    # results = pgraph.query("all", nth=100)
    vulnerability_list = [
        node for node in repository_list if node.vulnerabilityAlerts.edges
    ]

    repo_count = len(repository_list)
    vulnerable_count = len(vulnerability_list)

    template_data = {"repo_count": repo_count, "vulnerable_count": vulnerable_count}

    return render_template("layout.html", data=template_data)
