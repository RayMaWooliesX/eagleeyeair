
import os
os.environ["EES_AUTH_CLIENT_ID"] = "u2v2hsh07xvju1eex8eh"
os.environ["EES_AUTH_CLIENT_SECRET"] = "tplzi3t8v6okghbrrhts0644dep5ns"
os.environ["EES_API_PREFIX"] = "/2.0"
os.environ["EES_POS_API_HOST"] = "pos.sandbox.uk.eagleeye.com"
os.environ["EES_RESOURCES_API_HOST"] = "resources.sandbox.uk.eagleeye.com"
os.environ["EES_WALLET_API_HOST"] = "wallet.sandbox.uk.eagleeye.com"
os.environ["ee_memberSchemeId"] = "850545"

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

crn_register = "999-crn-account-register" + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
crn_hash_register = hashlib.sha256(crn_register.encode('utf-8')).hexdigest()
lcn_register = "888-lcn-account_register" + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
print(crn_register)

@mock.patch("main._parse_request", return_value = ({
  "eventType": "accounts",
  "eventSubType": "register",
  "operation": "create",
  "eventDetails": {
    "source": {
      "code": 1,
      "name": "CPORTAL"
    },
    "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341",
    "publishedAt": "2018-11-11T11:01:59+11:11",
    "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004",
    "profile": {
      "crn": crn_register,
      "crnHash": crn_hash_register,
      "account": {
        "accountType": {
          "code": 1002,
          "name": "EDR"
        },
        "cardNumber": lcn_register
      }
    }
  }
},1))
def test_main_accounts_register(mock_parse_request):
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_accounts(data) == "200"