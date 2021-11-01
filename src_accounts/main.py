'''
This Cloud function is responsible for:
- Parsing data triggered by source pubsub
- Preparing data for the EE API calls.
- Calling EE APIs to update preference
'''

import os
import base64
import time
from datetime import datetime, timezone
import logging
import traceback

import json
from eagleeyeair import wallet
import jsonschema
from google.cloud import pubsub_v1

import eagleeyeair as ee

def main_accounts(request):
    """ Responds to an HTTP request using data from the request body parsed
    according to the "content-type" header.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    More detail information can be found in the LLD below:
    
    """   
    event_data, delivery_attempt = _parse_request(request)
    event_sub_types = ["register"]

    if event_data["eventType"] != "accounts":
        raise RuntimeError("Unexpected event type: " + event_data["eventType"])

    if event_data["eventSubType"] not in event_sub_types:
        raise RuntimeError("Unexpected event sub type: " + event_data["eventSubType"])

    # register account
    if event_data["eventSubType"] == 'register':
        wallet_payload = _prepare_wallet_payload(event_data)
        wallet = ee.wallet.create_wallet_and_wallet_identities(wallet_payload)

        ee.wallet.create_wallet_consumer(wallet["walletId"], 
                                        {
                                        "friendlyName": "DefaultConsumer",
                                        "type": "DEFAULT",
                                        }
                                        )

        ee.wallet.create_wallet_scheme_account(wallet["walletId"], 
                                            os.environ["ee_memberSchemeId"], 
                                            {"status": "ACTIVE", "state": "LOADED"}
                                            )   
                      
    return '200'

def _prepare_wallet_payload(event_data):
    return {
            "type": "MEMBER",
            "status": "ACTIVE",
            "state": "EARNBURN",
            "identities": [
                {
                "type": "LCN",
                "friendlyName": "Loyalty Card Number",
                "value": event_data["eventDetails"]["profile"]["account"]["cardNumber"],
                "state": "REGISTERED",
                "status": "ACTIVE"
                },
                {
                "type": "CRN",
                "friendlyName": "Customer Reference Number",
                "value": event_data["eventDetails"]["profile"]["crn"],
                "state": "REGISTERED",
                "status": "ACTIVE"
                },
                {
                "type": "HASH_CRN",
                "friendlyName": "Hashed Customer Reference Number",
                "value": event_data["eventDetails"]["profile"]["crnHash"],
                "state": "REGISTERED",
                "status": "ACTIVE"
                }]
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
    validate_payload_format(event_data)

    logging.info('Completed preparing data for EE request.')
    return event_data, delivery_attempt


def validate_payload_format(event_data):
    "this function validate the message payload format againt the schema"
    with open('account-register-schema.json', 'r') as file:
        schema = json.load(file)
    
    jsonschema.validate(instance=event_data, schema=schema)

