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

def main(request):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
        event (dict):  The dictionary with data specific to this type of
        event. The `data` field contains the PubsubMessage message. The
        `attributes` field will contain custom attributes if there are any.
        context (google.cloud.functions.Context): The Cloud Functions event
        metadata. The `event_id` field contains the Pub/Sub message ID. The
        `timestamp` field contains the publish time.
    """
    # response_code = '200'
    error_client = error_reporting.Client()
    
    try:
        print("Preparing data for EE request.")
        url = os.environ['ee_api_url']
        authClientId = os.environ['ee_api_user']
        password = os.environ['ee_api_password']

        envelope = request.get_json()
        message = envelope['message']
        delivery_attempt = envelope['deliveryAttempt']
        event_data_str = base64.b64decode(message["data"])
        event_data = json.loads(event_data_str)
        crn = event_data['crn']

        event_type = event_data["eventType"]
        if event_type != 'Change Preference':
            raise Exception("Incorrect event type!")
        event_sub_type = event_data["eventSubType"]

        if event_sub_type == "No liquor Offers":
            preference_label = "noLiquorOffers"
        elif event_sub_type == "Redemption Setting":
            preference_label = "redemptionSetting"
        else:
            raise Exception("Incorrect sub event type!")
        
        preferences = event_data['preferences']
        preference_value = preferences['value']

        print("Data preparation completed.")

        print("Calling EE APIs to update consumer preference.")
        wallet_id = _get_wallet_id_by_crn(url, authClientId, password, crn, event_data['correlationId'])
        consumer_id = _get_consumer_id_by_wallet(url, authClientId, password, wallet_id, event_data['correlationId'])
        update_response = _update_consumer_objects_by_wallet_and_consumer_id(url, authClientId, password, wallet_id, consumer_id, preference_label, preference_value,  event_data['correlationId'])
        print('Updating completed.')
        response_code = '200'

        try:
            _logging_in_mongodb(event_data['correlationId'], '200', 'OK', delivery_attempt)
        except Exception as e:
            logging.error(RuntimeError("!!! There was an error while logging in mongodb."))
            print(traceback.format_exc())
            error_client.report_exception()
            pass

    except requests.exceptions.RequestException as e:
        if e.response.status_code == 429:
            response_code = '500'
            logging.error(RuntimeError("Too many requests error"))
            print(traceback.format_exc())
            error_client.report_exception()
            if message.delivery_attempt == 5:
                _logging_in_mongodb( event_data['correlationId'], str(e.response.status_code), e.response.reason + ": " + e.response.text , delivery_attempt)
            print("Too many requests error logging completed.")
        else:
            response_code = '102'
            logging.error(RuntimeError("Http error: "))
            print(traceback.format_exc())
            error_client.report_exception()
            _logging_in_deadletter(event_data_str.decode('utf-8'), e.response.reason)
            _logging_in_mongodb( event_data['correlationId'], str(e.response.status_code), e.response.reason + ": " + e.response.text , delivery_attempt)
            print("Http error logging completed.")

    except Exception as e:
        response_code = '204'
        logging.error(RuntimeError('Data error:'))
        error_msg = ','.join(e.args) + "," + e.__doc__
        logging.error(RuntimeError(error_msg))
        print(traceback.format_exc())
        error_client.report_exception()
        _logging_in_deadletter(event_data_str.decode('utf-8'), error_msg)
        if event_data['correlationId']:
            _logging_in_mongodb( event_data['correlationId'], '400', error_msg, delivery_attempt)
    finally:
        return response_code

def _get_wallet_id_by_crn(url, authClientId, password, crn, correlationId):
    '''
    This function will be called to get the Wallet ID based on CRN
    :param crn:
    :return: Wallet ID  will be returned based on the CRN
    '''
    service_path = os.environ['ee_get_wallet_service_path'].replace('{{identityValueCRN}}', crn)
    payload = ''
    headers = _get_header(url, service_path, payload, authClientId, password)
    end_point = url + service_path
    return _calling_the_request_consumer_object_function("GET", end_point, headers, payload, correlationId)['walletId']

def _get_consumer_id_by_wallet(url, authClientId, password, wallet_id, correlationId):
    # This function will be called to get Consumer ID based on Wallet ID
    service_path = os.environ['ee_get_consumer_service_path'].replace('{{walletId}}', wallet_id)
    payload = ''
    end_point = url + service_path
    headers = _get_header(url, service_path, payload, authClientId, password)
    return _calling_the_request_consumer_object_function("GET", end_point, headers, payload, correlationId)['consumerId']

def _update_consumer_objects_by_wallet_and_consumer_id(url, authClientId, password, wallet_id, consumer_id, preference_label, preference_value, correlationId):
    # This function will be called to update the Consumer objects based on Wallet and Consumer ID
    service_path = update_consumer_service_path = os.environ['ee_update_consumer_service_path'].replace('{{walletId}}', wallet_id).replace('{{consumerId}}', consumer_id)

    payload = json.dumps({"friendlyName": "Consumer Details",
                          "data": {"dimension": [
                                                 {"label": preference_label,
                                                  "value": preference_value}
                                                ]
                                   }
                          })
    end_point = url + service_path
    headers = _get_header(url, service_path, payload, authClientId, password)

    return _calling_the_request_consumer_object_function("PATCH", end_point, headers=headers, payload=payload, correlationId=correlationId)

def _calling_the_request_consumer_object_function(mode, end_point, headers, payload, correlationId):
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

def _get_header(url, service_path, payload, authClientId, password):
    '''
    This function will prepare the header based on the parameters
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

def _logging_in_mongodb(correlationId, status_code, status_message, retried_count):
    print("---Logging in mongodb")
    try:
        url = os.environ['mongodb_url']
        dbname = os.environ['mongodb_dbname']
        collection = os.environ['mongodb_collection']

        print(url)
        print(dbname)
        print(collection)

        changes_updated = 'false' if status_code >= '300' else 'true'
        status_object = {"name": "EagleEye", "changesUpdated": changes_updated, "response": {"statusCode": status_code, "message": status_message}, "retriedCount": retried_count, "updatedAt": datetime.now().astimezone(pytz.timezone("Australia/Sydney")).strftime("%Y%m%d-%H%M%S")}
        client = MongoClient(url)
        db = client[dbname]
        print(db.list_collection_names())
        col = db[collection]
        print(col.full_name)
        results = col.update_one({'correlationId': correlationId}, {'$push': {'status': status_object}})

        print("---Logging in mongodb completed, " + str(results.modified_count) + " records logged.")
    except Exception as e:
        logging.error(RuntimeError("!!! There was an error while logging in mongodb."))
        print(traceback.format_exc())
        pass

def _logging_in_deadletter(event_data, error_message):
    try:
        print("---Logging original message to dead letter topic.")
        error_publisher_client = pubsub_v1.PublisherClient()
        error_topic_path = error_publisher_client.topic_path(os.environ['GCP_PROJECT'], 
                                                            os.environ['error_topic'])
        user = os.environ['FUNCTION_NAME']
        future = error_publisher_client.publish(error_topic_path, event_data.encode("utf-8") ,
                                                                        user=user,
                                                                        error = error_message)
        # Wait for the publish future to resolve before exiting.
        while not future.done():
            time.sleep(1)
        print("---Logging original message to dead letter topic completed.")
    except Exception as e:
        logging.error(RuntimeError("!!! There was an error while sending error message to dead letter topic. " ))
        print(traceback.format_exc())
        pass