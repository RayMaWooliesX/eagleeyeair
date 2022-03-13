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


def is_in_household(card_number: str) -> tuple:
    """
    returns:
           is in household flag
           wallet of the card
    """
    wallet = ee.wallet.get_wallet_by_identity_value(card_number)
    return (True, wallet) if len(wallet["relationships"]["child"]) else (False, wallet)


def is_household_primary_card(card_number: str) -> tuple:
    """
    return values: one of the flags: {NO_IN_HOUSEHOLD, PRIMARY, SECONDARY}
                   primary card wallet
                   house hold wallet
    """
    in_household, wallet = is_in_household(card_number)

    if not in_household:
        return ("NO_IN_HOUSEHOLD", wallet, {})
    h_wallet_id = wallet["relationships"]["child"][0]
    h_wallet = ee.wallet.get_wallet_by_wallet_id(h_wallet_id)

    return (
        ("PRIMARY", wallet, h_wallet)
        if h_wallet["meta"]["primary lcn"] == card_number
        else ("SECONDARY", wallet, h_wallet)
    )


def dismantle_household_wallet(h_wallet):
    for child_wallet_id in h_wallet["relationships"]["parent"]:
        ee.wallet.split_wallet_relation(child_wallet_id, h_wallet["walletId"])
    ee.wallet.delete_wallet(h_wallet["walletId"])


def link_cards(primary_card: str, secondary_card: str):
    in_household, s_wallet = is_in_household(secondary_card)
    if in_household:
        raise ValueError(f"card {secondary_card} is already member of a household")

    is_primary_card, p_wallet, h_wallet = is_household_primary_card(primary_card)
    if is_primary_card == "SECONDARY":
        raise ValueError(
            f"{primary_card} is not a primary card but a secondary card of a household"
        )
    elif is_primary_card == "NO_IN_HOUSEHOLD":
        h_wallet = create_house_hold_wallet(primary_card)
        ee.wallet.create_wallet_child_relation(
            p_wallet["walletId"], h_wallet["walletId"]
        )
        logging.info(
            "Primary card is not in any household wallet. New household wallet is created."
        )
    ee.wallet.create_wallet_child_relation(s_wallet["walletId"], h_wallet["walletId"])
    logging.info("Cards are linked successfully.")


def unlink_cards(primary_card: str, secondary_card: str):
    in_household, s_wallet = is_in_household(secondary_card)
    if not in_household:
        raise ValueError(
            f"card {secondary_card} does not belong to any household wallet."
        )

    is_primary_card, p_wallet, h_wallet = is_household_primary_card(primary_card)
    if is_primary_card == "SECONDARY":
        raise ValueError(
            f"{primary_card} is not a primary card but a secondary card of a household"
        )
    elif is_primary_card == "NO_IN_HOUSEHOLD":
        raise ValueError(
            f"card {secondary_card} does not belong to any household wallet."
        )

    if p_wallet["relationships"]["child"][0] != s_wallet["relationships"]["child"][0]:
        raise ValueError(
            f"card {primary_card} and {secondary_card} are not in the same household wallet."
        )
    h_wallet_id = h_wallet["walletId"]
    ee.wallet.split_wallet_relation(s_wallet["walletId"], h_wallet_id)
    if len(h_wallet["relationships"]["parent"]) == 2:
        ee.wallet.split_wallet_relation(p_wallet["walletId"], h_wallet_id)
        ee.wallet.delete_wallet(h_wallet_id)
        logging.info("Deleted household wallet, since it only has one child left.")
    logging.info("Completed unlinking card.")
