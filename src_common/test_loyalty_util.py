import os

os.environ["EES_AUTH_CLIENT_ID"] = "u2v2hsh07xvju1eex8eh"
os.environ["EES_AUTH_CLIENT_SECRET"] = "tplzi3t8v6okghbrrhts0644dep5ns"
os.environ["EES_API_PREFIX"] = "/2.0"
os.environ["EES_POS_API_HOST"] = "pos.sandbox.uk.eagleeye.com"
os.environ["EES_RESOURCES_API_HOST"] = "resources.sandbox.uk.eagleeye.com"
os.environ["EES_WALLET_API_HOST"] = "wallet.sandbox.uk.eagleeye.com"
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
