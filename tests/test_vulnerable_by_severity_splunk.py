import pytest
from VulnerableBySeveritySplunk import (
    VulnerableBySeveritySplunk,
    Vulnerability,
    VulnerabilityAlert,
    Project,
)
import json


@pytest.fixture
def vuln():
    """Test data"""
    with open("tests/fixtures/data/vulnerable_by_severity.json") as f:
        return json.load(f)


def test_project_vulnerability_alerts(vuln):
    """Test VulnerableBySeveritySplunk.splunk_format returns the correct
    sized list for Splunk ingestion. The test file has 1 repo with a 3
    child objects so that should generate 3 Splunk events.
    """
    assert len(list(VulnerableBySeveritySplunk(vuln).splunk_format())) == 3


@pytest.fixture
def project(vuln):
    """Test project object"""
    return Project(vuln["LOW"][0])


def test_project_owner(project):
    """Test owner is extracted"""
    assert project.owner == "alphagov"


def test_project_topics(project):
    """Test topics are extracted correctly"""
    assert project.topics == ["govuk"]


def test_project_vulnerability_alerts_size(project):
    """Should return a generator containing two elements"""
    assert len(list(project.vulnerability_alerts)) == 2


def test_project_vulnerability_alerts_type(project):
    """Should return a generator containing VulnerabilityAlerts"""
    assert all(isinstance(i, VulnerabilityAlert) for i in project.vulnerability_alerts)


def test_project_iter(project):
    """Should return a custom dict() representation"""
    assert dict(project) == {
        "isArchived": False,
        "isDisabled": False,
        "isPrivate": False,
        "name": "marples",
        "owner": "alphagov",
        "topics": ["govuk"],
        "recentCommitDaysAgo": "",
        "recentPullRequestStatus": "",
        "securityAdvisoriesEnabledStatus": "",
        "team": "",
        "averageCommitFrequency": "",
        "currencyBand": "",
        "maxSeverity": "",
    }


def test_project_splunk_format(project):
    """Should generate a new entry for each possible combination of child elements"""
    assert len(list(project.splunk_format())) == 3


@pytest.fixture
def vulnerability_alert(vuln):
    """Test vulnerability_alert object"""
    return VulnerabilityAlert(vuln["LOW"][0]["vulnerabilityAlerts"]["edges"][0]["node"])


def test_vulnerability_alerts_vulnerability_alert_size(vulnerability_alert):
    """Should return a generator containing two elements"""
    assert len(list(vulnerability_alert.vulnerabilities)) == 2


def test_vulnerability_alerts_vulnerabiliteis_type(vulnerability_alert):
    """Should return a generator for two Vulnerabilities"""
    assert all(
        isinstance(i, Vulnerability) for i in vulnerability_alert.vulnerabilities
    )


def test_vulnerability_alert_iter(vulnerability_alert):
    """Should return a custom dict() representation"""
    assert dict(vulnerability_alert) == {
        "packageName": "activerecord",
        "summary": "Moderate severity vulnerability that affects activerecord",
        "vulnerableManifestPath": "marples.gemspec",
        "vulnerableRequirements": "~> 3.1.0",
    }


def test_vulnerability_alert_splunk_format(vulnerability_alert):
    """Should generate a new entry for each possible combination of child elements"""
    assert list(vulnerability_alert.splunk_format()) == [
        {
            "packageName": "activerecord",
            "summary": "Moderate severity vulnerability that affects activerecord",
            "vulnerability": {
                "description": "activerecord/lib/active_record/nested_attributes.rb "
                "in Active Record in Ruby on Rails 3.1.x "
                "and 3.2.x before 3.2.22.1, 4.0.x and 4.1.x "
                "before 4.1.14.1, 4.2.x before 4.2.5.1, and "
                "5.x before 5.0.0.beta1.1 does not properly "
                "implement a certain destroy option, which "
                "allows remote attackers to bypass intended "
                "change restrictions by leveraging use of "
                "the nested attributes feature.",
                "firstPatchedVersion": "3.2.22.1",
                "package": "activerecord",
                "severity": "MODERATE",
            },
            "vulnerableManifestPath": "marples.gemspec",
            "vulnerableRequirements": "~> 3.1.0",
        },
        {
            "packageName": "activerecord",
            "summary": "Moderate severity vulnerability that affects activerecord",
            "vulnerability": {
                "description": "activerecord/lib/active_record/nested_attributes.rb "
                "in Active Record in Ruby on Rails 3.1.x "
                "and 3.2.x before 3.2.22.1, 4.0.x and 4.1.x "
                "before 4.1.14.1, 4.2.x before 4.2.5.1, and "
                "5.x before 5.0.0.beta1.1 does not properly "
                "implement a certain destroy option, which "
                "allows remote attackers to bypass intended "
                "change restrictions by leveraging use of "
                "the nested attributes feature.",
                "firstPatchedVersion": "4.1.14.1",
                "package": "activerecord",
                "severity": "MODERATE",
            },
            "vulnerableManifestPath": "marples.gemspec",
            "vulnerableRequirements": "~> 3.1.0",
        },
    ]


@pytest.fixture
def vulnerability(vuln):
    """Test vulnerability object"""
    return Vulnerability(
        vuln["LOW"][0]["vulnerabilityAlerts"]["edges"][0]["node"]["securityAdvisory"][
            "vulnerabilities"
        ]["edges"][0]["node"]
    )


def test_vulnerability_first_patched_version(vulnerability):
    """Should return correct version number"""
    assert vulnerability.first_patched_version == "3.2.22.1"


def test_vulnerability_first_patched_version_empty(vulnerability):
    """Should return an empty string"""
    vulnerability.data["firstPatchedVersion"] = []
    assert vulnerability.first_patched_version == ""


def test_vulnerability_iter(vulnerability):
    """Should return a custom dict() representation"""
    assert dict(vulnerability) == {
        "description": "activerecord/lib/active_record/nested_attributes.rb in Active "
        "Record in Ruby on Rails 3.1.x and 3.2.x before 3.2.22.1, "
        "4.0.x and 4.1.x before 4.1.14.1, 4.2.x before 4.2.5.1, and "
        "5.x before 5.0.0.beta1.1 does not properly implement a "
        "certain destroy option, which allows remote attackers to "
        "bypass intended change restrictions by leveraging use of the "
        "nested attributes feature.",
        "firstPatchedVersion": "3.2.22.1",
        "package": "activerecord",
        "severity": "MODERATE",
    }
