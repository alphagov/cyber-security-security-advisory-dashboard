import pgraph
from dependabot_api import get_parsed, get_repos_by_status
import os
from addict import Dict


def setup_module(module):
    """
    Set FLASK_ENV to production to pull in the right env vars
    for pgraph.query
    """
    os.environ["FLASK_ENV"] = "production"


def teardown_module(module):
    """
    Set FLASK_ENV back to development for remaining tests
    """
    os.environ["FLASK_ENV"] = "development"


def test_github_graphql() -> None:
    """
    Tests that there are *some* repositories returned by each
    of the pgraph queries in `query/`
    """

    for query in ["all", "prs", "refs"]:
        page = Dict(pgraph.query(query, org="alphagov", nth=1, after=None))
        assert page.organization.repositories.nodes


def test_github_dependabot() -> None:
    """
    Tests that there are more than 10 active, inactive, by_status and custom, repos.
    """
    active = "/active_repos?account-id=596977&account-type=org"
    assert len(get_parsed(active)) > 10
    by_status = get_repos_by_status("alphagov")
    assert len(by_status) > 10
