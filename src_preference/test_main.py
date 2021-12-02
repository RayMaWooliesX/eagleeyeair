
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


@mock.patch("main._parse_request", return_value = ({
  "eventType": "preferences",
  "eventSubType": "liquor",
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
      "crn": "5f8eb7a691e34dc92e99c683a4daa5d1",
      "crnHash": "53b826a7bf79256a18562333696c8207a8c4427e63e12fcc5336a01486511a17",
      "account": {
        "accountType": {
          "code": 1002,
          "name": "EDR"
        },
        "cardNumber": "2f57c7caa8b7487c95914b8dc1851102",
        "preferences": [
          {
            "id": 1042,
            "name": "Liquor offers and promotions",
            "value": False
          },
          {
            "id": 39,
            "name": "Save for later",
            "value": "QantasPoints"
          },          
          {
            "id": 30101,
            "name": "Woolworths",
            "value": True
          },
          {
            "id": 30102,
            "name": "BigW",
            "value": True
          },
          {
            "id": 30103,
            "name": "BWS",
            "value": True
          }
        ]
      }
    }
  }
},1))
def test_main_preference(mock_parse_request):
    data = {'deliveryAttempt': 1, 'message': {}}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)

    assert main.main_preference(data) == "200"

