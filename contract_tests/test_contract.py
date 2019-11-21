import pgraph
from dependabot_api import get_parsed, get_active_repos
from addict import Dict


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
    by_status = get_active_repos("alphagov")
    assert len(by_status) > 10
