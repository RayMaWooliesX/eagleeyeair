import unittest
from unittest import mock
import os
from requests.api import patch
from requests.models import Response
import main
import base64
import hashlib
import time
from pymongo import MongoClient
from pymongo.collection import Collection
from flask import Flask
import requests

@mock.patch("main._get_wallet_id_by_crn", return_value=123)
@mock.patch("main._get_consumer_id_by_wallet", return_value=123)
@mock.patch("main._update_consumer_objects_by_wallet_and_consumer_id")
@mock.patch("main._logging_in_mongodb")
# @mock.patch("main._logging_in_deadletter")
def test_main(mock_get_wallet, mock_get_consumerId, mock_update_consumer, mock_log_mongo):
    os.environ["ee_api_url"] = "ee_api_url"
    os.environ["ee_api_user"] = "ee_api_user"
    os.environ["ee_api_password"] = "ee_api_password"

    name = "test"
    data = '{"deliveryAttempt": 1, "message": {"data": "eyJzb3VyY2UiOnsiY29kZSI6MSwibmFtZSI6IkNQT1JUQUwifSwidHJhY2tpbmdJZCI6ImM2Mzk4MDExLWNlMDYtNGVlOC1iZGM3LWY1MzE5Zjc3MTJhNyIsImV2ZW50VHlwZSI6IkNoYW5nZSBQcmVmZXJlbmNlIiwgImV2ZW50U3ViVHlwZSI6Ik5vIGxpcXVvciBPZmZlcnMiLCJwdWJsaXNoZWRBdCI6IjIwMjEtMDUtMTkwMzo1ODoxNy4yNDciLCJjcm4iOiIzZmU4Y2RmMjRmNGJiMTNkNWQ1NmM5NGY2ZjUyMjkwYSIsImhhc2hlZENybiI6IjM1NWMzMTAwZDUzNmVhNGYyZThiYjFmNjQ3YjMwM2U3YWE2MjJmMDU2MGVmYzRiNzk4ODQ2MzQwNmYzYjM1OWIiLCJjYXJkTnVtYmVyIjoiOTM1NTA0OTM3OTMyOSIsImNvcnJlbGF0aW9uSWQiOiJjNjM5ODAxMS1jZTA2LTRlZTgtYmRjNy1mNTMxOWY3NzEyYTciLCJwcmVmZXJlbmNlcyI6eyJpZCI6IjEwNDIiLCJ2YWx1ZSI6ZmFsc2V9fQ==", "messageId": "2652670209994957", "message_id": "2652670209994957", "publishTime": "2021-07-11T10:26:03.697Z", "publish_time": "2021-07-11T10:26:03.697Z"}, "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub"}'
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)
    
    main.main(req)

    mock_get_wallet.assert_called_once()
    mock_get_consumerId.assert_called_once()
    mock_update_consumer.assert_called_once()
    mock_log_mongo.assert_called_once()
    
    assert main.main(req) == "200"



@mock.patch("main._logging_in_deadletter")
@mock.patch("google.cloud.error_reporting.Client.report_exception", return_value= "error reporting")
def test_main_data_error(mock_log_deadletter, mock_error_reporting):
    os.environ["ee_api_url"] = "ee_api_url"
    os.environ["ee_api_user"] = "ee_api_user"
    os.environ["ee_api_password"] = "ee_api_password"

    name = "test"
    data = '{"deliveryAttempt": 1, "message": {"dataa": "eyJzb3VyY2UiOnsiY29kZSI6MSwibmFtZSI6IkNQT1JUQUwifSwidHJhY2tpbmdJZCI6ImM2Mzk4MDExLWNlMDYtNGVlOC1iZGM3LWY1MzE5Zjc3MTJhNyIsImV2ZW50VHlwZSI6IkNoYW5nZSBQcmVmZXJlbmNlIiwgImV2ZW50U3ViVHlwZSI6Ik5vIGxpcXVvciBPZmZlcnMiLCJwdWJsaXNoZWRBdCI6IjIwMjEtMDUtMTkwMzo1ODoxNy4yNDciLCJjcm4iOiIzZmU4Y2RmMjRmNGJiMTNkNWQ1NmM5NGY2ZjUyMjkwYSIsImhhc2hlZENybiI6IjM1NWMzMTAwZDUzNmVhNGYyZThiYjFmNjQ3YjMwM2U3YWE2MjJmMDU2MGVmYzRiNzk4ODQ2MzQwNmYzYjM1OWIiLCJjYXJkTnVtYmVyIjoiOTM1NTA0OTM3OTMyOSIsImNvcnJlbGF0aW9uSWQiOiJjNjM5ODAxMS1jZTA2LTRlZTgtYmRjNy1mNTMxOWY3NzEyYTciLCJwcmVmZXJlbmNlcyI6eyJpZCI6IjEwNDIiLCJ2YWx1ZSI6ZmFsc2V9fQ", "messageId": "2652670209994957", "message_id": "2652670209994957", "publishTime": "2021-07-11T10:26:03.697Z", "publish_time": "2021-07-11T10:26:03.697Z"}, "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub"}'
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)
    
    main.main(req)   
    
    assert main.main(req) == "204"



