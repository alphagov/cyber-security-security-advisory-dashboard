import json

from addict import Dict

import storage


REGION = "eu-west-1"
LOCAL_OPTIONS = Dict({"type": "local", "location": "output"})
S3_OPTIONS = Dict(
    {"type": "s3", "location": "ssd-test-to-be-removed", "region": "eu-west-1"}
)
path = "test/test.json"
content = Dict({"test1": "test1", "test2": "test2"})


def test_get_set_options():
    storage.set_options(LOCAL_OPTIONS)
    options = storage.get_options()
    assert options.type == "local", "Options type is correct"
    assert options.location == "output", "Options location is correct"


def test_save():
    data = json.dumps(content, indent=2)
    status = storage.save(path, data)
    assert status, "Local file save reported success"


def test_read_json():
    parsed = storage.read_json(path)
    assert parsed.test1 == content.test1, "Read local file matches saved content"


# Both of these tests are broken because of the GLOBAL state in the
# module file affecting the outcome of each test.

# def test_save_s3():
#     """
#     This test only works if AWS credentials are available..
#     ..and there is an S3 bucket to read/write from.
#     The API call is not mocked.
#     """
#     if "AWS_SECRET_ACCESS_KEY" in os.environ:
#         print(os.environ["AWS_ACCESS_KEY_ID"], sys.stderr)
#         os.environ["FLASK_ENV"] == "production"
#         storage.set_region(REGION)
#         storage.set_options(S3_OPTIONS)
#         status = storage.save(path, json.dumps(content, indent=2))
#         assert status, "S3 put object reported success"


# def test_read_s3():
#     """
#     This test only works if AWS credentials are available..
#     ..and there is an S3 bucket to read/write from.
#     The API call is not mocked.
#     """
#     if "AWS_SECRET_ACCESS_KEY" in os.environ:
#         print(os.environ["AWS_ACCESS_KEY_ID"], sys.stderr)
#         os.environ["FLASK_ENV"] == "production"
#         storage.set_region(REGION)
#         storage.set_options(S3_OPTIONS)
#         parsed = storage.read_json(path)
#         assert parsed.test1 == content.test1, "Read S3 object matches saved content"
