import cyber_dependabot

from addict import Dict


def test_get_topics():
    mock_repo_with_topic = Dict(
        {
            "name": "marples",
            "owner": {"login": "alphagov"},
            "repositoryTopics": {
                "edges": [
                    {"node": {"topic": {"id": "MDU6VG9waWNnb3Z1aw==", "name": "govuk"}}}
                ]
            },
            "isArchived": "false",
            "isPrivate": "false",
            "isDisabled": "false",
        }
    )

    mock_repo_without_topic = Dict({"repositoryTopics": {"edges": []}})

    actual_with_topic = cyber_dependabot.get_topics(mock_repo_with_topic)
    actual_without_topic = cyber_dependabot.get_topics(mock_repo_without_topic)

    assert actual_with_topic == ["govuk"]
    assert actual_without_topic == []


def test_enable_alert_ignores_correct_tags():
    mock_repo_with_correct_tag = Dict(
        {
            "repositoryTopics": {
                "edges": [
                    {
                        "node": {
                            "topic": {"id": "id==", "name": "no-security-advisories"}
                        }
                    }
                ]
            }
        }
    )

    actual = cyber_dependabot.enable_alert(mock_repo_with_correct_tag)

    assert actual == 204


def test_enable_alert_ignores_correct_repos():
    mock_repo_with_security_alerts_enabled = Dict(
        {"securityAdvisoriesEnabledStatus": True}
    )
    mock_archived_repo = Dict({"isArchived": True})

    actual_aready_enabled = cyber_dependabot.enable_alert(
        mock_repo_with_security_alerts_enabled
    )
    actual_archived = cyber_dependabot.enable_alert(mock_archived_repo)

    assert actual_aready_enabled == 204
    assert actual_archived == 204


def test_enable_alerts_enables_alerts(mocker):
    mocker.patch.object(cyber_dependabot, "put")
    cyber_dependabot.put.return_value = Dict({"status_code": 567, "text": "test"})
    mock_repo = Dict(
        {
            "securityAdvisoriesEnabledStatus": False,
            "isArchived": False,
            "owner": {"login": "test"},
            "name": "test-repo",
        }
    )

    cyber_dependabot.enable_alert(mock_repo)

    cyber_dependabot.put.assert_called_with(
        "/repos/test/test-repo/vulnerability-alerts",
    )
    cyber_dependabot.put.assert_called_once()