@mock.patch("main._get_wallet_id_by_crn", autospec=True)
@mock.patch("main._logging_in_mongodb")
@mock.patch("main._logging_in_deadletter")
@mock.patch("builtins.print")
def test_main_429(mock_get_wallet, mock_log_mongo, mock_deadletter, mock_print):
    os.environ["ee_api_url"] = "ee_api_url"
    os.environ["ee_api_user"] = "ee_api_user"
    os.environ["ee_api_password"] = "ee_api_password"

    name = "test"
    data = '{"deliveryAttempt": 1, "message": {"data": "eyJzb3VyY2UiOnsiY29kZSI6MSwibmFtZSI6IkNQT1JUQUwifSwidHJhY2tpbmdJZCI6ImM2Mzk4MDExLWNlMDYtNGVlOC1iZGM3LWY1MzE5Zjc3MTJhNyIsImV2ZW50VHlwZSI6IkNoYW5nZSBQcmVmZXJlbmNlIiwgImV2ZW50U3ViVHlwZSI6Ik5vIGxpcXVvciBPZmZlcnMiLCJwdWJsaXNoZWRBdCI6IjIwMjEtMDUtMTkwMzo1ODoxNy4yNDciLCJjcm4iOiIzZmU4Y2RmMjRmNGJiMTNkNWQ1NmM5NGY2ZjUyMjkwYSIsImhhc2hlZENybiI6IjM1NWMzMTAwZDUzNmVhNGYyZThiYjFmNjQ3YjMwM2U3YWE2MjJmMDU2MGVmYzRiNzk4ODQ2MzQwNmYzYjM1OWIiLCJjYXJkTnVtYmVyIjoiOTM1NTA0OTM3OTMyOSIsImNvcnJlbGF0aW9uSWQiOiJjNjM5ODAxMS1jZTA2LTRlZTgtYmRjNy1mNTMxOWY3NzEyYTciLCJwcmVmZXJlbmNlcyI6eyJpZCI6IjEwNDIiLCJ2YWx1ZSI6ZmFsc2V9fQ==", "messageId": "2652670209994957", "message_id": "2652670209994957", "publishTime": "2021-07-11T10:26:03.697Z", "publish_time": "2021-07-11T10:26:03.697Z"}, "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub"}'
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)
    mock_response = mock.MagicMock()
    mock_response.status_code = 429
    mock_get_wallet.side_effect = requests.exceptions.HTTPError(response = mock_response)
    main.main(req)

    # mock_print.assert_called_with('Timeout error')
    assert main.main(req) == "500"


