"""
This Cloud function is responsible for:
- Parsing data triggered by source pubsub
- Preparing data for the EE API calls.
- Calling EE APIs to update preference
"""
import logging

import google.cloud.logging

import eagleeyeair as ee
from loyalty_util import mongodb_logging, parse_request, validate_payload

# Instantiates a client
client = google.cloud.logging.Client()
client.setup_logging()

EXPECTED_EVENT_TYPE = "cards"
EXPECTED_EVENT_SUB_TYPES = {"cancel", "replace", "reregister", "deregister"}


def main_cards(request):
    """Responds to an HTTP request using data from the request body parsed
    according to the "content-type" header.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    More detail information can be found in the LLD below:
    https://woolworthsdigital.atlassian.net/wiki/spaces/DGDMS/pages/25482592639/Detailed+Design+for+Loyalty+API+integration+of+card+management#Deregister-Card-Event
    """
    try:
        event_data, delivery_attempt = parse_request(request)
        validate_payload(event_data, EXPECTED_EVENT_TYPE, EXPECTED_EVENT_SUB_TYPES)
        logging.info("Starting the " + event_data["eventSubType"] + " card process.")
        if event_data["eventSubType"] == "replace":
            wallet = ee.wallet.get_wallet_by_identity_value(
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "oldCardNumber"
                ]
            )
            new_card_payload = _prepare_active_lcn_payload(
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "newCardNumber"
                ]
            )
            # create the new card
            ee.wallet.create_wallet_identity(wallet["walletId"], new_card_payload)
            # cancel the existing card
            _cancel_card(
                wallet["walletId"],
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "oldCardNumber"
                ],
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "replacementReason"
                ].upper(),
            )

        if event_data["eventSubType"] == "cancel":
            wallet = ee.wallet.get_wallet_by_identity_value(
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "cancelledCardNumber"
                ]
            )
            # cancel the card
            _cancel_card(
                wallet["walletId"],
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "cancelledCardNumber"
                ],
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "cancellationReasonDescription"
                ].upper(),
            )
            _remove_edr_registered_card_segment(wallet["walletId"])

        if event_data["eventSubType"] == "reregister":
            wallet = ee.wallet.get_wallet_by_identity_value(
                event_data["eventDetails"]["profile"]["crnHash"]
            )
            _re_register_card(
                wallet,
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "newCardNumber"
                ],
            )
            _add_edr_registered_card_segment(wallet["walletId"])

        if event_data["eventSubType"] == "deregister":
            wallet = ee.wallet.get_wallet_by_identity_value(
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "deregisteredCardNumber"
                ]
            )

            _deregister_card(
                wallet["walletId"],
                event_data["eventDetails"]["profile"]["crn"],
                event_data["eventDetails"]["profile"]["crnHash"],
                event_data["eventDetails"]["profile"]["account"]["cardEventDetail"][
                    "deregisteredCardNumber"
                ],
            )
        logging.info("Completed the " + event_data["eventSubType"] + " card process.")
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
        logging.error(e)
        mongodb_logging(
            event_data["operation"],
            False,
            "NA",
            str(e),
            event_data["eventDetails"]["correlationId"],
        )
        raise e


def _cancel_card(wallet_id, lcn, cancel_reason):
    identities = ee.wallet.get_wallet_identities_by_wallet_id(wallet_id)["results"]
    lcn_identity_id = _get_wallet_identity_id(identities, lcn, "LCN")
    if cancel_reason == "LOST":
        ee.wallet.update_wallet_identity_status_lost(wallet_id, lcn_identity_id)
    elif cancel_reason == "STOLEN":
        ee.wallet.update_wallet_identity_status_stolen(wallet_id, lcn_identity_id)
    else:
        ee.wallet.update_wallet_identity_status_suspended(wallet_id, lcn_identity_id)


def _re_register_card(wallet, lcn):
    # update the wallet state, status value and create card
    if wallet["state"] != "EARNBURN":
        ee.wallet.update_wallet_state(
            wallet_id=wallet["walletId"], data={"state": "EARNBURN"}
        )
    if wallet["status"] != "ACTIVE":
        ee.wallet.activate_wallet(wallet["walletId"])

    data = _prepare_active_lcn_payload(lcn)
    ee.wallet.create_wallet_identity(wallet["walletId"], data)


def _deregister_card(wallet_id, crn, hash_crn, lcn):
    identities = ee.wallet.get_wallet_identities_by_wallet_id(wallet_id)["results"]
    crn_identity_id = _get_wallet_identity_id(identities, crn, "CRN")
    hash_crn_identity_id = _get_wallet_identity_id(identities, hash_crn, "HASH_CRN")
    lcn_identity_id = _get_wallet_identity_id(identities, lcn, "LCN")

    ee.wallet.update_wallet_identity_state(
        wallet_id, hash_crn_identity_id, {"state": "CLOSED"}
    )
    ee.wallet.update_wallet_identity_status_terminated(wallet_id, hash_crn_identity_id)
    ee.wallet.delete_wallet_identity(wallet_id, crn_identity_id)
    ee.wallet.delete_wallet_identity(wallet_id, lcn_identity_id)

    _remove_all_dimension_segment_values(wallet_id)

    ee.wallet.update_wallet_state(wallet_id, {"state": "CLOSED"})
    ee.wallet.terminate_wallet(wallet_id)


def _prepare_active_lcn_payload(lcn):
    return {
        "type": "LCN",
        "friendlyName": "Loyalty Card Number",
        "value": lcn,
        "state": "REGISTERED",
        "status": "ACTIVE",
    }


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

    if not memberOfferTarget:
        memberOfferTarget = {
            "name": "memberOfferTarget",
            "segments": [
                {
                    "labels": ["Member Offer Target"],
                    "data": {"0101": "EDR Registered card"},
                }
            ],
        }

    else:
        if not memberOfferTarget["segments"][0]["data"]:
            memberOfferTarget["segments"][0]["data"] = {}
        memberOfferTarget["segments"][0]["data"].update({"0101": "EDR Registered card"})
    ee.wallet.update_wallet_consumer(
        wallet_id,
        consumer["consumerId"],
        {
            "data": {"segmentation": [memberOfferTarget]},
        },
    )


def _get_memberOfferTarget_segment(consumer):
    """get the memberOfferTarget segment from EE, return {} if not exist"""
    memberOfferTarget = {}

    if not consumer["data"]:
        pass
    else:
        if consumer["data"].get("segmentation"):
            for segmentation in consumer["data"]["segmentation"]:
                if segmentation["name"] == "memberOfferTarget":
                    memberOfferTarget = segmentation
    if not memberOfferTarget:
        memberOfferTarget = {}
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
                segmentation.update({"segments": []})
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
    print(seg_without_value)
    if consumer_data:
        ee.wallet.update_wallet_consumer(
            wallet_id,
            consumer["consumerId"],
            {
                "data": consumer_data,
            },
        )


def _get_wallet_identity_id(identities, identity_value, identity_type):

    for identity in identities:
        if identity["value"] == identity_value and identity["type"] == identity_type:
            identity_id = identity["identityId"]
    if not identity_id:
        raise RuntimeError(
            identity_type + "N: " + identity_value + " can not be found in the wallet!"
        )

    return identity_id
