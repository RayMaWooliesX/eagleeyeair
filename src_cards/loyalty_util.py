import os
import logging
from datetime import datetime
import base64

import jsonschema
import json
import requests

import eagleeyeair as ee

MONGO_API_LOGGING_URL = os.environ["MONGO_API_LOGGING_URL"]
SYS_NAME = "RTL"
MONGO_API_LOGGING_CLIENT_ID = os.environ["MONGO_API_LOGGING_CLIENT_ID"]
MONGO_API_LOGGING_HEADERS = {
    "Content-Type": "application/json",
    "client_id": MONGO_API_LOGGING_CLIENT_ID,
}


def mongodb_logging(operation, changesUpdated, responseCode, message, correlationId):
    """exception in logging in mongodb will not failed the function"""
    try:
        data = {
            "name": SYS_NAME,
            "operation": operation,
            "changesUpdated": changesUpdated,
            "responseCode": responseCode,
            "message": message,
            "updatedAt": datetime.now().strftime("%Y-%m-%d/, %H:%M:%S:%f"),
            "correlationId": correlationId,
        }
        r = requests.put(
            MONGO_API_LOGGING_URL, json.dumps(data), headers=MONGO_API_LOGGING_HEADERS
        )
        if r.status_code >= 400:
            logging.error("Mongo logging completed with  " + r.text)
        else:
            logging.info("Mongo logging completed with  " + r.text)

        r.raise_for_status
        return r.status_code
    except Exception as e:
        logging.error(e)
        pass


def validate_payload(event_data, expected_event_type, expected_event_sub_types=None):
    """this function:
    ---validates the message payload format againt the schema
    ---checks the value of the event type
    ---optionally checks the value of event sub type"""
    with open("message-schema.json", "r") as file:
        schema = json.load(file)

    jsonschema.validate(instance=event_data, schema=schema)

    ##validate the event type and event sub type value
    event_sub_types = expected_event_sub_types
    if event_data["eventType"] != expected_event_type:
        raise ValueError("Unexpected event type: " + event_data["eventType"])
    if expected_event_sub_types:
        if event_data["eventSubType"] not in event_sub_types:
            raise ValueError("Unexpected event sub type: " + event_data["eventSubType"])

    logging.info(
        "Validated the payload format, event type and event sub types(optional)"
    )


def parse_request(request):
    """This function parses the request and return the request data in jason format"""
    envelope = request.get_json()
    message = envelope["message"]
    delivery_attempt = envelope["deliveryAttempt"]
    event_data_str = base64.b64decode(message["data"])
    event_data = json.loads(event_data_str)

    logging.info("Parsed event data for EE request.")
    return event_data, delivery_attempt


def create_house_hold_wallet(lcn: str) -> dict:
    """
    Create house hold wallet for given LCN
    """
    payload = {
        "status": "ACTIVE",
        "state": "EARNBURN",
        "type": "HOUSEHOLD",
        "friendlyName": f"HOUSEHOLD WALLET of holder {lcn}",
        "meta": {"Primary LCN": lcn},
    }
    wallet = ee.wallet.create_wallet(payload)
    return wallet
