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
        wallet_id = eagleeyeair.wallet.get_wallet_by_identity_value(event_data["profile"]["crn"])["walletId"]
        ###temp code
        wallet_api = ee_api(wallet_host, prefix, client_id, secret)
        ###
        identities = wallet_api.get_wallet_identities_by_wallet_id_with_no_query(wallet_id)["results"]
        identity_id = ""
        for identity in identities:
            if identity["value"] == event_data["profile"]["cardNumber"]:
                identity_id = identity["identityId"]
        eagleeyeair.wallet.update_wallet_identity_status_suspended(wallet_id, identity_id)

        if event_data["eventSubType"] == "replace":
            data = _prepare_lcn_payload(event_data["profile"]["newCardNumber"])
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
        logging.error(RuntimeError('Data error:'))
        error_msg = ','.join(e.args) + "," + e.__doc__
        logging.error(RuntimeError(error_msg))
        logging.info(traceback.format_exc())
        error_client.report_exception()
        _logging_in_deadletter(json.dumps(event_data), error_msg)
    finally:
        return response_code

def _prepare_lcn_payload(lcn_num):
    return 
    {
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

def _prepare_preference_payload(event_sub_type, preferences):

    payload = {"friendlyName": "Consumer Details",
                          "data": {"dimension": []
                                   }
              }

    if event_sub_type == 'communications':
        for preference in preferences:
            if preference['id'] == 1042:
                payload['data']['dimension'].append({"label": 'noLiquorOffers',
                                                     "value":  True if preference['value'] == 'Y' else False }
                                                   )
    elif event_sub_type == 'redemption':
        payload['data']['dimension'].append({"label": 'redemptionSetting',
                                                "value": preferences[0]['value']}
                                            )

    if not payload['data']['dimension']:
        raise Exception('No expected preference found in the event data !') 

    return json.dumps(payload)

def _get_wallet_id_by_crn(url, authClientId, password, crn, correlationId):
    '''
    This function will be called to get the Wallet ID based on CRN
    :param crn:
    :return: Wallet ID  will be returned based on the CRN
    '''
    service_path = os.environ['ee_get_wallet_service_path'].replace('{{identityValueCRN}}', crn)
    payload = ''
    headers = _get_header(service_path, payload, authClientId, password, correlationId)
    end_point = url + service_path
    return _calling_the_request_consumer_object_function("GET", end_point, headers, payload)['walletId']

def _get_consumer_id_by_wallet(url, authClientId, password, wallet_id, correlationId):
    # This function will be called to get Consumer ID based on Wallet ID
    service_path = os.environ['ee_get_consumer_service_path'].replace('{{walletId}}', wallet_id)
    payload = ''
    end_point = url + service_path
    headers = _get_header(service_path, payload, authClientId, password, correlationId)
    return _calling_the_request_consumer_object_function("GET", end_point, headers, payload)['consumerId']

def _update_consumer_objects_by_wallet_and_consumer_id(url, authClientId, password, wallet_id, consumer_id, preference_payload, correlationId):
    # This function will be called to update the Consumer objects based on Wallet and Consumer ID
    service_path = update_consumer_service_path = os.environ['ee_update_consumer_service_path'].replace('{{walletId}}', wallet_id).replace('{{consumerId}}', consumer_id)
    end_point = url + service_path

    headers = _get_header(service_path, preference_payload, authClientId, password, correlationId)

    return _calling_the_request_consumer_object_function("PATCH", end_point, headers=headers, payload=preference_payload)

def _calling_the_request_consumer_object_function(mode, end_point, headers, payload):
    '''
    This function will make a call to Eagle Eye API
    :param mode: will determine if it is get, Post or Patch
    :param end_point: End point is the complete URL
    :param header:  Header is the request header
    :param payload: payload is the request payload
    :return: This function will return the response or return Null
    '''
    response = requests.request(mode, end_point, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def _get_header(service_path, payload, authClientId, password, correlationId):
    '''
    This function will prepare the header based on the parameters
    :param service_path:
    :param transaction_id:
    :param payload:
    :param authClientId:
    :param password:
    :return:
    '''
    prefix = '/2.0'
    transaction_id = correlationId + '-' + str(time.time())
    authHash = hashlib.sha256((prefix + service_path + payload + password).encode()).hexdigest()
    header = {"X-EES-AUTH-HASH": authHash, "X-EES-AUTH-CLIENT-ID": authClientId,
              "X-TRANSACTION-ID": transaction_id,
              "X-RETRY": "1", "X-EES-OPERATOR": "1", "X-EES-CALLER": "DASHBOARD",
              "X-EES-CALLER-VERSION": "0",
              "Content-Type": "application/json"}

    return header

def _logging_in_mongodb(correlationId, status_code, status_message, retried_count):
    logging.info("---Logging in mongodb")
    try:
        url = os.environ['mongodb_url']
        dbname = os.environ['mongodb_dbname']
        collection = os.environ['mongodb_collection']

        changes_updated = 'false' if status_code >= '300' else 'true'
        status_object = {"name": "EagleEye", "changesUpdated": changes_updated, "response": {"statusCode": status_code, "message": status_message}, "retriedCount": retried_count, "updatedAt": datetime.now().astimezone(pytz.timezone("Australia/Sydney")).strftime("%Y%m%d-%H%M%S")}

        client = MongoClient(url, connectTimeoutMS = 5000, serverSelectionTimeoutMS = 5000)
        db = client[dbname]
        col = db[collection]
        print(correlationId)
        results = col.update_one({'correlationId': correlationId}, {'$push': {'status': status_object}})

        logging.info("---Logging in mongodb completed, " + str(results.modified_count) + " records logged.")
    except Exception as e:
        logging.error(RuntimeError("!!! There was an error while logging in mongodb."))
        logging.info(traceback.format_exc())
        return '200'

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