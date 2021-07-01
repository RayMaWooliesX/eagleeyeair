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
import requests
from pymongo import MongoClient
import pymongo
from google.cloud import pubsub_v1

def main(message):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
        event (dict):  The dictionary with data specific to this type of
        event. The `data` field contains the PubsubMessage message. The
        `attributes` field will contain custom attributes if there are any.
        context (google.cloud.functions.Context): The Cloud Functions event
        metadata. The `event_id` field contains the Pub/Sub message ID. The
        `timestamp` field contains the publish time.
    """

    print(message)
    print('Processing message id: {}'.format(message.messageId))
    print('attributs:' + message.attributes)

    url = os.environ['ee_api_url']
    authClientId = os.environ['ee_api_user']
    password = os.environ['ee_api_password']

    event_data = json.loads(base64.b64decode(message.data))

    eventType = event_data['eventType']
    if eventType != 'Change redemptionSetting':
        return

    crn = event_data['crn']
    correlationId = event_data['correlationId']
    preferences = event_data['preferences']
    redemptionSetting = preferences['value']


    wallet_id = _get_wallet_id_by_crn(url, authClientId, password, crn, correlationId)['walletId']
    consumer_id = _get_consumer_id_by_wallet(url, authClientId, password, wallet_id, correlationId)['consumerId']

    ##  3. update consumer with new redemption setting
    update_response = _update_consumer_objects_by_wallet_and_consumer_id(url, authClientId, password, wallet_id, consumer_id, redemptionSetting, correlationId)
    print('updating completed')

def _calling_the_request_consumer_object_function(mode, end_point, header, payload, correlationId):
    '''
    This fucntion will make a call to Eagle Eye API's
    :param mode: will determine if it is get, Post or Patch
    :param end_point: End point is the complete URL
    :param header:  Header is the request header
    :param payload: payload is the request payload
    :return: This function will return the response or return Null
    '''

    response = requests.request(mode, end_point, headers=header, data=payload)

    if response.status_code not in [200, 201]: 
        print(response.json()) # Printing the error if status codes are not in 200 and 201.
        logging.error(response.json())
        response.raise_for_status()

    if mode == 'GET':
        if (response.status_code == 404):  # expected_response_code
            return '404'
        elif response.status_code == 200:
            return response.json()
    elif mode == 'PATCH':
        if (response.status_code == 200):  # expected_response_code
            return response.json()
        else:
            print('Error.... Response code is not 2XX')
            print(response.json())
            logging.error(response.json())
            response.raise_for_status()
            return 'NULL'

def _get_wallet_id_by_crn(url, authClientId, password, crn, correlationId):
    '''
    This function will be called to get the Wallet ID based on CRN
    :param crn:
    :return: Wallet ID  will be returned based on the CRN
    '''
    service_path = os.environ['ee_get_wallet_service_path'].replace('{{idenitityValueCRN}}', crn)
    payload = ''
    headers = _get_header(url, service_path, payload, authClientId, password)
    end_point = url + service_path
    return _calling_the_request_consumer_object_function("GET", end_point, headers, payload, correlationId)

def _get_consumer_id_by_wallet(url, authClientId, password, wallet_id, correlationId):
    # This function will be called to get Consumer ID based on Wallet ID
    service_path = os.environ['ee_get_consumer_service_path'].replace('{{walletId}}', wallet_id)
    payload = ''
    end_point = url + service_path
    headers = _get_header(url, service_path, payload, authClientId, password)
    return _calling_the_request_consumer_object_function("GET", end_point, headers, payload, correlationId)

def _update_consumer_objects_by_wallet_and_consumer_id(url, authClientId, password, wallet_id, consumer_id, redemptionSetting, correlationId):
    # This function will be called to update the Consumer objects based on Wallet and Consumer ID
    service_path = update_consumer_service_path = os.environ['ee_update_consumer_service_path'].replace('{{walletId}}', wallet_id).replace('{{consumerId}}', consumer_id)

    payload = json.dumps({"friendlyName": "Consumer Details",
                          "data": {"dimension": [
                                                 {"label": "redemptionSetting",
                                                  "value": redemptionSetting}
                                                ]
                                   }
                          })

    end_point = url + service_path
    headers = _get_header(url, service_path, payload, authClientId, password)

    response = requests.request("PATCH", end_point, headers=headers, data=payload)

    status_code = response.status_code
    error_message = response.reason
    _logging_in_mongodb( correlationId, status_code, error_message)

    response.raise_for_status()

    return response.json()

def _get_header(url, service_path, payload, authClientId, password):
    '''
    This funtion will prepare the header based on the parameters
    :param url:
    :param service_path:
    :param transaction_id:
    :param payload:
    :param authClientId:
    :param password:
    :return:
    '''
    prefix = '/2.0'
    transaction_id = 'cde_update_records_ ' + hashlib.md5(str(time.time()).encode()).hexdigest()
    authHash = hashlib.sha256((prefix + service_path + payload + password).encode()).hexdigest()
    header = {"X-EES-AUTH-HASH": authHash, "X-EES-AUTH-CLIENT-ID": authClientId,
              "X-TRANSACTION-ID": transaction_id,
              "X-RETRY": "1", "X-EES-OPERATOR": "1", "X-EES-CALLER": "DASHBOARD",
              "X-EES-CALLER-VERSION": "0",
              "Content-Type": "application/json"}
    return header

def _logging_in_mongodb(correlationId, status_code, status_message):
    url = os.environ['mongodb_url']
    dbname = os.environ['mongodb_dbname']
    collection = os.environ['mongodb_collection']
    changes_updated = 'false' if status_code >= 300 else 'ture'
    status_object = {"name": "EagleEye", "changesUpdated": changes_updated, "response": {"statusCode": status_code, "message": status_message}, "retriedCount": 0, "updatedAt": datetime.now().astimezone(pytz.timezone("Australia/Sydney")).strftime("%Y%m%d-%H%M%S")}

    client = MongoClient(url)
    db = client[dbname]
    col = db[collection]
    results = col.update_one({'correlationId': correlationId}, {'$push': {'status': status_object}})