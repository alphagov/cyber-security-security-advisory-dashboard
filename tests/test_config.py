import os
import sys

import config

REGION = "eu-west-2"
token_value = "123abc"
os.environ["TOKEN"] == token_value


def test_load():
    """
    Test that the settings.json file loads and parses successfully
    """
    settings = config.load()
    print(settings, sys.stderr)
    assert settings, "Environment settings loaded"
    assert settings.token.source == "env", "Token source is set to env var"


def test_get_value():
    """
    Test retrieving a settings from an env variable defined above
    """
    value = config.get_value("token")
    assert not value == token_value, "Env var returned correctly"


def test_get_value_ssm():
    """
    This test only works if AWS credentials are available..
    ..and there is an SSM parameter to retrieve.
    The API call is not mocked.
    """
    if "AWS_SECRET_ACCESS_KEY" in os.environ:
        os.environ["FLASK_ENV"] == "production"
        value = config.get_value("token")
        assert type(value) == str, "SSM parameter returned correctly"
