import os
import logging

import google.cloud.logging

import eagleeyeair as ee
from loyalty_util import mongodb_logging, parse_request, validate_payload

# Instantiates a client
client = google.cloud.logging.Client()
client.setup_logging()

EXPECTED_EVENT_TYPE = "accounts"
EXPECTED_EVENT_SUB_TYPES = ["register", "close"]


def main_accounts(request):
    """Responds to an HTTP request using data from the request body parsed
        according to the "content-type" header.
        Args:
            request (flask.Request): The request object.
            <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
        More detail information can be found in the LLD below:
    https://woolworthsdigital.atlassian.net/wiki/spaces/DGDMS/pages/25556287773/Detailed+Design+for+Loyalty+API+Integration+of+account+management
    """
    try:
        event_data, delivery_attempt = parse_request(request)
        validate_payload(event_data, EXPECTED_EVENT_TYPE, EXPECTED_EVENT_SUB_TYPES)

        # register account
        if event_data["eventSubType"] == "register":
            wallet_payload = _prepare_wallet_payload(event_data)
            wallet = ee.wallet.create_wallet_and_wallet_identities(wallet_payload)

            consumer = ee.wallet.create_wallet_consumer(
                wallet["walletId"],
                {
                    "friendlyName": "DefaultConsumer",
                    "type": "DEFAULT",
                },
            )

            ee.wallet.create_wallet_scheme_account(
                wallet["walletId"],
                os.environ["ee_memberSchemeId"],
                {"status": "ACTIVE", "state": "LOADED"},
            )

            ee.wallet.update_wallet_consumer(
                wallet["walletId"],
                consumer["consumerId"],
                {
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
                },
            )
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
                "status": "ACTIVE",
            },
            {
                "type": "CRN",
                "friendlyName": "Customer Reference Number",
                "value": event_data["eventDetails"]["profile"]["crn"],
                "state": "REGISTERED",
                "status": "ACTIVE",
            },
            {
                "type": "HASH_CRN",
                "friendlyName": "Hashed Customer Reference Number",
                "value": event_data["eventDetails"]["profile"]["crnHash"],
                "state": "REGISTERED",
                "status": "ACTIVE",
            },
        ],
    }
