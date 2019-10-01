import pytest
import requests
import datetime
from splunk import Splunk


@pytest.fixture
def splunk(mocker):
    mocker.patch("requests.post")
    return Splunk("host:443", "token")


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
            verify=False,
        )
    ]


def test_splunk_data_files(splunk):
    """Should return a list of JSON files from the fixtures directory."""

    splunk.data_prefix = "tests/fixtures"

    assert splunk.data_files() == ["tests/fixtures/data/repo.json"]


def test_splunk_data_prefix(splunk):
    """Should be set to todays date by default"""
    assert splunk.data_prefix == datetime.date.today().isoformat()


def test_splunk_send_data_files(splunk, mocker):
    """Should send all data files to Splunk"""

    splunk.data_prefix = "tests/fixtures"

    splunk.send_data_files()

    assert requests.post.call_args_list == [
        mocker.call(
            "https://host:443/services/collector",
            '{"repo": "foo"}\n',
            headers={"Authorization": "Splunk token"},
            verify=False,
        )
    ]
