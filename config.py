import os
import json

from addict import Dict
import boto3

SETTINGS = None
REGION = None


def set_region(region):
    global REGION
    REGION = region


def load():
    """
    Load settings
    """
    flask_env = os.environ["FLASK_ENV"]

    with open(f"settings.{flask_env}.json", "r") as f:
        return Dict(json.load(f))


def get_ssm_client():
    region = get_value("aws_region")
    if "AWS_SECRET_ACCESS_KEY" in os.environ:
        ssm = boto3.client(
            "ssm",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            aws_session_token=os.environ["AWS_SESSION_TOKEN"],
            region_name=region,
        )
    else:
        print("aws_secret_key not in env, setting to none")
        ssm = None
    return ssm


def get_value(name):
    settings = load()
    setting = settings.get(name, Dict({"source": None}))
    value = None
    if "source" in setting:
        if setting.source == "env":
            value = os.environ[setting.name]
        elif setting.source == "ssm":
            ssm = get_ssm_client()
            if ssm:
                response = ssm.get_parameter(Name=setting.name, WithDecryption=True)
                param = response["Parameter"]
                value = param["Value"]
            else:
                value = None
        elif setting.source == "this":
            value = setting.name

    return value


def get_setting(name):
    settings = load()
    setting = settings.get(name, {"source": None})
    return setting
