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
    global SETTINGS
    if not SETTINGS:
        try:
            # Unset all empty env vars.
            for var, val in os.environ.items():
                if val == "":
                    del os.environ[var]

            env = os.environ["FLASK_ENV"]
            settings_file = f"settings.{env}.json"
            # print(f"Settings file: {settings_file}", sys.stderr)
            with open(settings_file, "r") as settings_file:
                SETTINGS = Dict(json.loads(settings_file.read()))
                set_region(get_value("aws_region"))

        except Exception as e:
            print(e.message)
            SETTINGS = Dict({})

    return SETTINGS


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
