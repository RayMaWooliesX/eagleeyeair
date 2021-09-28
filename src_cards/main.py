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
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """ 
    event_sub_types = {"cancel", "replace", "reregister", "deregister"}
    event_data, delivery_attempt = _parse_request(request)

    if event_data["eventType"] != "cards":
        raise RuntimeError("Unexpected event type: " + event_data["eventType"])

    if event_data["eventSubType"] not in event_sub_types:
        raise RuntimeError("Unexpected event sub type: " + event_data["eventSubType"])

    wallet_id = ee.wallet.get_wallet_by_identity_value(event_data["eventDetails"]["profile"]["crn"])["walletId"]
    identities = ee.wallet.get_wallet_identities_by_wallet_id(wallet_id, type='LCN')["results"]

    identity_id = ""
    for identity in identities:
        if identity["value"] == event_data["eventDetails"]["profile"]["account"]["cardNumber"]:
            identity_id = identity["identityId"]
    if identity_id == "":
        raise RuntimeError("LCN number: " 
                        + event_data["eventDetails"]["profile"]["account"]["cardNumber"]
                        + " can't be found in EE.")
    
    if event_data["eventSubType"] == "replace":
        data = _prepare_lcn_payload(event_data["eventDetails"]["profile"]["account"]["cards"]["newCardNumber"])
        ee.wallet.create_wallet_identity(wallet_id,data)

    if event_data["eventSubType"] in ("replace", "cancel"):
        if event_data["eventSubType"]  == "replace":
            cancel_reason = event_data["eventDetails"]["profile"]["account"]["cards"]["replacementReason"].upper()
        else: 
            cancel_reason = event_data["eventDetails"]["profile"]["account"]["cards"]["cancellationReasonDescription"].upper()
        
        if cancel_reason == "LOST":
            ee.wallet.update_wallet_identity_status_lost(wallet_id= wallet_id, identity_id= identity_id)
        elif cancel_reason == "STOLEN":
            ee.wallet.update_wallet_identity_status_stolen(wallet_id= wallet_id, identity_id= identity_id)
        else:
            ee.wallet.update_wallet_identity_status_suspended(wallet_id= wallet_id, identity_id= identity_id)

    return '200'

def _prepare_lcn_payload(lcn_num):
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



    try:
        logging.info("---Logging original message to dead letter topic.")
        error_publisher_client = pubsub_v1.PublisherClient()
        error_topic_path = error_publisher_client.topic_path(os.environ['GCP_PROJECT'], 
                                                            os.environ['error_topic'])
        user = os.environ['FUNCTION_NAME']
        future = error_publisher_client.publish(error_topic_path, event_data.encode("utf-8"),
                                                                        user=user,
                                                                        error = error_message)
        # Wait for the publish future to resolve before exiting.
        while not future.done():
            time.sleep(1)
        logging.info("---Logging original message to dead letter topic completed.")
    except Exception as e:
        logging.error(RuntimeError("!!! There was an error while sending error message to dead letter topic. " ))
        logging.info(traceback.format_exc())
        pass