@mock.patch("main._get_wallet_id_by_crn", autospec=True)
@mock.patch("main._logging_in_mongodb")
@mock.patch("main._logging_in_deadletter")
@mock.patch("builtins.print")
def test_main_other_request_error(mock_get_wallet, mock_log_mongo, mock_deadletter, mock_print):
    os.environ["ee_api_url"] = "ee_api_url"
    os.environ["ee_api_user"] = "ee_api_user"
    os.environ["ee_api_password"] = "ee_api_password"

    name = "test"
    data = '{"deliveryAttempt": 1, "message": {"data": "eyJzb3VyY2UiOnsiY29kZSI6MSwibmFtZSI6IkNQT1JUQUwifSwidHJhY2tpbmdJZCI6ImM2Mzk4MDExLWNlMDYtNGVlOC1iZGM3LWY1MzE5Zjc3MTJhNyIsImV2ZW50VHlwZSI6IkNoYW5nZSBQcmVmZXJlbmNlIiwgImV2ZW50U3ViVHlwZSI6Ik5vIGxpcXVvciBPZmZlcnMiLCJwdWJsaXNoZWRBdCI6IjIwMjEtMDUtMTkwMzo1ODoxNy4yNDciLCJjcm4iOiIzZmU4Y2RmMjRmNGJiMTNkNWQ1NmM5NGY2ZjUyMjkwYSIsImhhc2hlZENybiI6IjM1NWMzMTAwZDUzNmVhNGYyZThiYjFmNjQ3YjMwM2U3YWE2MjJmMDU2MGVmYzRiNzk4ODQ2MzQwNmYzYjM1OWIiLCJjYXJkTnVtYmVyIjoiOTM1NTA0OTM3OTMyOSIsImNvcnJlbGF0aW9uSWQiOiJjNjM5ODAxMS1jZTA2LTRlZTgtYmRjNy1mNTMxOWY3NzEyYTciLCJwcmVmZXJlbmNlcyI6eyJpZCI6IjEwNDIiLCJ2YWx1ZSI6ZmFsc2V9fQ==", "messageId": "2652670209994957", "message_id": "2652670209994957", "publishTime": "2021-07-11T10:26:03.697Z", "publish_time": "2021-07-11T10:26:03.697Z"}, "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub"}'
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)
    mock_response = mock.MagicMock()
    mock_response.status_code = 404
    mock_get_wallet.side_effect = requests.exceptions.HTTPError(response = mock_response)
    main.main(req)

    # mock_print.assert_called_with('Timeout error')
    assert main.main(req) == "102"


def test_get_header():
    authHash = hashlib.sha256("/2.0service_pathPayloadpassword".encode()).hexdigest()
    transaction_id = 'cde_update_records_ ' + hashlib.md5(str(time.time()).encode()).hexdigest()
    assert main._get_header("http://localhost", "service_path", "Payload", "authClientId", "password")  == {"X-EES-AUTH-HASH": authHash, "X-EES-AUTH-CLIENT-ID": "authClientId",
                                                                                                            "X-TRANSACTION-ID": transaction_id,
                                                                                                            "X-RETRY": "1", "X-EES-OPERATOR": "1", "X-EES-CALLER": "DASHBOARD",
                                                                                                            "X-EES-CALLER-VERSION": "0",
                                                                                                            "Content-Type": "application/json"}



@mock.patch("main._get_header", return_value="Header", autospec=True)
@mock.patch("main._calling_the_request_consumer_object_function", return_value={'walletId': 123}, autospec=True)
def test_get_wallet_id_by_crn(mock__get_header, mock__calling_the_request_consumer_object_function):
    os.environ["ee_get_consumer_service_path"] = "/wallet/{{walletId}}/consumer"
    os.environ["ee_get_wallet_service_path"] = "/wallet?identity-value={{idenitityValueCRN}}"
    os.environ["ee_update_consumer_service_path"] = "/wallet/{{walletId}}/consumer/{{consumerId}}"
    assert main._get_wallet_id_by_crn("url", "authClientId", "password", "crn", "correlationId") == 123



@mock.patch("main._get_header", return_value="Header", autospec=True)
@mock.patch("main._calling_the_request_consumer_object_function", return_value={"consumerId": 123}, autospec=True)
def test_get_consumer_id_by_wallet(mock__get_header, mock__calling_the_request_consumer_object_function):
    os.environ["ee_get_consumer_service_path"] = "/wallet/{{walletId}}/consumer"
    os.environ["ee_get_wallet_service_path"] = "/wallet?identity-value={{idenitityValueCRN}}"
    os.environ["ee_update_consumer_service_path"] = "/wallet/{{walletId}}/consumer/{{consumerId}}"
    assert main._get_consumer_id_by_wallet("url", "authClientId", "password", "wallet_id", "correlationId") == 123



