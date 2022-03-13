import os

os.environ["EES_AUTH_CLIENT_ID"] = "u2v2hsh07xvju1eex8eh"
os.environ["EES_AUTH_CLIENT_SECRET"] = "tplzi3t8v6okghbrrhts0644dep5ns"
os.environ["EES_API_PREFIX"] = "/2.0"
os.environ["EES_POS_API_HOST"] = "pos.sandbox.uk.eagleeye.com"
os.environ["EES_RESOURCES_API_HOST"] = "resources.sandbox.uk.eagleeye.com"
os.environ["EES_WALLET_API_HOST"] = "wallet.sandbox.uk.eagleeye.com"

import hashlib
from unittest import mock
from datetime import datetime

import eagleeyeair
import main
import loyalty_util

try:
    # set up data for cancel
    eagleeyeair.wallet.update_wallet_identity_status_active("115103065", "88581976")
except Exception as e:
    print(e)
try:
    eagleeyeair.wallet.update_wallet_identity_status_active("128982941", "102948081")
except Exception as e:
    print(e)
try:
    eagleeyeair.wallet.update_wallet_identity_status_active("128983011", "102948221")
except Exception as e:
    print(e)
try:
    eagleeyeair.wallet.update_wallet_identity_status_active("128983050", "102948300")
except Exception as e:
    print(e)
try:
    "", "", ""
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
except Exception as e:
    print(e)
try:
    # set up data for replace
    eagleeyeair.wallet.update_wallet_identity_status_active("115205616", "88682691")
except Exception as e:
    print(e)
try:
    # set the wallet and identity status/state for reregister
    eagleeyeair.wallet.update_wallet_state(
        wallet_id="115205634", data={"state": "CLOSED"}
    )
except Exception as e:
    print(e)
try:
    eagleeyeair.wallet.suspend_wallet("115205634")
except Exception as e:
    print(e)


# preparing data for deregister
# card to be deregister
crn_deregister = "777" + datetime.now().strftime("%d%Y%H%m%S%f")
crn_hash_deregister = hashlib.sha256(crn_deregister.encode("utf-8")).hexdigest()
lcn_deregister = "666" + datetime.now().strftime("%d%Y%H%m%S%f")
print("crn_deregister: ", crn_deregister)
print("lcn_deregister: ", lcn_deregister)
wallet_deregister = eagleeyeair.wallet.create_wallet_and_wallet_identities(
    {
        "state": "EARNBURN",
        "status": "ACTIVE",
        "type": "MEMBER",
        "friendlyName": "Test Wallet",
        "identities": [
            {
                "type": "LCN",
                "friendlyName": "Loyalty Card Number",
                "value": lcn_deregister,
                "status": "ACTIVE",
                "state": "REGISTERED",
                "meta": {"registered": "app"},
            },
            {
                "type": "CRN",
                "friendlyName": "Customer Referenence Number",
                "value": crn_deregister,
            },
            {
                "type": "HASH_CRN",
                "friendlyName": "Hashed Customer Referenence Number",
                "value": crn_hash_deregister,
            },
        ],
        "meta": {"sample": "metadata", "key": "value"},
    }
)
print(wallet_deregister)
consumer_deregister = eagleeyeair.wallet.create_wallet_consumer(
    wallet_deregister["walletId"],
    {
        "friendlyName": "Sample Consumer",
        "type": "DEFAULT",
        "data": {
            "dimension": [
                {"label": "customerType", "value": "1002"},
                {"label": "noLiquorOffers", "value": False},
                {"label": "preferredStoreNumber", "value": "1800"},
                {"label": "redemptionSetting", "value": "Automatic Saving"},
                {"label": "staffDivisionCode", "value": "1005"},
            ]
        },
    },
)
print(consumer_deregister)
# card to be linked to the deregistered card
crn_deregister_link = "77" + datetime.now().strftime("%d%Y%H%m%S%f")
crn_hash_deregister_link = hashlib.sha256(
    crn_deregister_link.encode("utf-8")
).hexdigest()
lcn_deregister_link = "66" + datetime.now().strftime("%d%Y%H%m%S%f")
print("crn_deregister_link: ", crn_deregister_link)
print("lcn_deregister_link: ", lcn_deregister_link)
wallet_deregister_link = eagleeyeair.wallet.create_wallet_and_wallet_identities(
    {
        "state": "EARNBURN",
        "status": "ACTIVE",
        "type": "MEMBER",
        "friendlyName": "Test Wallet",
        "identities": [
            {
                "type": "LCN",
                "friendlyName": "Loyalty Card Number",
                "value": lcn_deregister_link,
                "status": "ACTIVE",
                "state": "REGISTERED",
                "meta": {"registered": "app"},
            },
            {
                "type": "CRN",
                "friendlyName": "Customer Referenence Number",
                "value": crn_deregister_link,
            },
            {
                "type": "HASH_CRN",
                "friendlyName": "Hashed Customer Referenence Number",
                "value": crn_hash_deregister_link,
            },
        ],
        "meta": {"sample": "metadata", "key": "value"},
    }
)
print(wallet_deregister_link)
consumer_deregister_link = eagleeyeair.wallet.create_wallet_consumer(
    wallet_deregister_link["walletId"],
    {
        "friendlyName": "Sample Consumer",
        "type": "DEFAULT",
        "data": {
            "dimension": [
                {"label": "customerType", "value": "1002"},
                {"label": "noLiquorOffers", "value": False},
                {"label": "preferredStoreNumber", "value": "1800"},
                {"label": "redemptionSetting", "value": "Automatic Saving"},
                {"label": "staffDivisionCode", "value": "1005"},
            ]
        },
    },
)
print(consumer_deregister_link)

