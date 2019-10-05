import requests
import json
from VulnerableBySeveritySplunk import VulnerableBySeveritySplunk
from concurrent.futures import ThreadPoolExecutor


class Splunk(object):
    def __init__(self, host, hec_token):
        """Create a connection to the Splunk API
        :param host: Hostname / IP for Splunk
        :param hec_token: HEC token for splunk
        :param
        """
        self.host = host
        self.hec_token = hec_token

    def send_json(self, json):
        """
        Send a JSON payload to the Splunk HEC. There is a 1mb payload size limit.
        :param json: A JSON object or multiple JSON objects separated by newlines.
        :returns: A Requests Response object
        :rtype: headers
        """
        return requests.post(
            f"https://{self.host}/services/collector",
            json,
            headers={"Authorization": f"Splunk {self.hec_token}"},
        )

    def send_vulnerable_by_severtiy(self, v, max_workers=50):
        """Send vulnerable_by_severity data to Splunk

        :param v: dict() representation of vulnerable_by_severity.json
        :param max_workers: Concurrent HTTP requests

        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for project in VulnerableBySeveritySplunk(v).splunk_format():
                executor.submit(
                    self.send_json,
                    json.dumps(
                        {
                            "host": "advisory_dashboard",
                            "source": f"vulnerable_by_severity",
                            "event": project,
                        }
                    ),
                )
