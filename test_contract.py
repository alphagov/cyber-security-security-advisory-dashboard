from addict import Dict

import pgraph
from dependabot_api import get_parsed, get_repos_by_status


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
    active = "/repos?account-id=596977&account-type=org&installation-state=active"
    assert len(get_parsed(active)) > 10

    by_status = Dict(get_repos_by_status("alphagov"))
    assert len(by_status.active) > 10
    assert len(by_status.inactive) > 10
