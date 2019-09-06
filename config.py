import os
import json


from addict import Dict
import boto3


SETTNGS = None


def get_ssm_client():
    settings = load()
    region = settings.get("aws_region")
    if "AWS_SECRET_ACCESS_KEY" in os.environ:
        ssm = boto3.client(
            "ssm",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            aws_session_token=os.environ["AWS_SESSION_TOKEN"],
            region_name=region,
        )
    else:
        ssm = None
    return ssm


def load():
    if not SETTNGS:
        try:

            env = os.environ["FLASK_ENV"]
            with open("settings.json", "r") as settings_file:
                settings = Dict(json.loads(settings_file.read()))
                SETTINGS = settings[env]
        except:
            SETTINGS = {}

    return SETTINGS


def get_value(name):
    settings = load()
    setting = settings.get(name, {"source": None})
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
        else:
            value = None
    return value


def get_setting(name):
    settings = load()
    setting = settings.get(name, {"source": None})
    return setting
