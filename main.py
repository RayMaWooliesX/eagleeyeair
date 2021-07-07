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
from pymongo import MongoClient
from google.cloud import pubsub_v1
from google.cloud import error_reporting

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
    response_code = '200'
    error_client = error_reporting.Client()
    
    try:
        print("Preparing data for EE request.")
        url = os.environ['ee_api_url']
        authClientId = os.environ['ee_api_user']
        password = os.environ['ee_api_password']
        envelope = json.loads(request.data.decode('utf-8'))
        message = envelope['message']
        delivery_attempt = envelope['deliveryAttempt']
        event_data_str = base64.b64decode(message["data"])
        event_data = json.loads(event_data_str)
        crn = event_data['crn']
        correlationId = event_data['correlationId']
        preferences = event_data['preferences']
        redemptionSetting = preferences['value']
        print("Data preparation completed.")

        print("Calling EE APIs to update consumer preference.")
        wallet_id = _get_wallet_id_by_crn(url, authClientId, password, crn, correlationId)['walletId']
        consumer_id = _get_consumer_id_by_wallet(url, authClientId, password, wallet_id, correlationId)['consumerId']
        update_response = _update_consumer_objects_by_wallet_and_consumer_id(url, authClientId, password, wallet_id, consumer_id, redemptionSetting, correlationId)
        print('Updating completed.')
        response_code = '200'

        _logging_in_mongodb(correlationId, '200', 'OK', delivery_attempt)

    # return 500 and retry from the pubsub again for a timeout error and log into the mongodb in the last retry
    except requests.Timeout as e:
        response_code = '500'
        print("Timeout error")
        print("-- correlationId: " + correlationId + "; " + str(e.response.status_code) + ": " + e.response.reason + ", " + e.response.text)
        _logging_in_deadletter(event_data_str.decode('utf-8'), e.response.reason)
        if message.delivery_attempt == 5:
            _logging_in_mongodb( correlationId, e.response.status_code, e.response.reason, delivery_attempt)
        print("Timeout error logging completed.")

    # forward data errors to dead letter and log in mongodb without retry by acknowledgeing the message
    except requests.exceptions.RequestException as e:
        print("Request error: ")
        print(correlationId)
        print(e.response.status_code)
        print(e.response.reason)
        print(e.response.text)
        print("-- correlationId: " + correlationId + "; " + str(e.response.status_code) + ": " + e.response.reason + ", " + e.response.text)
        _logging_in_deadletter(event_data_str.decode('utf-8'), e.response.reason)
        error_client.report_exception()
        _logging_in_deadletter(event_data_str.decode('utf-8'), e.response.reason)
        _logging_in_mongodb( correlationId, e.response.status_code, e.response.reason, delivery_attempt)
        print("Http error logging completed.")

    except Exception as e:
        response_code = '200'
        print("Data error: ")
        print("--correlationId: " + correlationId + "; " + e.message)
        error_client.report_exception()
        _logging_in_deadletter(event_data_str, e.message)
        _logging_in_mongodb( correlationId, '500', e.message, delivery_attempt)

    finally:
        return response_code

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

    return _calling_the_request_consumer_object_function("PATCH", end_point, headers=headers, payload=payload, correlationId=correlationId)

def _calling_the_request_consumer_object_function(mode, end_point, headers, payload, correlationId):
    '''
    This function will make a call to Eagle Eye API's
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
        print(response.json())
        response.raise_for_status()
        return 'NULL'

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
        changes_updated = 'false' if status_code >= '300' else 'true'
        status_object = {"name": "EagleEye", "changesUpdated": changes_updated, "response": {"statusCode": status_code, "message": status_message}, "retriedCount": retried_count, "updatedAt": datetime.now().astimezone(pytz.timezone("Australia/Sydney")).strftime("%Y%m%d-%H%M%S")}
        client = MongoClient(url)
        db = client[dbname]
        col = db[collection]
        results = col.update_one({'correlationId': correlationId}, {'$push': {'status': status_object}})

        print("---Logging in mongodb completed, " + str(results.modified_count) + " records logged.")
    except Exception as e:
        print("!!! There was an error while logging in mongodb. " + "Error message.")
        print(traceback.format_exc())
        pass

def _logging_in_deadletter(event_data, error_message):
    try:
        print("---Sending error message to dead letter topic.")
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
        print("---Logging to dead letter topic completed.")
    except Exception as e:
        print("!!! There was an error while sending error message to dead letter topic. " + "Error message: " + e.message)
        pass