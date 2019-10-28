import pytest
import requests
import json
from splunk import Splunk
from VulnerableBySeveritySplunk import VulnerableBySeveritySplunk


@pytest.fixture
def splunk(mocker):
    mocker.patch("requests.post")
    return Splunk("host:443", "token")


@pytest.fixture
def vuln():
    """Test data"""
    with open("tests/fixtures/data/vulnerable_by_severity.json") as f:
        return json.load(f)


def test_send_json(splunk, mocker):
    """Test `splunk.send_json` invokes `requests.post` with the correct
    parameters.
    """

    splunk.send_json({"test": "bar"})

    assert requests.post.call_args_list == [
        mocker.call(
            "https://host:443/services/collector",
            {"test": "bar"},
            headers={"Authorization": "Splunk token"},
            timeout=10,
        )
    ]


def test_splunk_send_data_files(splunk, mocker, vuln):
    """Should send all data files to Splunk"""

    splunk.send_vulnerable_by_severtiy(vuln)

    expected_calls = [
        mocker.call(
            "https://host:443/services/collector",
            json.dumps(
                {
                    "host": "advisory_dashboard",
                    "source": f"vulnerable_by_severity",
                    "event": v,
                }
            ),
            headers={"Authorization": "Splunk token"},
            timeout=10,
        )
        for v in VulnerableBySeveritySplunk(vuln).splunk_format()
    ]

    assert all(call in requests.post.call_args_list for call in expected_calls)
