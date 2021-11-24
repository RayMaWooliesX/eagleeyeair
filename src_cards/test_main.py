import os

os.environ["EES_AUTH_CLIENT_ID"] = "u2v2hsh07xvju1eex8eh"
os.environ["EES_AUTH_CLIENT_SECRET"] = "tplzi3t8v6okghbrrhts0644dep5ns"
os.environ["EES_API_PREFIX"] = "/2.0"
os.environ["EES_POS_API_HOST"] = "pos.sandbox.uk.eagleeye.com"
os.environ["EES_RESOURCES_API_HOST"] = "resources.sandbox.uk.eagleeye.com"
os.environ["EES_WALLET_API_HOST"] = "wallet.sandbox.uk.eagleeye.com"

import unittest
from unittest import mock
from requests.api import patch
from requests.models import Response
import main
import base64
import hashlib
import time
from pymongo import MongoClient
from pymongo.collection import Collection
from flask import Flask
import requests
import logging
from datetime import datetime

import eagleeyeair

try:
    # set up data for cancel
    eagleeyeair.wallet.update_wallet_identity_status_active("114413159", "87930461")
    eagleeyeair.wallet.update_wallet_consumer(
        "114413159",
        "18088672",
        {
            "friendlyName": "Sample Consumer",
            "data": {
                "segmentation": [
                    {
                        "name": "localEnvironmentSegments",
                        "segments": [
                            {
                                "labels": ["Local Environment Segments"],
                                "data": {"0090": "Layby Modify Txn"},
                            }
                        ],
                    },
                    {
                        "name": "localTargetSegments",
                        "segments": [
                            {
                                "labels": ["Local Target Segments"],
                                "data": {"0005": "Staff Discount Card"},
                            }
                        ],
                    },
                    {
                        "name": "memberOfferTarget",
                        "segments": [
                            {
                                "labels": ["Member Offer Target"],
                                "data": {
                                    "0062": "BWS Staff",
                                    "0063": "Big W Staff",
                                    "0101": "EDR Registered card",
                                },
                            }
                        ],
                    },
                    {
                        "name": "memberOfferExclusions",
                        "segments": [
                            {
                                "labels": ["Member Offer Exclusions"],
                                "data": {"0047": "No Liquor Offers"},
                            }
                        ],
                    },
                    {
                        "name": "memberPreferences",
                        "segments": [
                            {
                                "labels": ["Member Preferences"],
                                "data": {
                                    "0033": "eReceipt - Supermarkets & Metro",
                                    "0035": "eReceipt - BWS",
                                    "0037": "eReceipt - Big W",
                                    "0104": "SFL QFF",
                                },
                            }
                        ],
                    },
                ]
            },
        },
    )
    # set up data for replace
    eagleeyeair.wallet.update_wallet_identity_status_active("114305351", "87863093")

    # set the wallet and identity status/state for reregister
    eagleeyeair.wallet.update_wallet_state(
        wallet_id="114801331", data={"state": "CLOSED"}
    )
    eagleeyeair.wallet.suspend_wallet("114801331")

except Exception as e:
    print(e)


@mock.patch(
    "main._parse_request",
    return_value=(
        {
            "eventType": "cards",
            "eventSubType": "cancel",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
                "profile": {
                    "crn": "622589b75ea8cb24c3d3b505379b26fe",
                    "crnHash": "94b43035b41b54fea20c7e8bea4e5c43cc3a6fc9137a41c1d330f1e481c5c7d5",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR"},
                        "cardNumber": "d309d83e9f408633597ec19da315880c",
                        "cards": {
                            "cancelledCardNumber": "d309d83e9f408633597ec19da315880c",
                            "cancellationReasonCode": "123",
                            "cancellationReasonDescription": "LOST",
                            "cancellationComment": "Not getting many offers",
                            "cancellationRequestDatetime": "2018-11-11T11:01:59+11:11",
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_cancel(mock_parse_request):
    data = {
        "deliveryAttempt": 1,
        "message": {},
        "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub",
    }
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"


@mock.patch(
    "main._parse_request",
    return_value=(
        {
            "eventType": "cards",
            "eventSubType": "replace",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
                "profile": {
                    "crn": "9942cc5d2bfee0e540d5801a483aa882",
                    "crnHash": "3d05e22d0c398e642a3b5ffe815461306b99c901ee57682a52b0827c3c270e08",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR"},
                        "cardNumber": "a90ce8514780380e5cd752ae6151d620",
                        "cards": {
                            "oldCardNumber": "a90ce8514780380e5cd752ae6151d620",
                            "newCardNumber": "a90ce8514780380e5cd752ae6151d620new"
                            + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                            "replacementReason": "Lost",
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_replace(mock_parse_request):
    data = {
        "deliveryAttempt": 1,
        "message": {
            "data": "eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=",
            "messageId": "2754332662377047",
            "message_id": "2754332662377047",
            "publishTime": "2021-08-01T13:48:51.299Z",
            "publish_time": "2021-08-01T13:48:51.299Z",
        },
        "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub",
    }
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"


@mock.patch(
    "main._parse_request",
    return_value=(
        {
            "eventType": "cards",
            "eventSubType": "reregister",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
                "profile": {
                    "crn": "c78a09b2d48445e0bc7a233257984fdb",
                    "crnHash": "53e23eb30f9f9d55da90d3836fde4599acff88860cc2c97819bc5e5bf350089f",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR"},
                        "cardNumber": "476161f03910f2bc459c9d98c8508d4c",
                        "cards": {
                            "newCardNumber": "476161f03910f2bc459c9d98c8508d4c-reregister"
                            + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_reregister(mock_parse_request):
    data = {
        "deliveryAttempt": 1,
        "message": {},
        "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub",
    }
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"


@mock.patch(
    "main._parse_request",
    return_value=(
        {
            "eventType": "cards",
            "eventSubType": "deregister",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
                "profile": {
                    "crn": "b9c82ef7bf55b08a609ed89f6b20bb4f",
                    "crnHash": "1d40285eb9758aad6d18a449d6602af710c428b753f5f3c3ce38adad284b4f99",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR"},
                        "cardNumber": "5d7e27763c60c85cc4acfc8644d1257d",
                        "cards": {
                            "deregisteredCardNumber": "5d7e27763c60c85cc4acfc8644d1257d"
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_deregister(mock_parse_request):
    data = {
        "deliveryAttempt": 1,
        "message": {},
        "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub",
    }
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"
