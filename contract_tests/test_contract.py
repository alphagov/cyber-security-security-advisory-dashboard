import pgraph
from addict import Dict


def test_github_graphql() -> None:
    """
    Tests that there are *some* repositories returned by each
    of the pgraph queries in `query/`
    """

    for query in ["all", "prs", "refs"]:
        page = Dict(pgraph.query(query, org="alphagov", nth=1, after=None))
        assert page.organization.repositories.nodes
