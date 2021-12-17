import os

os.environ[
    "MONGO_API_LOGGING_URL"
] = "https://apigee-test.api-wr.com/wx/v2/member/preferences/mongo"

os.environ["MONGO_API_LOGGING_CLIENT_ID"] = "hrANvT98mnUo2fPXIZlAXEEO9u9VNihA"

from loyalty_util import mongodb_logging


def test_logging():
    r = mongodb_logging(
        "update",
        True,
        200,
        "message",
        "5cffdbe0-1912-42eb-8a60-c12b34ded5c6",
    )

    assert r == 200
