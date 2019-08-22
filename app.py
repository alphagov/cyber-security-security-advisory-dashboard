from flask import Flask
from flask import render_template

import pgraph

app = Flask(__name__, static_url_path="/assets")


@app.route("/")
def hello_world():

    results = pgraph.query("all", nth=100)

    vulnerable_nodes = [
        node
        for node in results.organization.repositories.nodes
        if node.vulnerabilityAlerts.edges
    ]
    return render_template("layout.html", data=vulnerable_nodes)