@mock.patch("main._get_header", return_value="Header", autospec=True)
@mock.patch("main._calling_the_request_consumer_object_function", return_value={"walletId": "123"}, autospec=True)
def test_update_consumer_objects_by_wallet_and_consumer_id(mock_get_header, mock_calling_the_request_consumer_object_function):
    os.environ["ee_get_consumer_service_path"] = "/wallet/{{walletId}}/consumer"
    os.environ["ee_get_wallet_service_path"] = "/wallet?identity-value={{idenitityValueCRN}}"
    os.environ["ee_update_consumer_service_path"] = "/wallet/{{walletId}}/consumer/{{consumerId}}"
    assert main._update_consumer_objects_by_wallet_and_consumer_id("url", "authClientId", "password", "wallet_id", "consumer_id", "preference_label", "preference_value", "correlationId") == {"walletId": "123"}



@mock.patch("pymongo.collection.Collection.update_one", return_value = {"a":"b"}, autospec=True)
def test_logging_in_mongodb(mock_update):
    # main._logging_in_mongodb("correlationId", "status_code", "status_message", 0) == 
    os.environ["mongodb_url"] = "mongodb_url"
    os.environ["mongodb_dbname"] = "mongodb_dbname"
    os.environ["mongodb_collection"] = "mongodb_collection"
    main._logging_in_mongodb("correlationId", "status_code", "status_message", 0)
    mock_update.assert_called_once()



@mock.patch("google.pubsub_v1.PublisherClient.publish", return_value = {"a":"b"}, autospec=True)
@mock.patch("concurrent.futures.Future.done", return_value = True)
def test_logging_in_deadletter(mock_publish, mock_done):
    os.environ["GCP_PROJECT"] = "GCP_PROJECT"
    os.environ["error_topic"] = "error_topic"
    os.environ["FUNCTION_NAME"] = "FUNCTION_NAME"

    main._logging_in_deadletter('event_data', "error_message")

    mock_publish.assert_called_once()


'''
@mock.patch("main._get_wallet_id_by_crn", autospec=True)
@mock.patch("main._logging_in_mongodb")
@mock.patch("main._logging_in_deadletter")
@mock.patch("builtins.print")
def test_main_timeout(mock_get_wallet, mock_log_mongo, mock_deadletter, mock_print):
    os.environ["ee_api_url"] = "ee_api_url"
    os.environ["ee_api_user"] = "ee_api_user"
    os.environ["ee_api_password"] = "ee_api_password"

    name = "test"
    data = '{"deliveryAttempt": 1, "message": {"data": "eyJzb3VyY2UiOnsiY29kZSI6MSwibmFtZSI6IkNQT1JUQUwifSwidHJhY2tpbmdJZCI6ImM2Mzk4MDExLWNlMDYtNGVlOC1iZGM3LWY1MzE5Zjc3MTJhNyIsImV2ZW50VHlwZSI6IkNoYW5nZSBQcmVmZXJlbmNlIiwgImV2ZW50U3ViVHlwZSI6Ik5vIGxpcXVvciBPZmZlcnMiLCJwdWJsaXNoZWRBdCI6IjIwMjEtMDUtMTkwMzo1ODoxNy4yNDciLCJjcm4iOiIzZmU4Y2RmMjRmNGJiMTNkNWQ1NmM5NGY2ZjUyMjkwYSIsImhhc2hlZENybiI6IjM1NWMzMTAwZDUzNmVhNGYyZThiYjFmNjQ3YjMwM2U3YWE2MjJmMDU2MGVmYzRiNzk4ODQ2MzQwNmYzYjM1OWIiLCJjYXJkTnVtYmVyIjoiOTM1NTA0OTM3OTMyOSIsImNvcnJlbGF0aW9uSWQiOiJjNjM5ODAxMS1jZTA2LTRlZTgtYmRjNy1mNTMxOWY3NzEyYTciLCJwcmVmZXJlbmNlcyI6eyJpZCI6IjEwNDIiLCJ2YWx1ZSI6ZmFsc2V9fQ==", "messageId": "2652670209994957", "message_id": "2652670209994957", "publishTime": "2021-07-11T10:26:03.697Z", "publish_time": "2021-07-11T10:26:03.697Z"}, "subscription": "projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub"}'
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)
    mock_get_wallet.side_effect = requests.Timeout
    main.main(req)

    # mock_print.assert_called_with('Timeout error')
    assert main.main(req) == "500"
'''