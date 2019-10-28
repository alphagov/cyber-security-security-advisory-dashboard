import audit_lambda
import splunk
import config  # noqa
import storage  # noqa


def test_send_vulnerable_by_severtiy_to_splunk(mocker):
    mocker.patch("config.get_value", return_value="foo")
    mocker.patch("storage.read_json", return_value={})
    mocker.patch("splunk.Splunk.send_vulnerable_by_severtiy", return_value="foo")

    audit_lambda.send_vulnerable_by_severtiy_to_splunk()

    print(splunk.Splunk.send_vulnerable_by_severtiy.call_args_list)
    assert splunk.Splunk.send_vulnerable_by_severtiy.call_args_list
