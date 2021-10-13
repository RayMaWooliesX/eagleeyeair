
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
  # set up data for replace/cancel
  eagleeyeair.wallet.update_wallet_identity_status_active("114413159", "87930461")
  eagleeyeair.wallet.update_wallet_identity_status_active("114305351", "87863093")

  # set the wallet and identity status/state for reregister
  eagleeyeair.wallet.update_wallet_state(wallet_id= "114453866", data = {"state": "CLOSED"})
  eagleeyeair.wallet.suspend_wallet("114453866")


except Exception as e:
  print(e)

@mock.patch("main._parse_request", return_value = ({
    "eventType": "cards",
    "eventSubType": "cancel",
    "operation": "update",
    "eventDetails": {
      "source": {
        "code": 1,
        "name": "CPORTAL"
      },
      "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
      "publishedAt": "2018-11-11T11:01:59+11:11",
      "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
      "profile": {
        "crn": "622589b75ea8cb24c3d3b505379b26fe",
        "crnHash": "7a30398d3e11bfecb7c9e7b014adfgdfg6463c768cc35b942d6ec44af66f185",
        "account": {
          "accountType": {
            "code": 1002,
            "name": "EDR"
          },
          "cardNumber": "d309d83e9f408633597ec19da315880c",
          "cards": {
            "cancelledCardNumber": "d309d83e9f408633597ec19da315880c",
            "cancellationReasonCode": "123",
            "cancellationReasonDescription": "LOST",
            "cancellationComment": "Not getting many offers",
            "cancellationRequestDatetime": "2018-11-11T11:01:59+11:11"
          }
        }
      }
    }
  },1))
def test_main_cards_cancel(mock_parse_request):
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"


@mock.patch("main._parse_request", return_value = ({
    "eventType": "cards",
    "eventSubType": "replace",
    "operation": "update",
    "eventDetails": {
      "source": {
        "code": 1,
        "name": "CPORTAL"
      },
      "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
      "publishedAt": "2018-11-11T11:01:59+11:11",
      "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
      "profile": {
        "crn": "9942cc5d2bfee0e540d5801a483aa882",
        "crnHash": "7a30398d3e11bfecb7c9e7b014adfgdfg6463c768cc35b942d6ec44af66f185",
        "account": {
          "accountType": {
            "code": 1002,
            "name": "EDR"
          },
          "cardNumber": "a90ce8514780380e5cd752ae6151d620",
          "cards": {
            "oldCardNumber": "a90ce8514780380e5cd752ae6151d620",
            "newCardNumber": "a90ce8514780380e5cd752ae6151d620new"+datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"),
            "replacementReason": "Lost"
          }
        }
      }
    }
  },1))
def test_main_cards_replace(mock_parse_request):
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"


@mock.patch("main._parse_request", return_value = ({
    "eventType": "cards",
    "eventSubType": "reregister",
    "operation": "update",
    "eventDetails": {
      "source": {
        "code": 1,
        "name": "CPORTAL"
      },
      "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
      "publishedAt": "2018-11-11T11:01:59+11:11",
      "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
      "profile": {
        "crn": "49f1ec5fb2384d0e9b51d249a0629da8",
        "crnHash": "26249410976150692bb2056107ba6eb62c6d8f3746ffeb38cf374f3a3de9b1b8",
        "account": {
          "accountType": {
            "code": 1002,
            "name": "EDR"
          },
          "cardNumber": "4bc8492fbf0c1d4ecbbea980a9054a56",
          "cards": {
            "newCardNumber": "4bc8492fbf0c1d4ecbbea980a9054a56-reregister"  + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
          }
        }
      }
    }
},1))
def test_main_cards_reregister(mock_parse_request):
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_cards(data) == "200"