loyalty_util.link_cards(lcn_deregister, lcn_deregister_link)


@mock.patch(
    "main.parse_request",
    return_value=(
        {
            "eventType": "cards",
            "eventSubType": "link",
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
                            "primaryCardNumber": "888152021161217433918",
                            "secondaryCardNumber": "666112022100336460831",
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_link_for_cancel_1(mock_parse_request):
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
            "eventSubType": "link",
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
                            "primaryCardNumber": "888152021161217433918",
                            "secondaryCardNumber": "666112022100304641892",
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_link_for_cancel_2(mock_parse_request):
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
            "eventSubType": "link",
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
                            "primaryCardNumber": "888152021161217433918",
                            "secondaryCardNumber": "666112022100309075178",
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_link_for_cancel_3(mock_parse_request):
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
            "eventSubType": "cancel",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
                "profile": {
                    "crn": "777112022100336459231",
                    "crnHash": "e1da6f2b8fc7c27292d0012393b29a9c5623e867848de513c044f82de4b2ed65",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "666112022100336460831",
                        "cardEventDetail": {
                            "cancelledCardNumber": "666112022100336460831",
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
def test_main_cards_cancel_secondary(mock_parse_request):
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
            "eventSubType": "cancel",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
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
def test_main_cards_cancel_primary(mock_parse_request):
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
                    "crn": "777112022100309075178",
                    "crnHash": "387055aaf088b1c5c5825edc91f474fe488da31b5e555c19f509c573c334a616",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "666112022100309075178",
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
                    "crn": crn_deregister,
                    "crnHash": crn_hash_deregister,
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": lcn_deregister,
                        "cardEventDetail": {"deregisteredCardNumber": lcn_deregister},
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


@mock.patch(
    "main.parse_request",
    return_value=(
        {
            "eventType": "cards",
            "eventSubType": "link",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
                "profile": {
                    "crn": "777082022140258367737",
                    "crnHash": "d5a69f10552071da51c7c61a391f06a7a01420ca213a57d95927110d6ddb828d",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "666082022140258367737",
                        "cardEventDetail": {
                            "primaryCardNumber": "666082022140258367737",
                            "secondaryCardNumber": "666082022140248219742",
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_link(mock_parse_request):
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
            "eventSubType": "unlink",
            "operation": "update",
            "eventDetails": {
                "source": {"code": 1, "name": "CPORTAL"},
                "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
                "publishedAt": "2018-11-11T11:01:59+11:11",
                "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
                "profile": {
                    "crn": "3300000000034535748",
                    "crnHash": "7a30398d3e11bfecb7c9e7b014adfgdfg6463c768cc35b942d6ec44af66f185",
                    "account": {
                        "accountType": {"code": 1002, "name": "EDR Card"},
                        "cardNumber": "9355049379329",
                        "cardEventDetail": {
                            "primaryCardNumber": "666082022140258367737",
                            "secondaryCardNumber": "666082022140248219742",
                        },
                    },
                },
            },
        },
        1,
    ),
)
def test_main_cards_unlink(mock_parse_request):
    data = {
        "deliveryAttempt": 1,
        "message": {},
        "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub",
    }
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"
