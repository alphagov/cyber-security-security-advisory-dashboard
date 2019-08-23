import sys
from addict import Dict

class RepositorySummarizer():

    _repositories_by_status = {}

    @classmethod
    def reset(cls):
        cls._repositories_by_status = {
            "public": [],
            "private": [],
            "archived": [],
            "disabled": []
        }

    @classmethod
    def _get_status(cls, repo):
        if repo.isArchived:
            status = "archived"
        elif repo.isDisabled:
            status = "disabled"
        elif repo.isPrivate:
            status = "private"
        else:
            status = "public"

        cls._repositories_by_status[status].append(repo)

        return f"{repo.name}: {status}"

    @classmethod
    def collate_by_status(cls, repositories):
        cls.reset()
        [cls._get_status(repo) for repo in repositories]
        return Dict(cls._repositories_by_status)


class VulnerabilitySummarizer():

    _vulnerable_by_severity = {}
    _severities = [
        "LOW",
        "MODERATE",
        "HIGH",
        "CRITICAL"
    ]

    @classmethod
    def get_severity_order(cls):
        return cls._severities

    @classmethod
    def _get_severity(cls, repo):
        maxSeverityIndex = -1
        severity = "NONE"

        for vaEdge in repo.vulnerabilityAlerts.edges:
            print(vaEdge.node.packageName, file=sys.stderr)

            for vEdge in vaEdge.node.securityAdvisory.vulnerabilities.edges:

                edgeSeverity = vEdge.node.severity
                print(f"{vEdge.node.package.name} : {edgeSeverity}", file=sys.stderr)
                severityIndex = cls._severities.index(edgeSeverity)
                print(f"{edgeSeverity}: {severityIndex}", file=sys.stderr)
                if severityIndex > maxSeverityIndex:
                    maxSeverityIndex = severityIndex
                    severity = edgeSeverity

        if severity not in cls._vulnerable_by_severity:
            cls._vulnerable_by_severity[severity] = []
        cls._vulnerable_by_severity[severity].append(repo)

        return f"{repo.name}: {severity}"

    @classmethod
    def collate_by_severity(cls, repositories):
        cls._vulnerable_by_severity = {}
        [cls._get_severity(repository) for repository in repositories]
        return Dict(cls._vulnerable_by_severity)


def collate_repositories_by_status(repositories):
    return RepositorySummarizer.collate_by_status(repositories)


def collate_vulnerable_by_severity(repositories):
    return VulnerabilitySummarizer.collate_by_severity(repositories)

def count_types(categories):
    counts = {}
    for category,list in categories.items():
        counts[category] = len(list)
    return counts

def get_severity_order():
    return VulnerabilitySummarizer.get_severity_order()