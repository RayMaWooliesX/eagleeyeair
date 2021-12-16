import unittest
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
