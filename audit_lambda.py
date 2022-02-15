import json
import datetime
import logging as log
from collections import defaultdict

from addict import Dict
import click

import arrow
import pgraph
import repository_summarizer
import vulnerability_summarizer
import stats
import dependabot_api
import github_rest_client
import config
import storage
import errors
from splunk import Splunk

from concurrent.futures import ThreadPoolExecutor

log.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s", level=log.DEBUG
)

settings = config.load()

if settings.aws_region:
    storage.set_region(config.get_value("aws_region"))

if settings.storage:
    storage_options = config.get_value("storage")
    storage.set_options(storage_options)


def get_adv_status(repo):
    response = github_rest_client.get(
        f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts"
    )
    alerts_enabled = response.status_code == 204
    vulnerable = repo.vulnerabilityAlerts.edges

    if vulnerable:
        repo.status = "vulnerable"
    elif alerts_enabled:
        repo.status = "clean"
    else:
        repo.status = "disabled"

    # append status to repo in original repositories file
    repo.securityAdvisoriesEnabledStatus = alerts_enabled

    return repo


def update_github_advisories_status():
    log.debug("update_github_advisories_status")
    today = datetime.date.today().isoformat()
    current = get_current_audit()

    by_alert_status = defaultdict(list)

    today_repositories = storage.read_json(f"{today}/data/repositories.json")
    current_repositories = storage.read_json(f"{current}/data/repositories.json")

    for state in today_repositories.keys():
        log.debug(f"{state} repos: {len(today_repositories[state])}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            for r in executor.map(get_adv_status, today_repositories[state]):
                by_alert_status[r.status].append(r)

    storage.save_json(f"{today}/data/repositories.json", today_repositories)
    status = storage.save_json(f"{today}/data/alert_status.json", by_alert_status)
    return status


def update_history(history):
    return storage.save_json("all/data/history.json", history)


def get_github_repositories_and_classify_by_status(org, today):
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


def get_github_activity_refs_audit(org, today):
    cursor = None
    last = False
    repository_list = []

    while not last:

        page = pgraph.query("refs", org=org, nth=20, after=cursor)

        repository_list.extend(page.organization.repositories.nodes)
        last = not page.organization.repositories.pageInfo.hasNextPage
        cursor = page.organization.repositories.pageInfo.endCursor

    total = len(repository_list)
    log.debug(f"Repository list count: {total}")

    repository_lookup = {repo.name: repo for repo in repository_list}

    total = len(repository_lookup.keys())
    log.debug(f"Repository lookup count: {total}")

    updated = storage.save_json(f"{today}/data/activity_refs.json", repository_lookup)


def get_github_activity_prs_audit(org, today):
    cursor = None
    last = False
    repository_list = []

    while not last:

        page = pgraph.query("prs", org=org, nth=100, after=cursor)

        repository_list.extend(page.organization.repositories.nodes)
        last = not page.organization.repositories.pageInfo.hasNextPage
        cursor = page.organization.repositories.pageInfo.endCursor

    total = len(repository_list)
    log.debug(f"Repository list count: {total}")

    repository_lookup = {repo.name: repo for repo in repository_list}

    total = len(repository_lookup.keys())
    log.debug(f"Repository lookup count: {total}")

    updated = storage.save_json(f"{today}/data/activity_prs.json", repository_lookup)


def get_dependabot_status(org, today):
    dependabot_status = dependabot_api.get_active_repos(org)
    storage.save_json(f"{today}/data/dependabot_status.json", dependabot_status)

    repositories = storage.read_json(f"{today}/data/repositories.json")

    dependabot_repo_names = [r.attributes.name for r in dependabot_status]
    for r in repositories["active"]:
        r.dependabotEnabledStatus = r.name in dependabot_repo_names

    storage.save_json(f"{today}/data/repositories.json", repositories)


def analyse_repo_ownership(today):
    list_owners = defaultdict(list)
    list_topics = defaultdict(list)
    repositories = storage.read_json(f"{today}/data/repositories.json")
    for repo in repositories["active"]:

        if repo.repositoryTopics.edges:
            for topics in repo.repositoryTopics.edges:
                list_owners[repo.name].append(topics.node.topic.name)
                list_topics[topics.node.topic.name].append(repo.name)

    owner_status = storage.save_json(f"{today}/data/owners.json", list_owners)
    topic_status = storage.save_json(f"{today}/data/topics.json", list_topics)
    return owner_status and topic_status


def analyse_pull_request_status(today):
    now = arrow.utcnow()
    pull_requests = storage.read_json(f"{today}/data/activity_prs.json")
    repositories = storage.read_json(f"{today}/data/repositories.json")
    for repo in repositories["active"]:

        repo_prs = pull_requests[repo.name]

        pr_final_status = "No pull requests in this repository"

        if repo_prs.pullRequests.edges:
            node = repo_prs.pullRequests.edges[0].node

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

        repo.recentPullRequestStatus = pr_final_status

    status = storage.save_json(f"{today}/data/repositories.json", repositories)
    return status


def analyse_activity_refs(today):
    now = arrow.utcnow()
    refs = storage.read_json(f"{today}/data/activity_refs.json")
    repositories = storage.read_json(f"{today}/data/repositories.json")
    for repo_name, repo in refs.items():
        repo_commit_dates = []
        for ref in repo.refs.edges:
            branch = ref.node
            for commit_edge in branch.target.history.edges:
                commit = commit_edge.node
                committed_date = arrow.get(commit.committedDate)
                repo_commit_dates.append(committed_date)
        repo_commit_dates.sort()
        if len(repo_commit_dates) > 0:
            first_commit = repo_commit_dates[0]
            last_commit = repo_commit_dates[-1]
            delta = last_commit - first_commit
            average_delta = delta / len(repo_commit_dates)
            average_days = average_delta.days
            currency_delta = now - last_commit
            currency_days = currency_delta.days

            for repo in repositories["active"]:
                if repo.name == repo_name:
                    repo.recentCommitDaysAgo = currency_days
                    repo.averageCommitFrequency = average_days
                    repo.isActive = currency_days < 365 and average_days < 180

                    currency_band = "older"
                    if currency_days <= 28:
                        currency_band = "within a month"
                    elif currency_days <= 91:
                        currency_band = "within a quarter"
                    elif currency_days <= 365:
                        currency_band = "within a year"

                    repo.currencyBand = currency_band

    updated = storage.save_json(f"{today}/data/repositories.json", repositories)

    return updated


def analyse_team_membership(today):
    storage.read_json(f"{today}/data/topics.json")
    repositories = storage.read_json(f"{today}/data/repositories.json")

    # This one can't currently use storage because it's
    # outside the output folder and not written to S3.
    with open("teams.json", "r") as teams_file:
        teams = json.loads(teams_file.read())

    for status, repo_list in repositories.items():
        for repo in repo_list:
            repo_team = "unknown"
            repo_topics = []
            if repo.repositoryTopics:
                repo_topics = [
                    topic_edge.node.topic.name
                    for topic_edge in repo.repositoryTopics.edges
                ]

            for team, team_topics in teams.items():
                for topic in team_topics:
                    if topic in repo_topics:
                        repo_team = team
            repo.team = repo_team

    updated = storage.save_json(f"{today}/data/repositories.json", repositories)


def analyse_vulnerability_patch_recommendations(today):
    repositories = storage.read_json(f"{today}/data/repositories.json")

    vulnerable_list = [
        node for node in repositories["active"] if node.vulnerabilityAlerts.edges
    ]
    vulnerable_by_severity = vulnerability_summarizer.group_by_severity(vulnerable_list)

    storage.save_json(
        f"{today}/data/vulnerable_by_severity.json", vulnerable_by_severity
    )

    for repo in repositories["active"]:
        for severity, vuln_repos in vulnerable_by_severity.items():
            for vuln_repo in vuln_repos:
                if repo.name == vuln_repo.name:
                    log.debug(repo.name)
                    repo.maxSeverity = severity
                    repo.patches = vulnerability_summarizer.get_patch_list(repo)
                    repo.vulnerabiltyCounts = (
                        vulnerability_summarizer.get_repository_severity_counts(repo)
                    )

    updated = storage.save_json(f"{today}/data/repositories.json", repositories)

    # TODO Remove this redundant rebuilding step

    repositories = storage.read_json(f"{today}/data/repositories.json")

    vulnerable_list = [
        node for node in repositories["active"] if node.vulnerabilityAlerts.edges
    ]
    vulnerable_by_severity = vulnerability_summarizer.group_by_severity(vulnerable_list)

    storage.save_json(
        f"{today}/data/vulnerable_by_severity.json", vulnerable_by_severity
    )
    return updated


def build_route_data(today):
    route_data_overview_repositories_by_status(today)
    route_data_overview_alert_status(today)
    route_data_overview_vulnerable_repositories(today)
    route_data_overview_activity(today)
    route_data_overview_monitoring_status(today)


def route_data_overview_monitoring_status(today):
    monitoring_disabled = storage.read_json(f"{today}/data/alert_status.json")
    repositories = storage.read_json(f"{today}/data/repositories.json")

    monitoring_alert = len(monitoring_disabled["disabled"])

    dependabot_count = 0
    advisory_count = 0

    for repo in repositories["active"]:
        dependabot_status = repo.dependabotEnabledStatus
        advisory_status = repo.securityAdvisoriesEnabledStatus

        if dependabot_status:
            dependabot_count += 1

        elif advisory_status:
            advisory_count += 1

    template_data = {
        "content": {
            "title": "Overview - Monitoring status",
            "org": config.get_value("github_org"),
            "monitoring": {
                "dependabot_enabled": dependabot_count,
                "advisory_enabled": advisory_count,
                "disabled": monitoring_alert,
            },
        },
        "footer": {"updated": today},
    }

    monitoring_status = storage.save_json(
        f"{today}/routes/overview_monitoring_status.json", template_data
    )
    return monitoring_status


def route_data_overview_repositories_by_status(today):
    repositories_by_status = storage.read_json(f"{today}/data/repositories.json")
    status_counts = stats.count_types(repositories_by_status)
    repo_count = sum(status_counts.values())

    vulnerable_by_severity = storage.read_json(
        f"{today}/data/vulnerable_by_severity.json"
    )

    template_data = {
        "content": {
            "title": "Overview - Repositories by status",
            "org": config.get_value("github_org"),
            "repositories": {
                "all": repo_count,
                "by_status": status_counts,
                "repos_by_status": repositories_by_status,
            },
            "vulnerable_by_severity": vulnerable_by_severity,
        },
        "footer": {"updated": today},
    }

    overview_status = storage.save_json(
        f"{today}/routes/overview_repositories_by_status.json", template_data
    )
    return overview_status


def route_data_overview_alert_status(today):

    by_alert_status = {"public": {}}
    alert_statuses = storage.read_json(f"{today}/data/alert_status.json")
    for status, repos in alert_statuses.items():
        by_alert_status["public"][status] = len(repos)

    status = storage.save_json(
        f"{today}/routes/count_alert_status.json", by_alert_status
    )
    return status


def route_data_overview_vulnerable_repositories(today):

    alert_status = storage.read_json(f"{today}/routes/count_alert_status.json")

    vulnerable_by_severity = storage.read_json(
        f"{today}/data/vulnerable_by_severity.json"
    )
    severity_counts = stats.count_types(vulnerable_by_severity)
    vulnerable_count = sum(severity_counts.values())
    severities = vulnerability_summarizer.SEVERITIES

    template_data = {
        "content": {
            "title": "Overview - Vulnerable repositories",
            "org": config.get_value("github_org"),
            "vulnerable": {
                "severities": severities,
                "all": vulnerable_count,
                "by_severity": severity_counts,
                "repositories": vulnerable_by_severity,
            },
            "alert_status": alert_status,
        },
        "footer": {"updated": today},
    }

    template_status = storage.save_json(
        f"{today}/routes/overview_vulnerable_repositories.json", template_data
    )
    return template_status


def route_data_overview_activity(today):
    repositories = storage.read_json(f"{today}/data/repositories.json")
    counts = defaultdict(int)
    repositories_by_activity = defaultdict(list)
    for repo in repositories["active"]:
        if "recentCommitDaysAgo" in repo:
            currency = repo.currencyBand
            counts[currency] += 1
            repositories_by_activity[currency].append(repo)

    bands = ["within a month", "within a quarter", "within a year", "older"]
    template_data = {
        "content": {
            "title": "Overview - Activity",
            "org": config.get_value("github_org"),
            "activity": {
                "bands": bands,
                "counts": counts,
                "repositories": repositories_by_activity,
            },
        },
        "footer": {"updated": today},
    }

    overview_activity_status = storage.save_json(
        f"{today}/routes/overview_activity.json", template_data
    )
    return overview_activity_status


def get_current_audit():
    try:
        history = get_history()
        current = history.current
    except FileNotFoundError:
        current = datetime.date.today().isoformat()
        log.error(errors.get_log_event())
    return current


def get_history():
    history_file = "all/data/history.json"

    default = Dict({"current": None, "alltime": {}})
    history = storage.read_json(history_file, default=default)

    log.debug(str(history))

    return history


def get_github_resolve_alert_status():
    today = datetime.date.today().isoformat()
    by_alert_status = defaultdict(list)

    repositories = storage.read_json(f"{today}/data/repositories.json")
    for repo in repositories["active"]:
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

        # append status to repo in original repositories file
        repo.securityAdvisoriesEnabledStatus = alerts_enabled

        by_alert_status[status].append(repo)

    storage.save_json(f"{today}/data/repositories.json", repositories)
    status = storage.save_json(f"{today}/data/alert_status.json", by_alert_status)
    return status


@click.group()
def cli():
    pass


@cli.command("run-task")
@click.argument("task")
def cli_task(task):
    today = datetime.date.today().isoformat()
    org = config.get_value("github_org")
    history = get_history()

    if task == "repository-status":
        get_github_repositories_and_classify_by_status(org, today)
    elif task == "get-activity":
        get_github_activity_refs_audit(org, today)
        get_github_activity_prs_audit(org, today)
    elif task == "dependabot":
        get_dependabot_status(org, today)
    elif task == "advisories":
        if history.current:
            update_github_advisories_status()
        else:
            get_github_resolve_alert_status()
    elif task == "membership":
        analyse_repo_ownership(today)
        analyse_team_membership(today)
    elif task == "analyse-activity":
        analyse_pull_request_status(today)
        analyse_activity_refs(today)
    elif task == "patch":
        analyse_vulnerability_patch_recommendations(today)
    elif task == "routes":
        build_route_data(today)
    else:
        log.error("ERROR: Undefined task")


@cli.command("audit")
def click_audit():
    cronable_vulnerability_audit()


def lambda_handler(event, context):
    cronable_vulnerability_audit()


def cronable_vulnerability_audit():
    today = datetime.date.today().isoformat()

    # set status to inprogress in history
    history = get_history()
    history.alltime[today] = "in progress"
    update_history(history)

    # retrieve data from apis
    org = config.get_value("github_org")
    # todo - set maintenance mode
    get_github_repositories_and_classify_by_status(org, today)
    get_github_activity_refs_audit(org, today)
    get_github_activity_prs_audit(org, today)

    # Dependabot Preview has been shut down as of August 3rd, 2021. 
    # In order to keep getting Dependabot updates, please migrate to GitHub-native Dependabot.
    # https://preview.tinyurl.com/dependabot-deprecated
    #get_dependabot_status(org, today)

    if history.current:
        update_github_advisories_status()
    else:
        get_github_resolve_alert_status()

    # analyse raw data
    analyse_repo_ownership(today)
    analyse_pull_request_status(today)
    analyse_activity_refs(today)
    analyse_vulnerability_patch_recommendations(today)
    analyse_team_membership(today)

    # build page template data
    build_route_data(today)

    # update current audit in history
    history.current = today
    history.alltime[today] = "complete"
    update_history(history)
    # todo - set enabled mode

    send_vulnerable_by_severtiy_to_splunk()
    return True


@cli.command("send_to_splunk")
def send_to_splunk():
    send_vulnerable_by_severtiy_to_splunk()


def send_vulnerable_by_severtiy_to_splunk():
    """Send vulnerable_by_severity.json to Splunk"""
    host = config.get_value("splunk_host")
    token = config.get_value("splunk_token")

    if not host or not token:
        raise

    s = Splunk(host, token)

    s.send_vulnerable_by_severtiy(
        storage.read_json(f"{datetime.date.today().isoformat()}/data/repositories.json")
    )


if __name__ == "__main__":
    cli()
