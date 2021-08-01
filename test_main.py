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



def test_parse_request():
    name = "test"
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
    req = mock.Mock(get_json=mock.Mock(return_value=data), args=data)
    

    a = main._parse_request(req)
    print(a.get('event_data_str'))

    assert main._parse_request(req) == {'delivery_attempt': 1,
                                        'event_sub_types': 'redemption',
                                        'operation': 'update',
                                        'tracking_id': '1b671a64-40d5-491e-99b0-da01ff1f3341', 
                                        'correlation_id': 'a8ee6a90-ccbc-4678-8230-a4a65fbf7004', 
                                        'crn': '3300000000034535748', 
                                        'preferences': [{"id": 1024, "name": "Unsubscribe All", "value": "QFF"}],
                                        'event_data_str': b'{"eventType": "preferences", "eventSubType": "redemption", "operation": "update", "eventDetails": {"source": {"code": 1, "name": "CPORTAL"}, "trackingId": "1b671a64-40d5-491e-99b0-da01ff1f3341", "publishedAt": "2018-11-11T11:01:59+11:11", "correlationId": "a8ee6a90-ccbc-4678-8230-a4a65fbf7004", "profile": {"crn": "3300000000034535748", "crnHash": "7a30398d3e11bfecb7c9e7b014adfgdfg6463c768cc35b942d6ec44af66f185", "account": {"accountType": {"code": 1002, "name": "EDR"}, "cardNumber": "9355049379329", "preferences": [{"id": 1024, "name": "Unsubscribe All", "value": "QFF"}]}}}}'
                                        }


def test_prepare_preference_payload():
    assert main._prepare_preference_payload('redemption', [{"id": 1024, "name": "Unsubscribe All", "value": "QFF"}]) == '{"friendlyName": "Consumer Details", "data": {"dimension": [{"label": "redemptionSetting", "value": "QFF"}]}}'


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
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
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
    data = {'deliveryAttempt': 1, 'message': {'dataa': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
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
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
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
    data = {'deliveryAttempt': 1, 'message': {'data': 'eyJldmVudFR5cGUiOiAicHJlZmVyZW5jZXMiLCAiZXZlbnRTdWJUeXBlIjogInJlZGVtcHRpb24iLCAib3BlcmF0aW9uIjogInVwZGF0ZSIsICJldmVudERldGFpbHMiOiB7InNvdXJjZSI6IHsiY29kZSI6IDEsICJuYW1lIjogIkNQT1JUQUwifSwgInRyYWNraW5nSWQiOiAiMWI2NzFhNjQtNDBkNS00OTFlLTk5YjAtZGEwMWZmMWYzMzQxIiwgInB1Ymxpc2hlZEF0IjogIjIwMTgtMTEtMTFUMTE6MDE6NTkrMTE6MTEiLCAiY29ycmVsYXRpb25JZCI6ICJhOGVlNmE5MC1jY2JjLTQ2NzgtODIzMC1hNGE2NWZiZjcwMDQiLCAicHJvZmlsZSI6IHsiY3JuIjogIjMzMDAwMDAwMDAwMzQ1MzU3NDgiLCAiY3JuSGFzaCI6ICI3YTMwMzk4ZDNlMTFiZmVjYjdjOWU3YjAxNGFkZmdkZmc2NDYzYzc2OGNjMzViOTQyZDZlYzQ0YWY2NmYxODUiLCAiYWNjb3VudCI6IHsiYWNjb3VudFR5cGUiOiB7ImNvZGUiOiAxMDAyLCAibmFtZSI6ICJFRFIifSwgImNhcmROdW1iZXIiOiAiOTM1NTA0OTM3OTMyOSIsICJwcmVmZXJlbmNlcyI6IFt7ImlkIjogMTAyNCwgIm5hbWUiOiAiVW5zdWJzY3JpYmUgQWxsIiwgInZhbHVlIjogIlFGRiJ9XX19fX0=', 'messageId': '2754332662377047', 'message_id': '2754332662377047', 'publishTime': '2021-08-01T13:48:51.299Z', 'publish_time': '2021-08-01T13:48:51.299Z'}, 'subscription': 'projects/gcp-wow-rwds-etl-dev/subscriptions/data-dev-p24-partner-loyalty-api-sub'}
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
    assert main._get_header( "service_path", "Payload", "authClientId", "password", "correlationId")  == {"X-EES-AUTH-HASH": authHash, "X-EES-AUTH-CLIENT-ID": "authClientId",
                                                                                                            "X-TRANSACTION-ID": 'correlationId' + '-' + str(time.time()),
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
    assert main._update_consumer_objects_by_wallet_and_consumer_id("url", "authClientId", "password", "wallet_id", "consumer_id", "preference_payload", "correlationId") == {"walletId": "123"}



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