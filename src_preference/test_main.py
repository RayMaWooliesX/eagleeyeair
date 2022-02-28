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

from unittest import mock
import main

import eagleeyeair


@mock.patch(
    "main.parse_request",
    return_value=(
        {
            "eventType": "preferences",
            "eventSubType": "liquor",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "5cffdbe0-1912-42eb-8a60-c12b34ded5c6",
                "profile": {
                    "crn": "999142021141236899440",
                    "crnHash": "b73bb1dde9bc512ad8e852e4b9c7789bba986fd64824637a49c6cd06e5aa3d03",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "888142021141236899440",
                        "preferences": [
                            {
                                "id": 1042,
                                "name": "Liquor offers and promotions",
                                "value": True,
                            },
                            {
                                "id": 1024,
                                "name": "Unsubscribe All",
                                "value": False,
                            },
                            {
                                "id": 39,
                                "name": "Save for later",
                                "value": "QantasPoints",
                            },
                            {"id": 30101, "name": "Woolworths", "value": True},
                            {"id": 30102, "name": "BigW", "value": True},
                            {"id": 30103, "name": "BWS", "value": True},
                        ],
                    },
                },
            },
        },
        1,
    ),
)
def test_main_preference(mock_parse_request):
    data = {"deliveryAttempt": 1, "message": {}}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_preference(data) == "200"


def test_update_segmentation_unsubscribe_all():
    event_data = {
        "eventType": "preferences",
        "eventSubType": "liquor",
        "operation": "update",
        "eventDetails": {
            "source": {"code": 1, "name": "CPORTAL"},
            "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
            "publishedAt": "2018-11-11T11:01:59+11:11",
            "correlationId": "5cffdbe0-1912-42eb-8a60-c12b34ded5c6",
            "profile": {
                "crn": "999142021141236899440",
                "crnHash": "b73bb1dde9bc512ad8e852e4b9c7789bba986fd64824637a49c6cd06e5aa3d03",
                "account": {
                    "accountType": {"code": 1002, "name": "EDR Card"},
                    "cardNumber": "888142021141236899440",
                    "preferences": [
                        {
                            "id": 1024,
                            "name": "Unsubscribe All",
                            "value": True,
                        },
                        {"id": 30102, "name": "BigW", "value": False},
                    ],
                },
            },
        },
    }
    in_memberOfferExclusions = {
        "name": "memberOfferExclusions",
        "segments": [
            {
                "labels": ["Member Offer Exclusions"],
                "data": {"0047": "No Liquor Offers"},
            }
        ],
    }
    in_memberPreferences = {
        "name": "memberPreferences",
        "segments": [
            {
                "labels": ["Member Preferences"],
                "data": {
                    "0033": "eReceipt - Supermarkets & Metro",
                    "0037": "eReceipt - Big W",
                    "0035": "eReceipt - BWS",
                    "0105": "SFL Christmas",
                },
            }
        ],
    }
    memberOfferExclusions, memberPreferences = main._update_segmentation(
        event_data, in_memberOfferExclusions, in_memberPreferences
    )

    assert memberOfferExclusions == {
        "name": "memberOfferExclusions",
        "segments": [
            {
                "labels": ["Member Offer Exclusions"],
                "data": {},
            }
        ],
    }
    assert memberPreferences == {
        "name": "memberPreferences",
        "segments": [
            {
                "labels": ["Member Preferences"],
                "data": {
                    "0033": "eReceipt - Supermarkets & Metro",
                    "0035": "eReceipt - BWS",
                    "0105": "SFL Christmas",
                },
            }
        ],
    }


def test_update_segmentation_liquor():
    event_data = {
        "eventType": "preferences",
        "eventSubType": "liquor",
        "operation": "update",
        "eventDetails": {
            "source": {"code": 1, "name": "CPORTAL"},
            "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
            "publishedAt": "2018-11-11T11:01:59+11:11",
            "correlationId": "5cffdbe0-1912-42eb-8a60-c12b34ded5c6",
            "profile": {
                "crn": "999142021141236899440",
                "crnHash": "b73bb1dde9bc512ad8e852e4b9c7789bba986fd64824637a49c6cd06e5aa3d03",
                "account": {
                    "accountType": {"code": 1002, "name": "EDR Card"},
                    "cardNumber": "888142021141236899440",
                    "preferences": [
                        {
                            "id": 1024,
                            "name": "Unsubscribe All",
                            "value": False,
                        },
                        {
                            "id": 1042,
                            "name": "Liquor offers and promotions",
                            "value": True,
                        },
                        {"id": 30102, "name": "BigW", "value": False},
                    ],
                },
            },
        },
    }
    in_memberOfferExclusions = {
        "name": "memberOfferExclusions",
        "segments": [
            {
                "labels": ["Member Offer Exclusions"],
                "data": {},
            }
        ],
    }
    in_memberPreferences = {
        "name": "memberPreferences",
        "segments": [
            {
                "labels": ["Member Preferences"],
                "data": {
                    "0033": "eReceipt - Supermarkets & Metro",
                    "0037": "eReceipt - Big W",
                    "0035": "eReceipt - BWS",
                    "0105": "SFL Christmas",
                },
            }
        ],
    }
    memberOfferExclusions, memberPreferences = main._update_segmentation(
        event_data, in_memberOfferExclusions, in_memberPreferences
    )

    assert memberOfferExclusions == {
        "name": "memberOfferExclusions",
        "segments": [
            {
                "labels": ["Member Offer Exclusions"],
                "data": {"0047": "No Liquor Offers"},
            }
        ],
    }
    assert memberPreferences == {
        "name": "memberPreferences",
        "segments": [
            {
                "labels": ["Member Preferences"],
                "data": {
                    "0033": "eReceipt - Supermarkets & Metro",
                    "0035": "eReceipt - BWS",
                    "0105": "SFL Christmas",
                },
            }
        ],
    }
