class VulnerableBySeveritySplunk:
    """Format `vulnerable_by_severity.json` for Splunk"""

    def __init__(self, data):
        """
        :param data: a dict() created from `data/vulnerable_by_severity.json`
        """
        self.data = data

    def splunk_format(self):
        """Format for splunk: Split out multivalue fields into separate
        events. One entry per possible combination."""
        for _k, level in self.data.items():
            for project in level:
                for p in Project(project).splunk_format():
                    yield p


class Project(object):
    """Format Github API projects/repos for Splunk
    https://developer.github.com/v4/object/project/

    Some fields are non standard and have already been processed.
    """

    def __init__(self, data):
        """
        :param data: Dict representing the Github API object
        """
        self.data = data

    @property
    def owner(self):
        """Project owner
        https://developer.github.com/v4/interface/projectowner/
        """
        return self.data["owner"]["login"]

    @property
    def topics(self):
        """Topic
        https://developer.github.com/v4/object/topic/
        """
        return [
            topic["node"]["topic"]["name"]
            for topic in self.data["repositoryTopics"]["edges"]
        ]

    @property
    def vulnerability_alerts(self):
        """Generator for VulnerabilityAlerts"""
        for i in self.data["vulnerabilityAlerts"]["edges"]:
            yield VulnerabilityAlert(i["node"])

    def __iter__(self):
        """Display object as custom dict()"""
        return iter(
            {
                "isArchived": self.data["isArchived"],
                "isPrivate": self.data["isPrivate"],
                "isDisabled": self.data["isDisabled"],
                "name": self.data["name"],
                "owner": self.owner,
                "topics": self.topics,
                "team": self.data.get("team", ""),
                "securityAdvisoriesEnabledStatus": self.data.get(
                    "securityAdvisoriesEnabledStatus", ""
                ),
                "recentPullRequestStatus": self.data.get("recentPullRequestStatus", ""),
                "recentCommitDaysAgo": self.data.get("recentCommitDaysAgo", ""),
                "averageCommitFrequency": self.data.get("averageCommitFrequency", ""),
                "maxSeverity": self.data.get("maxSeverity", ""),
                "currencyBand": self.data.get("currencyBand", ""),
                "dependabotEnabledStatus": self.data.get("dependabotEnabledStatus", ""),
            }.items()
        )

    def splunk_format(self):
        """Format for splunk: Split out multivalue fields into separate events."""
        for va in self.vulnerability_alerts:
            for s in va.splunk_format():
                yield {**dict(self), "vulnerability_alerts": dict(s)}
        if not self.data["vulnerabilityAlerts"]["edges"]:
            yield dict(self)


class VulnerabilityAlert(object):
    """Format VulnerabilityAlerts for Splunk
    https://developer.github.com/v4/object/repositoryvulnerabilityalert/
    """

    def __init__(self, data):
        """
        :param data: Dict representing the Github API object
        """
        self.data = data

    @property
    def vulnerabilities(self):
        """Generator for attached Vulnerabilities"""
        for topic in self.data["securityAdvisory"]["vulnerabilities"]["edges"]:
            yield Vulnerability(topic["node"])

    def __iter__(self):
        """Display object as custom dict()"""
        return iter(
            {
                "packageName": self.data["packageName"],
                "vulnerableManifestPath": self.data["vulnerableManifestPath"],
                "vulnerableRequirements": self.data["vulnerableRequirements"],
                "summary": self.data["securityAdvisory"]["summary"],
                "publishedAt": self.data["securityAdvisory"].get("publishedAt"),
                "updatedAt": self.data["securityAdvisory"].get("updatedAt"),
                "withdrawnAt": self.data["securityAdvisory"].get("withdrawnAt"),
                "ghsaId": self.data["securityAdvisory"].get("ghsaId"),
            }.items()
        )

    def splunk_format(self):
        """Format for splunk: Split out multivalue fields into separate events."""
        for v in self.vulnerabilities:
            yield {**dict(self), "vulnerability": dict(v)}


class Vulnerability(object):
    """Format Github SecurityVulnerabilities for Splunk
    https://developer.github.com/v4/object/securityvulnerability/
    """

    def __init__(self, data):
        """
        :param data: Dict representing the Github API object
        """
        self.data = data

    @property
    def first_patched_version(self):
        """First patched or empty string. Not all Vulnerabilities have the
        `identifier` property"""
        return (
            self.data["firstPatchedVersion"]["identifier"]
            if self.data["firstPatchedVersion"]
            else ""
        )

    def __iter__(self):
        """Display object as custom dict()"""
        return iter(
            {
                "package": self.data["package"]["name"],
                "description": self.data["advisory"]["description"],
                "severity": self.data["severity"],
                "firstPatchedVersion": self.first_patched_version,
            }.items()
        )
