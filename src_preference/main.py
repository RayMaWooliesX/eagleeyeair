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

import pytz
import json
import logging
import traceback
import requests
from google.cloud import pubsub_v1
from google.cloud import error_reporting
import jsonschema

import eagleeyeair as ee

def main_preference(request):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
        event (dict):  The dictionary with data specific to this type of
        event. The `data` field contains the PubsubMessage message. The
        `attributes` field will contain custom attributes if there are any.
        context (google.cloud.functions.Context): The Cloud Functions event
        metadata. The `event_id` field contains the Pub/Sub message ID. The
        `timestamp` field contains the publish time.
    """
    event_data, delivery_attempt = _parse_request(request)
    wallet = ee.wallet.get_wallet_by_identity_value(event_data["eventDetails"]["profile"]["crn"])
    consumer = ee.wallet.get_wallet_consumer(wallet["walletId"])
    preference_payload = _prepare_consumer_payload(event_data, consumer)

    ee.wallet.update_wallet_consumer(wallet["walletId"], consumer["consumerId"], preference_payload)

    return "200"

def _parse_request(request):
    '''parse the request and return the request data in jason format
    '''
    logging.info('Preparing data for EE request.')
    envelope = request.get_json()
    message = envelope['message']
    delivery_attempt = envelope['deliveryAttempt']
    event_data_str = base64.b64decode(message['data'])
    event_data = json.loads(event_data_str)
    _validate_payload_format(event_data)

    logging.info('Completed preparing data for EE request.')
    return event_data, delivery_attempt

def _validate_payload_format(event_data):
    "this function validate the message payload format againt the schema"
    with open('message-schema.json', 'r') as file:
        schema = json.load(file)
    
    jsonschema.validate(instance=event_data, schema=schema)

def _prepare_consumer_payload(event_data, consumer):

    memberOfferExclusions = {}
    memberPreferences = {}

    if not consumer["data"]:
        pass
    else:
        if not consumer["data"].get("segmentation"):
            for segmentation in consumer["data"]["segmentation"]:
                if segmentation["name"] == "memberOfferExclusions":
                    memberOfferExclusions = segmentation
                elif segmentation["name"] == "memberPreferences":
                    memberPreferences = segmentation

    if not memberOfferExclusions: 
        memberOfferExclusions=  {
                        "name": "memberOfferExclusions",
                        "segments": [
                            {
                                "labels": [
                                    "Member Offer Exclusions"
                                ],
                                "data": {
                                }
                            }
                        ]
                    }
    if not memberPreferences:
        memberPreferences = {
                "name": "memberPreferences",
                "segments": [
                    {
                        "labels": [
                            "Member Preferences"
                        ],
                        "data": {
                        }
                    }
                ]
            }

    memberOfferExclusions, memberPreferences = _update_segmentation(event_data,memberOfferExclusions, memberPreferences)
    
    payload = {
                "friendlyName": "Sample Consumer",
                "data": {
                    "segmentation": [memberOfferExclusions,memberPreferences]}
               }

    return payload

def _update_segmentation(event_data, memberOfferExclusions, memberPreferences):
    '''update the segment memberOfferExclusions, memberPreferences with the data from request'''
    # functions to update the dict
    memberOfferExclusions_update_func = memberOfferExclusions["segments"][0]["data"].update
    memberOfferExclusions_pop_func = memberOfferExclusions["segments"][0]["data"].pop
    memberPreferences_update_func = memberPreferences["segments"][0]["data"].update
    memberPreferences_pop_func = memberPreferences["segments"][0]["data"].pop

    # this dictionary maps preference id and value to segment id, value in EE and the function used to update them
    OP_DICT = {"1042-True": [{memberOfferExclusions_update_func:{"0047": "No Liquor Offers"}}],
               "1042-False":[{memberOfferExclusions_pop_func: "0047"}],
               "30101-True":[{memberPreferences_update_func: {"0033": "eReceipt - Supermarkets & Metro"}}],
               "30101-False":[{memberPreferences_pop_func: "0033"}],
               "30102-True":[{memberPreferences_update_func: {"0037": "eReceipt - Big W"}}],
               "30102-False":[{memberPreferences_pop_func: "0037"}],
               "30103-True":[{memberPreferences_update_func: {"0035": "eReceipt - BWS"}}],
               "30103-False":[{memberPreferences_pop_func: "0035"}],
               "39-Automatic":[{memberPreferences_pop_func: "0104"}, {memberPreferences_pop_func: "0105"}],
               "39-QantasPoints":[{memberPreferences_update_func: {"0104": "SFL QFF"}}, {memberPreferences_pop_func: "0105"}],
               "39-Christmas":[{memberPreferences_update_func: {"0105": "SFL Christmas"}},{memberPreferences_pop_func: "0104"}]
    }

    for preference in event_data["eventDetails"]["profile"]["account"]["preferences"]:
        operations = OP_DICT.get(str(preference["id"]) + "-" + str(preference["value"]))
        if not operations:
            raise RuntimeError("Incorrect preference id or value! id: "  + str(preference["id"])
                                + "; value: " + preference["value"])
        for op in operations:
            func = list(op.keys())[0]
            param = list(op.values())[0]
            if func.__name__ == "pop":
                func(param, None)
            else:
                func(param)


    return memberOfferExclusions, memberPreferences

