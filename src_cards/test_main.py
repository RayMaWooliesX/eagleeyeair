
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

logger = logging.getLogger('eagle_eye_api')
logger.setLevel(logging.DEBUG)




@mock.patch("main._parse_request", return_value = ({
            "eventType": "cards",
            "eventSubType": "cancel",
            "operation": "delete",
            "eventDetails": {
                "source": {
                "code": 1,
                "name": "CPORTAL"
                },
                "trackingId": "a9cee8c2-72a5-44b7-bca6-e15d4f91dc8d",
                "correlationId": "4b5b39c2-d012-431d-8b40-d0e77ffa9f26",
                "publishedAt": "2021-09-07T05:08:34UTC",
                "profile": {
                "crn": "3fe8cdf24f4bb13d5d56c94f6f52290a",
                "crnHash": "559256253_hash",
                "account": {
                    "accountType": {
                    "code": 1002,
                    "name": "EDR"
                    },
                    "cardNumber": "9e98c906459a7e0b5272913d3a58589c",
                    "cards": {}
                }
                }
            }
            },1))
def test_main_cards(mock_parse_request):
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    
    assert main.main_cards(req) == "200"



@mock.patch("main._parse_request", return_value = ({
  "eventType": "cards",
  "eventSubType": "replace",
  "operation": "delete",
  "eventDetails": {
    "source": {
      "code": 1,
      "name": "CPORTAL"
    },
    "trackingId": "a9cee8c2-72a5-44b7-bca6-e15d4f91dc8d",
    "correlationId": "4b5b39c2-d012-431d-8b40-d0e77ffa9f26",
    "publishedAt": "2021-09-07T05:08:34UTC",
    "profile": {
      "crn": "9942cc5d2bfee0e540d5801a483aa882",
      "crnHash": "3d05e22d0c398e642a3b5ffe815461306b99c901ee57682a52b0827c3c270e08",
      "account": {
        "accountType": {
          "code": 1002,
          "name": "EDR"
        },
        "cardNumber": "a90ce8514780380e5cd752ae6151d620",
        "newCardNumber": "a90ce8514780380e5cd752ae6151d620new",
        "cards": {}
      }
    }
  }
},1))
def test_main_cards_replace(mock_parse_request):
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    
    assert main.main_cards(req) == "200"

