"""
This Cloud function is responsible for:
- Parsing data triggered by source pubsub
- Preparing data for the EE API calls.
- Calling EE APIs to update preference
"""


import base64
import logging
import json
import jsonschema

import eagleeyeair as ee


def main_cards(request):
    """Responds to an HTTP request using data from the request body parsed
    according to the "content-type" header.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    More detail information can be found in the LLD below:
    https://woolworthsdigital.atlassian.net/wiki/spaces/DGDMS/pages/25482592639/Detailed+Design+for+Loyalty+API+integration+of+card+management#Deregister-Card-Event
    """

    event_data, delivery_attempt = _parse_request(request)

    ##validate the event type and event sub type value
    event_sub_types = {"cancel", "replace", "reregister", "deregister"}
    if event_data["eventType"] != "cards":
        raise RuntimeError("Unexpected event type: " + event_data["eventType"])
    if event_data["eventSubType"] not in event_sub_types:
        raise RuntimeError("Unexpected event sub type: " + event_data["eventSubType"])

    wallet = ee.wallet.get_wallet_by_identity_value(
        event_data["eventDetails"]["profile"]["crnHash"]
    )
    wallet_id = wallet["walletId"]
    identities = ee.wallet.get_wallet_identities_by_wallet_id(wallet_id)["results"]

    lcn = {}
    crn = {}
    hash_crn = {}
    replacing_lcn = {}
    identity_values = []

    for identity in identities:
        identity_values.append(identity["value"])
        if (
            identity["value"]
            == event_data["eventDetails"]["profile"]["account"]["cardNumber"]
        ):
            lcn = identity
        if identity["type"] == "CRN":
            crn = identity
        if identity["type"] == "HASH_CRN":
            hash_crn = identity
        if event_data["eventSubType"] == "replace":
            if (
                identity["value"]
                == event_data["eventDetails"]["profile"]["account"]["cards"][
                    "newCardNumber"
                ]
            ):
                replacing_lcn = identity
            if (
                identity["value"]
                == event_data["eventDetails"]["profile"]["account"]["cards"][
                    "oldCardNumber"
                ]
            ):
                lcn = identity

    if event_data["eventSubType"] == "replace":
        if replacing_lcn == {}:
            data = _prepare_active_lcn_payload(
                event_data["eventDetails"]["profile"]["account"]["cards"][
                    "newCardNumber"
                ]
            )
            # create the new card
            ee.wallet.create_wallet_identity(wallet_id, data)
        # cancel the existing card
        _cancel_card(
            wallet_id,
            lcn,
            event_data["eventDetails"]["profile"]["account"]["cards"][
                "replacementReason"
            ].upper(),
        )

    if event_data["eventSubType"] == "cancel":
        # cancel the card
        _cancel_card(
            wallet_id,
            lcn,
            event_data["eventDetails"]["profile"]["account"]["cards"][
                "cancellationReasonDescription"
            ].upper(),
        )
        _remove_edr_registered_card_segment(wallet_id)

    if event_data["eventSubType"] == "reregister":
        _re_register_card(wallet, event_data, lcn)
        _add_edr_registered_card_segment(wallet_id)

    if event_data["eventSubType"] == "deregister":
        _deregister_card(wallet, crn, hash_crn, lcn)

    return "200"


def _parse_request(request):
    """parse the request and return the request data in jason format"""
    envelope = request.get_json()
    message = envelope["message"]
    delivery_attempt = envelope["deliveryAttempt"]
    event_data_str = base64.b64decode(message["data"])
    event_data = json.loads(event_data_str)

    ##validate the payload against the scheme definition
    _validate_payload_format(event_data)

    logging.info("Completed preparing data for EE request.")
    return event_data, delivery_attempt


def _validate_payload_format(event_data):
    "this function validate the message payload format againt the schema"
    with open("message-schema.json", "r") as file:
        schema = json.load(file)

    jsonschema.validate(instance=event_data, schema=schema)


def _re_register_card(wallet, event_data, lcn):
    # update the wallet state, status value and create card if not exist
    if wallet["state"] != "EARNBURN":
        ee.wallet.update_wallet_state(
            wallet_id=wallet["walletId"], data={"state": "EARNBURN"}
        )
    if wallet["status"] != "ACTIVE":
        ee.wallet.activate_wallet(wallet_id=wallet["walletId"])

    data = _prepare_active_lcn_payload(
        event_data["eventDetails"]["profile"]["account"]["cardNumber"]
    )
    if not lcn:
        ee.wallet.create_wallet_identity(wallet["walletId"], data)


