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
import pymongo
from pymongo import MongoClient
from google.cloud import pubsub_v1
from google.cloud import error_reporting
from flask import request

import eagleeyeair

client_id = os.environ.get("EES_AUTH_CLIENT_ID", "")
secret = os.environ.get("EES_AUTH_CLIENT_SECRET", "")
prefix = os.environ.get("EES_API_PREFIX", "")
pos_host = os.environ.get("EES_POS_API_HOST", "")
resources_host = os.environ.get("EES_RESOURCES_API_HOST", "")
wallet_host = os.environ.get("EES_WALLET_API_HOST", "")

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
    error_client = error_reporting.Client()

    try:
        event_data, delivery_attempt = _parse_request(request)

        wallet_id = eagleeyeair.wallet.get_wallet_by_identity_value(event_data["eventDetails"]["profile"]["crn"])["walletId"]
        ###temp code
        wallet_api = ee_api(wallet_host, prefix, client_id, secret)
        ###
        identities = wallet_api.get_wallet_identities_by_wallet_id_with_no_query(wallet_id)["results"]
        identity_id = ""

        for identity in identities:
            if identity["value"] == event_data["eventDetails"]["profile"]["account"]["cardNumber"]:
                identity_id = identity["identityId"]
        eagleeyeair.wallet.update_wallet_identity_status_suspended(wallet_id= wallet_id, identity_id= identity_id)

        if event_data["eventSubType"] == "replace":
            data = _prepare_lcn_payload(event_data["eventDetails"]["profile"]["account"]["newCardNumber"])
            eagleeyeair.wallet.create_wallet_identity(wallet_id,data)
        response_code = '200'
        return '200'

    except requests.exceptions.RequestException as e:
        if e.response.status_code == 429:
            response_code = '500'
            logging.error(RuntimeError("Too many requests error"))
            logging.info(traceback.format_exc())
            error_client.report_exception()
            logging.info("Too many requests error logging completed.")
        else:
            response_code = '102'
            logging.error(RuntimeError("Http error: "))
            logging.info(traceback.format_exc())
            error_client.report_exception()
            logging.error(RuntimeError)
            _logging_in_deadletter(json.dumps(event_data), e.response.reason)
            logging.info("Http error logging completed.")
    except Exception as e:
        response_code = '204'
        logging.error(traceback.format_exc())
        logging.error(RuntimeError('Data error:'))
        error_msg = ','.join(e.args) + "," + e.__doc__
        logging.error(RuntimeError(error_msg))
        error_client.report_exception()
        _logging_in_deadletter(json.dumps(event_data), error_msg)
    finally:
        return response_code

def _prepare_lcn_payload(lcn_num):
    return {
            "type": "LCN",
            "friendlyName": "Loyalty Card Number",
            "value": lcn_num
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

def _logging_in_deadletter(event_data, error_message):

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


class ee_api(eagleeyeair.EagleEyeWallet):
    def get_wallet_identities_by_wallet_id_with_no_query(self,
        wallet_id,
        type=[]
    ):
        return self.get(
            f"/wallet/{wallet_id}/identities"
        )