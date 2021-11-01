'''
This Cloud function is responsible for:
- Parsing data triggered by source pubsub
- Preparing data for the EE API calls.
- Calling EE APIs to update preference
'''

import os
import base64
import hashlib
import time
from datetime import datetime, timezone
import logging
import traceback

import pytz
import json
import requests
import pymongo
from pymongo import MongoClient
from google.cloud import pubsub_v1
from google.cloud import error_reporting
from flask import request

import eagleeyeair as ee

def main_cards(request):
    """ Responds to an HTTP request using data from the request body parsed
    according to the "content-type" header.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    More detail information can be found in the LLD below:
    https://woolworthsdigital.atlassian.net/wiki/spaces/DGDMS/pages/25482592639/Detailed+Design+for+Loyalty+API+integration+of+card+management#Deregister-Card-Event
    """ 
    event_sub_types = {"cancel", "replace", "reregister", "deregister"}
    event_data, delivery_attempt = _parse_request(request)

    if event_data["eventType"] != "cards":
        raise RuntimeError("Unexpected event type: " + event_data["eventType"])

    if event_data["eventSubType"] not in event_sub_types:
        raise RuntimeError("Unexpected event sub type: " + event_data["eventSubType"])

    wallet = ee.wallet.get_wallet_by_identity_value(event_data["eventDetails"]["profile"]["crn"])
    wallet_id = wallet["walletId"]
    identities = ee.wallet.get_wallet_identities_by_wallet_id(wallet_id)["results"]

    lcn = ""
    crn = ""
    hash_crn = ""
    replacing_lcn = ""
    for identity in identities:
        if identity["value"] == event_data["eventDetails"]["profile"]["account"]["cardNumber"]:
            lcn = identity
        if identity["type"] == "CRN":
            crn = identity
        if identity["type"] == "HASH_CRN":
            hash_crn = identity
        if event_data["eventSubType"] == "replace" and identity["value"] == event_data["eventDetails"]["profile"]["account"]["cards"]["newCardNumber"]:
           replacing_lcn = identity
    
    if event_data["eventSubType"] == "replace":
        if replacing_lcn != "":
            data = _prepare_active_lcn_payload(event_data["eventDetails"]["profile"]["account"]["cards"]["newCardNumber"])
            ee.wallet.create_wallet_identity(wallet_id,data)

    if event_data["eventSubType"] in ("replace", "cancel"):
        if event_data["eventSubType"]  == "replace":
            cancel_reason = event_data["eventDetails"]["profile"]["account"]["cards"]["replacementReason"].upper()
        else: 
            cancel_reason = event_data["eventDetails"]["profile"]["account"]["cards"]["cancellationReasonDescription"].upper()
        
        if cancel_reason == "LOST" and lcn["status"] != "LOST":
            ee.wallet.update_wallet_identity_status_lost(wallet_id= wallet_id, identity_id= lcn["identityId"])
        elif cancel_reason == "STOLEN" and lcn["status"] != "STOLEN":
            ee.wallet.update_wallet_identity_status_stolen(wallet_id= wallet_id, identity_id= lcn["identityId"])
        else:
            if lcn["status"] != "SUSPENDED":
                ee.wallet.update_wallet_identity_status_suspended(wallet_id= wallet_id, identity_id= lcn["identityId"])

    if event_data["eventSubType"] == "reregister":
        if wallet["state"] != "EARNBURN":
            ee.wallet.update_wallet_state(wallet_id= wallet_id,data = {"state": "EARNBURN"})
        if wallet["status"] != "ACTIVE":
            ee.wallet.activate_wallet(wallet_id = wallet_id)
        if lcn != "":
            data = _prepare_active_lcn_payload(event_data["eventDetails"]["profile"]["account"]["cards"]["newCardNumber"])
            ee.wallet.create_wallet_identity(wallet_id,data)

    if event_data["eventSubType"] == "deregister":
        if hash_crn["state"] != "CLOSED":
            ee.wallet.update_wallet_identity_state(wallet_id, hash_crn["identityId"],{"state": "CLOSED"})
        if hash_crn["status"] != "TERMINATED":
            ee.wallet.update_wallet_identity_status_terminated(wallet_id, hash_crn["identityId"])
        if lcn != "":
            ee.wallet.delete_wallet_identity(wallet_id, lcn["identityId"])
        if crn != "":
            ee.wallet.delete_wallet_identity(wallet_id, crn["identityId"])
        if wallet["state"] != "CLOSED":
            ee.wallet.update_wallet_state(wallet_id,{"state": "CLOSED"})
        if wallet["status"] != "TERMINATED":
            ee.wallet.terminate_wallet(wallet_id)

    return '200'

def _prepare_active_lcn_payload(lcn_num):
    return {
            "type": "LCN",
            "friendlyName": "Loyalty Card Number",
            "value": lcn_num,
            "state": "REGISTERED",
            "status": "ACTIVE"
            }

def _parse_request(request):
    '''parse the request and return the request data in jason format
    '''
    logging.info('Preparing data for EE request.')
    envelope = request.get_json()
    message = envelope['message']
    delivery_attempt = envelope['deliveryAttempt']
    event_data_str = base64.b64decode(message['data'])
    event_data = json.loads(event_data_str)
    logging.info('Completed preparing data for EE request.')
    return event_data, delivery_attempt

