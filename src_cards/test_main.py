import os

os.environ["EES_AUTH_CLIENT_ID"] = "u2v2hsh07xvju1eex8eh"
os.environ["EES_AUTH_CLIENT_SECRET"] = "tplzi3t8v6okghbrrhts0644dep5ns"
os.environ["EES_API_PREFIX"] = "/2.0"
os.environ["EES_POS_API_HOST"] = "pos.sandbox.uk.eagleeye.com"
os.environ["EES_RESOURCES_API_HOST"] = "resources.sandbox.uk.eagleeye.com"
os.environ["EES_WALLET_API_HOST"] = "wallet.sandbox.uk.eagleeye.com"

from unittest import mock
from datetime import datetime

import eagleeyeair
import main

try:
    # set up data for cancel
    eagleeyeair.wallet.update_wallet_identity_status_active("115103065", "88581976")
    eagleeyeair.wallet.update_wallet_consumer(
        "115103065",
        "18092294",
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
    eagleeyeair.wallet.update_wallet_identity_status_active("115205616", "88682691")

    # set the wallet and identity status/state for reregister
    eagleeyeair.wallet.update_wallet_state(
        wallet_id="115205634", data={"state": "CLOSED"}
    )
    eagleeyeair.wallet.suspend_wallet("115205634")

except Exception as e:
    print(e)


@mock.patch(
    "main.parse_request",
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
                    "crn": "999152021161217433918",
                    "crnHash": "dd5d9273336cecfe867653f4e720c5642363128b4c176ed31cb3a64c922184a0",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "888152021161217433918",
                        "cardEventDetail": {
                            "cancelledCardNumber": "888152021161217433918",
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
    "main.parse_request",
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
                    "crn": "999162021091248967073",
                    "crnHash": "0c0d312b60dd309af44c11a74bb43d9f1d6c8916e971e00e2f67c233acb4ec8e",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "888162021091248967073",
                        "cardEventDetail": {
                            "oldCardNumber": "888162021091248967073",
                            "newCardNumber": "888162021091248967073new"
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
    "main.parse_request",
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
                    "crn": "999162021091245926065",
                    "crnHash": "b3fda621058bfdae3322d8110fbfca1966294dc94b7fc001339986c7670bae4a",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "888162021091245926065",
                        "cardEventDetail": {
                            "newCardNumber": "888162021091245926065-reregister"
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
    "main.parse_request",
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
                    "crn": "999162021111200990217",
                    "crnHash": "fc1304e481f4f49aaa74aecf9eb7473a694e118c4c53a3a36098547947bcc31a",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "888162021111200990217",
                        "cardEventDetail": {
                            "deregisteredCardNumber": "888162021111200990217"
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
