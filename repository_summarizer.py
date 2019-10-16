from addict import Dict


STATUSES = ["active", "archived", "disabled"]


def get_status(repo):
    if repo.isArchived:
        status = "archived"
    elif repo.isDisabled:
        status = "disabled"
    else:
        status = "active"

    return status


def group_by_status(repositories):
    repositories_by_status = Dict({status: [] for status in STATUSES})
    for repo in repositories:
        status = get_status(repo)
        repositories_by_status[status].append(repo)
    return repositories_by_status
