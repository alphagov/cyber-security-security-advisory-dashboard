from addict import Dict


def reset():
    _repositories_by_status = {
        "public": [],
        "private": [],
        "archived": [],
        "disabled": [],
    }

    return _repositories_by_status


def _get_status(repo):
    if repo.isArchived:
        status = "archived"
    elif repo.isDisabled:
        status = "disabled"
    elif repo.isPrivate:
        status = "private"
    else:
        status = "public"

    return status


def collate_by_status(repositories):
    _repositories_by_status = reset()
    [_repositories_by_status[_get_status(repo)].append(repo) for repo in repositories]
    return Dict(_repositories_by_status)
