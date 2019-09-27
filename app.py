import os
import sys
import json
import datetime
from collections import defaultdict
import warnings
import logging as log

from flask import Flask
from flask import render_template, request
from addict import Dict
import arrow
from arrow.factory import ArrowParseWarning

import config
import storage
import errors


warnings.simplefilter("ignore", ArrowParseWarning)
app = Flask(__name__, static_url_path="/assets")
settings = config.load()
log.error("Config loaded for env: " + os.environ["FLASK_ENV"])

if settings.aws_region:
    log.error("Setting AWS region to: " + config.get_value("aws_region"))
    storage.set_region(config.get_value("aws_region"))

if settings.storage:
    storage_options = config.get_value("storage")
    storage.set_options(storage_options)


@app.template_filter("iso_date")
def filter_iso_date(iso_date):
    """Convert a string to all caps."""
    parsed = arrow.get(iso_date, "YYYY-MM-DD")
    return parsed.format("DD/MM/YYYY")


@app.template_filter("abbreviate")
def filter_abbreviate(word):
    lowercase_word = word.lower()
    abbrevs = {
        "critical": "crit",
        "moderate": "mod",
        "medium": "med",
        "dependabot": "dbot",
        "advisory": "adv",
    }
    return abbrevs[lowercase_word] if (lowercase_word in abbrevs) else word


def get_header():
    org = config.get_value("github_org")
    org_name = org.title()
    return {"org": org, "app_name": f"{org_name} Audit", "route": request.path}


def get_error_data(message):
    log.error(message)
    return {"header": get_header(), "content": {"title": message}, "message": message}


def get_current_audit():
    try:
        history = get_history()
        current = history.current
        log.info(f"Found current: {current}")
    except FileNotFoundError:
        current = datetime.date.today().isoformat()
        log.info(f"Missing current: {current} (assume today)")
    return current


def get_history():
    history_file = "all/data/history.json"

    default = Dict({"current": None, "alltime": {}})
    history = storage.read_json(history_file, default=default)

    # print(str(history), sys.stderr)
    log.error(json.dumps(history))

    return history


@app.route("/")
def route_home():
    log.error("Route: /")
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        log.error(f"Getting audit results for: {today}")

        content = {"title": "Introduction", "org": config.get_value("github_org")}
        footer = {"updated": today}
        page = render_template(
            "pages/home.html", header=get_header(), content=content, footer=footer
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )

    return page


@app.route("/how-to")
def route_how_to():
    log.error("Route: /how-to")
    try:
        current = get_current_audit()
        content = {"title": "How to"}
        footer = {"updated": current}
        page = render_template(
            "pages/how_to.html", header=get_header(), content=content, footer=footer
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page =  render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )
    return page


@app.route("/how-to/enable-dependabot")
def route_how_to_enable_dependabot():
    log.error("Route: /how-to/enable-dependabot")
    try:
        current = get_current_audit()
        content = {"title": "How to enable dependabot"}
        footer = {"updated": current}
        page = render_template(
            "pages/how_to_enable_dependabot.html",
            header=get_header(),
            content=content,
            footer=footer,
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )
    return page


@app.route("/how-to/enable-security-advisories")
def route_how_to_enable_security_advisories():
    log.error("Route: /how-to/enable-security-advisories")
    try:
        current = get_current_audit()
        content = {"title": "How to enable security advisories"}
        footer = {"updated": current}
        page = render_template(
            "pages/how_to_enable_security_advisories.html",
            header=get_header(),
            content=content,
            footer=footer,
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )
    return page


@app.route("/overview")
def route_overview():
    log.error("Route: /overview")
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        content = {"title": "Overview"}
        footer = {"updated": today}
        repo_stats = storage.read_json(f"{today}/routes/overview.json")
        page = render_template(
            "pages/overview.html",
            header=get_header(),
            content=content,
            footer=footer,
            data=repo_stats,
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )

    return page


@app.route("/overview/activity")
def route_overview_activity():
    log.error("Route: /overview/activity")
    try:
        current = get_current_audit()
        template_data = storage.read_json(f"{current}/routes/overview_activity.json")
        log.error(f"Template data says footer updated: {template_data.footer.updated}")
        page = render_template(
            "pages/overview_activity.html",
            header=get_header(),
            **template_data
        )
        log.error(f"Rendered page starts: {page[0:10]} and is {len(page)} characters")
    except Exception as err:
        print(str(err))
        log.error(errors.get_log_event())
        page = render_template("pages/error.html", **get_error_data("File not found."))

    log.error("Returning page content: /overview/activity")
    return page


@app.route("/overview/monitoring-status")
def route_overview_monitoring_status():
    log.error("Route: /overview/monitoring-status")
    try:
        current = get_current_audit()
        template_data = storage.read_json(
            f"{current}/routes/overview_monitoring_status.json"
        )
        page = render_template(
            "pages/overview_monitoring_status.html",
            header=get_header(),
            **template_data,
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )
    return page


@app.route("/overview/repository-status")
def route_overview_repository_status():
    log.error("Route: /overview/repository-status")
    try:
        current = get_current_audit()
        template_data = storage.read_json(
            f"{current}/routes/overview_repositories_by_status.json"
        )
        page = render_template(
            "pages/overview_repository_status.html",
            header=get_header(),
            **template_data,
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )
    return page


@app.route("/overview/vulnerable-repositories")
def route_overview_vulnerable_repositories():
    log.error("Route: /overview/vulnerable-repositories")
    try:
        current = get_current_audit()
        template_data = storage.read_json(
            f"{current}/routes/overview_vulnerable_repositories.json"
        )
        page = render_template(
            "pages/overview_vulnerable_repositories.html",
            header=get_header(),
            **template_data,
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template("pages/error.html", **get_error_data("File not found."))
    return page


@app.route("/by-repository")
def route_by_repository():
    log.error("Route: /by-repository")
    try:
        # today = datetime.date.today().isoformat()
        today = get_current_audit()
        content = {"title": "By repository"}
        footer = {"updated": today}
        topics = storage.read_json(f"{today}/data/topics.json")
        raw_repositories = storage.read_json(f"{today}/data/repositories.json")
        repositories = {repo.name: repo for repo in raw_repositories["public"]}

        team_dict = defaultdict(list)
        for repo_name, repo in repositories.items():
            team_dict[repo.team].append(repo_name)

        teams = list(team_dict.keys())
        teams.sort()

        other_topics = {
            topic_name: topics[topic_name] for topic_name in set(topics.keys())
        }

        total = len([*repositories.keys()])
        print(f"Count of repos in lookup: {total}", sys.stderr)

        page = render_template(
            "pages/by_repository.html",
            header=get_header(),
            content=content,
            footer=footer,
            other_topics=other_topics,
            teams=teams,
            team_dict=team_dict,
            repositories=repositories,
        )
    except Exception as err:
        print(err.message)
        log.error(errors.get_log_event())
        page = render_template(
            "pages/error.html", **get_error_data("Something went wrong.")
        )
    return page


@app.route("/healthy")
def route_healthcheck():
    """An unauthenticated route for health checks
    """
    # log.msg("gtg")
    log.error("Route: /healthy")
    response = "OK"
    return response
