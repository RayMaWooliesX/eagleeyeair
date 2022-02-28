"""
This Cloud function is responsible for:
- Parsing data triggered by source pubsub
- Preparing data for the EE API calls.
- Calling EE APIs to update preference
"""
import os
import logging

import google.cloud.logging

import eagleeyeair as ee
from loyalty_util import mongodb_logging, parse_request, validate_payload

# Instantiates a logging client
client = google.cloud.logging.Client()
client.setup_logging()

EXPECTED_EVENT_TYPE = "preferences"


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
    try:
        event_data, delivery_attempt = parse_request(request)
        validate_payload(event_data, EXPECTED_EVENT_TYPE)
        logging.info("Starting the card preference updating process.")
        logging.info("Integration Id: " + event_data["eventDetails"]["correlationId"])
        logging.info("delivery attemp: " + str(delivery_attempt))

        logging.info(os.environ["EES_WALLET_API_HOST"])

        wallet = ee.wallet.get_wallet_by_identity_value(
            event_data["eventDetails"]["profile"]["crn"]
        )
        consumer = ee.wallet.get_wallet_consumer(wallet["walletId"])
        preference_payload = _prepare_consumer_payload(event_data, consumer)

        ee.wallet.update_wallet_consumer(
            wallet["walletId"], consumer["consumerId"], preference_payload
        )
        logging.info("Completed the card preference updating process.")
        # logging in mongodb, function return 200 even if logging fails
        mongodb_logging(
            event_data["operation"],
            True,
            200,
            "Succeeded",
            event_data["eventDetails"]["correlationId"],
        )
        return "200"

    except ee.eagle_eye_api.EagleEyeApiError as e:
        logging.error(e)
        mongodb_logging(
            event_data["operation"],
            False,
            e.status_code,
            e.reason,
            event_data["eventDetails"]["correlationId"],
        )
        raise e
    except Exception as e:
        logging.info(e)
        mongodb_logging(
            event_data["operation"],
            False,
            400,
            str(e),
            event_data["eventDetails"]["correlationId"],
        )
        raise e


def _prepare_consumer_payload(event_data, consumer):
    """Get the existing memberOfferExclusions and memberPreferences
    information from EE and update them with the event data segment information"""

    empty_memberOfferExclusions = {
        "name": "memberOfferExclusions",
        "segments": [{"labels": ["Member Offer Exclusions"], "data": {}}],
    }
    empty_memberPreferences = {
        "name": "memberPreferences",
        "segments": [{"labels": ["Member Preferences"], "data": {}}],
    }
    memberOfferExclusions = {}
    memberPreferences = {}
    # get the current memberOfferExclusions and memberPreferences from consumer data
    if not consumer["data"]:
        pass
    else:
        if consumer["data"].get("segmentation"):
            for segmentation in consumer["data"]["segmentation"]:
                if segmentation["name"] == "memberOfferExclusions":
                    memberOfferExclusions = segmentation
                elif segmentation["name"] == "memberPreferences":
                    memberPreferences = segmentation
    # create empty segment payload if not exist in EE yet.
    # ["segments"][0]["data"] is a list when it is empty, convert it to dict
    if not memberOfferExclusions:
        memberOfferExclusions = empty_memberOfferExclusions
    else:
        if not memberOfferExclusions["segments"][0]["data"]:
            memberOfferExclusions["segments"][0]["data"] = {}
    if not memberPreferences:
        memberPreferences = empty_memberPreferences
    else:
        if not memberPreferences["segments"][0]["data"]:
            memberPreferences["segments"][0]["data"] = {}
    # update memberOfferExclusions and memberPreferences segment with event data
    memberOfferExclusions, memberPreferences = _update_segmentation(
        event_data, memberOfferExclusions, memberPreferences
    )

    payload = {
        "data": {"segmentation": [memberOfferExclusions, memberPreferences]},
    }

    return payload


def _update_segmentation(event_data, memberOfferExclusions, memberPreferences):
    """update the segment memberOfferExclusions, memberPreferences with the data from request"""
    # functions to update the dict
    memberOfferExclusions_update_func = memberOfferExclusions["segments"][0][
        "data"
    ].update
    memberOfferExclusions_pop_func = memberOfferExclusions["segments"][0]["data"].pop
    memberPreferences_update_func = memberPreferences["segments"][0]["data"].update
    memberPreferences_pop_func = memberPreferences["segments"][0]["data"].pop

    # this dictionary maps preference id and value to segment id, value in EE and the function used to update them
    OP_DICT = {
        "1042-True": [
            {memberOfferExclusions_update_func: {"0047": "No Liquor Offers"}}
        ],
        "1042-False": [{memberOfferExclusions_pop_func: "0047"}],
        # unsubscribe all
        "1024-True": [{memberOfferExclusions_pop_func: "0047"}],
        "1024-False": [{lambda *args: None: "0047"}],
        "30101-True": [
            {memberPreferences_update_func: {"0033": "eReceipt - Supermarkets & Metro"}}
        ],
        "30101-False": [{memberPreferences_pop_func: "0033"}],
        "30102-True": [{memberPreferences_update_func: {"0037": "eReceipt - Big W"}}],
        "30102-False": [{memberPreferences_pop_func: "0037"}],
        "30103-True": [{memberPreferences_update_func: {"0035": "eReceipt - BWS"}}],
        "30103-False": [{memberPreferences_pop_func: "0035"}],
        "39-Automatic": [
            {memberPreferences_pop_func: "0104"},
            {memberPreferences_pop_func: "0105"},
        ],
        "39-QantasPoints": [
            {memberPreferences_update_func: {"0104": "SFL QFF"}},
            {memberPreferences_pop_func: "0105"},
        ],
        "39-Christmas": [
            {memberPreferences_update_func: {"0105": "SFL Christmas"}},
            {memberPreferences_pop_func: "0104"},
        ],
    }

    for preference in event_data["eventDetails"]["profile"]["account"]["preferences"]:
        operations = OP_DICT.get(str(preference["id"]) + "-" + str(preference["value"]))
        if not operations:
            raise RuntimeError(
                "Incorrect preference id or value! id: "
                + str(preference["id"])
                + "; value: "
                + preference["value"]
            )
        for op in operations:
            func = list(op.keys())[0]
            param = list(op.values())[0]
            if func.__name__ == "pop":
                func(param, None)
            else:
                func(param)

    return memberOfferExclusions, memberPreferences
