import requests
import glob
import datetime


class Splunk(object):
    def __init__(self, host, hec_token):
        """Create a connection to the Splunk API
        :param host: Hostname / IP for Splunk
        :param hec_token: HEC token for splunk
        :param
        """
        self.host = host
        self.hec_token = hec_token
        self.data_prefix = datetime.date.today().isoformat()

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
            verify=False,
        )

    def data_files(self):
        """Generate a list of data files"""
        return glob.glob(f"{self.data_prefix}/data/*.json")

    def send_data_files(self):
        """Send data files to Splunk"""
        for df in self.data_files():
            with open(df, "r") as f:
                self.send_json(f.read())