def _prepare_active_lcn_payload(lcn_num):
    return {
        "type": "LCN",
        "friendlyName": "Loyalty Card Number",
        "value": lcn_num,
        "state": "REGISTERED",
        "status": "ACTIVE",
    }


def _deregister_card(wallet, crn, hash_crn, lcn):
    if hash_crn["state"] != "CLOSED":
        ee.wallet.update_wallet_identity_state(
            wallet["walletId"], hash_crn["identityId"], {"state": "CLOSED"}
        )
    if hash_crn["status"] != "TERMINATED":
        ee.wallet.update_wallet_identity_status_terminated(
            wallet["walletId"], hash_crn["identityId"]
        )
    if lcn:
        ee.wallet.delete_wallet_identity(wallet["walletId"], lcn["identityId"])
    if crn:
        ee.wallet.delete_wallet_identity(wallet["walletId"], crn["identityId"])

    _remove_all_dimension_segment_values(wallet["walletId"])

    if wallet["state"] != "CLOSED":
        ee.wallet.update_wallet_state(wallet["walletId"], {"state": "CLOSED"})
    if wallet["status"] != "TERMINATED":
        ee.wallet.terminate_wallet(wallet["walletId"])


def _cancel_card(wallet_id, lcn, cancel_reason):
    if cancel_reason == "LOST" and lcn["status"] != "LOST":
        ee.wallet.update_wallet_identity_status_lost(
            wallet_id=wallet_id, identity_id=lcn["identityId"]
        )
    elif cancel_reason == "STOLEN" and lcn["status"] != "STOLEN":
        ee.wallet.update_wallet_identity_status_stolen(
            wallet_id=wallet_id, identity_id=lcn["identityId"]
        )
    else:
        if lcn["status"] != "SUSPENDED":
            ee.wallet.update_wallet_identity_status_suspended(
                wallet_id=wallet_id, identity_id=lcn["identityId"]
            )


def _remove_edr_registered_card_segment(wallet_id):
    consumer = ee.wallet.get_wallet_consumer(wallet_id)
    memberOfferTarget = _get_memberOfferTarget_segment(consumer)

    if memberOfferTarget != {}:
        memberOfferTarget["segments"][0]["data"].pop("0101")

        ee.wallet.update_wallet_consumer(
            wallet_id,
            consumer["consumerId"],
            {
                "friendlyName": "Sample Consumer",
                "data": {"segmentation": [memberOfferTarget]},
            },
        )


def _add_edr_registered_card_segment(wallet_id):
    consumer = ee.wallet.get_wallet_consumer(wallet_id)
    memberOfferTarget = _get_memberOfferTarget_segment(consumer)

    if memberOfferTarget == {}:
        memberOfferTarget = {
            "friendlyName": "Sample Consumer",
            "data": {
                "segmentation": [
                    {
                        "name": "memberOfferTarget",
                        "segments": [
                            {
                                "labels": ["Member Offer Target"],
                                "data": {"0101": "EDR Registered card"},
                            }
                        ],
                    }
                ]
            },
        }
    else:
        memberOfferTarget["segments"][0]["data"].update({"0101": "EDR Registered card"})
    ee.wallet.update_wallet_consumer(
        wallet_id,
        consumer["consumerId"],
        {
            "friendlyName": "Sample Consumer",
            "data": {"segmentation": [memberOfferTarget]},
        },
    )


def _get_memberOfferTarget_segment(consumer):

    memberOfferTarget = {}

    if not consumer["data"]:
        pass
    else:
        if consumer["data"].get("segmentation"):
            for segmentation in consumer["data"]["segmentation"]:
                if segmentation["name"] == "memberOfferTarget":
                    memberOfferTarget = segmentation

    return memberOfferTarget


def _remove_all_dimension_segment_values(wallet_id):
    consumer = ee.wallet.get_wallet_consumer(wallet_id)

    seg_without_value = []
    dim_without_value = []
    if not consumer.get("data"):
        pass
    else:
        if consumer["data"].get("segmentation"):
            for segmentation in consumer["data"].get("segmentation"):
                segmentation["segments"][0].update({"data": {}})
                seg_without_value.append(segmentation)
        if consumer["data"].get("dimension"):
            for dim in consumer["data"].get("dimension"):
                dim.update({"value": None})
                dim_without_value.append(dim)
    consumer_data = {}
    if dim_without_value:
        consumer_data.update({"dimension": dim_without_value})
    if seg_without_value:
        consumer_data.update({"segmentation": seg_without_value})

    if consumer_data:
        ee.wallet.update_wallet_consumer(
            wallet_id,
            consumer["consumerId"],
            {
                "friendlyName": "Sample Consumer",
                "data": consumer_data,
            },
        )
