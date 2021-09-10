#!/usr/bin/env python3

# Microblogging - Direct Messaging MicroService API

import bottle
from bottle import post, get, request, delete, HTTPResponse
import sqlite3
import json
import boto3
from boto3.dynamodb.conditions import Key
import uuid
import datetime


# Setup app
app = bottle.default_app()


@post('/messages/')
def sendDirectMessage():
    
    result = {}
    headers = {'Content-type': 'application/json'}

    # Flag indicating if quickReplies were provided
    qR_flag = False

    body = request.json
    # print(body.keys())

    # Check that valid inputs were provided
    to_username = body['to']
    if type(to_username) is not str:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "to" does not contain a string'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    from_username = body['from']
    if type(from_username) is not str:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "from" does not contain a string'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    message = body['message']
    if type(message) is not str:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "message" does not contain a string'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    if "quickReplies" in body.keys():
        quickReplies = body['quickReplies']
        # print(quickReplies)
        if type(quickReplies) is list:
            qR_flag = True
        elif quickReplies is None:
            pass
        else:
            result['status'] = "400 Bad Request"
            result['error'] = 'JSON entry "quickReplies" is defined, but is not a list'
            return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    # Create message
    message_entry = {}
    # Assign random id
    message_entry["message_id"] = str(uuid.uuid4())
    # Assign message details
    message_entry["to_username"] = to_username
    message_entry["from_username"] = from_username
    message_entry["message"] = message
    message_entry["timestamp"] = str(datetime.datetime.utcnow())
    # Check and Assign quick replies
    if qR_flag:
        message_entry["quick_replies"] = quickReplies
    
    # Access database
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    # Get table
    table = dynamodb.Table('messages')
    # Insert message into messages table
    table.put_item(Item=message_entry)

    # Return result
    result['status'] = "200 OK"
    result['sent'] = True
    return HTTPResponse(body=json.dumps(result),status=200,headers=headers)


@post('/messages/<messageId>/replies/')
def replyToDirectMessage(messageId):

    result = {}
    headers = {'Content-type': 'application/json'}

    # Flag indicating a quickReply response was given
    qR_flag = False
    
    body = request.json

    # Check that valid input was provided
    message = body['message']
    if type(message) is str:
        # Regular string message, continues
        pass
    elif type(message) is int:
        # Integer indicates quickReply response
        qR_flag = True
    else:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "message" does not contain a string or integer'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)
        
    # Access database
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    # Get table
    table = dynamodb.Table('messages')
    # Get message to reply to
    response = table.get_item(
        Key={'message_id':messageId}
    )

    # Check if message with matching id was found
    item = {}
    if "Item" in response.keys():
        item = response["Item"]
    else:
        result['status'] = "404 Not Found"
        result['error'] = 'No message matching messageId'
        return HTTPResponse(body=json.dumps(result),status=404,headers=headers)
    
    # print(item)

    # Create message
    message_entry = {}
    # Assign random id
    message_entry["message_id"] = str(uuid.uuid4())
    # Set to reply to message via id
    message_entry["in_reply_to"] = item["message_id"]
    # Reverse to and from, since it's a reply
    message_entry["to_username"] = item["from_username"]
    message_entry["from_username"] = item["to_username"]
    # Check quickReply
    if qR_flag:
        # If the message contained quick reply options
        if "quick_replies" in item.keys():
            # And a valid quick reply option was given
            if message in range(len(item["quick_replies"])):
                # Assign message via quick reply
                message_entry["message"] = item["quick_replies"][message]
            else:
                result['status'] = "400 Bad Request"
                result['error'] = 'Quick reply value out of range of quick_replies'
                return HTTPResponse(body=json.dumps(result),status=400,headers=headers)
        else:
            result['status'] = "400 Bad Request"
            result['error'] = 'Quick reply value given, but no quick_replies exist'
            return HTTPResponse(body=json.dumps(result),status=400,headers=headers)
    else:
        # If not quickReply, assign message string
        message_entry["message"] = message
    # Assign timestamp
    message_entry["timestamp"] = str(datetime.datetime.utcnow())

    # Insert reply message into messages table
    table.put_item(Item=message_entry)
    
    # Return result
    result['status'] = "200 OK"
    result['sent'] = True
    return HTTPResponse(body=json.dumps(result),status=200,headers=headers)


@get('/messages/')
def listDirectMessagesFor():
    
    result = {}
    headers = {'Content-type': 'application/json'}

    username = request.query.username
    if type(username) is not str:
        result['status'] = "400 Bad Request"
        result['error'] = 'username query missing or is not a string'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    # Access database
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    # Get table
    table = dynamodb.Table('messages')
    # Query messages by author, via from_username key
    authored = table.query(
        IndexName="author",
        KeyConditionExpression=Key('from_username').eq(username)
    )
    # Query messages by recipient, via to_username key
    received = table.query(
        IndexName="recipient",
        KeyConditionExpression=Key('to_username').eq(username)
    )

    # If both queries are empty
    if (authored["Count"] == 0) and (received["Count"] == 0):
        result['status'] = "200 OK"
        result['messages'] = []
        return HTTPResponse(body=json.dumps(result),status=200,headers=headers)

    # Get message ids, transform for batch get
    uuids1 = []
    if authored["Count"] != 0:
        uuids1 = [{"message_id":i.get("message_id")} for i in authored["Items"]]
    
    uuids2 = []
    if received["Count"] != 0:
        uuids2 = [{"message_id":i.get("message_id")} for i in received["Items"]]

    uuids1.extend(uuids2)
    # print(uuids)

    # Batch get messages from messages table, via message_id keys
    response = dynamodb.batch_get_item(
        RequestItems={
            "messages": {
                "Keys": uuids1
            }
        }
    )

    # Get retreived messages
    messages = response["Responses"]["messages"]

    # Return messages
    result['status'] = "200 OK"
    result['messages'] = messages
    return HTTPResponse(body=json.dumps(result),status=200,headers=headers)


@get('/messages/<messageId>/replies/')
def listRepliesTo(messageId):

    result = {}
    headers = {'Content-type': 'application/json'}

    # Access database
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    # Get table
    table = dynamodb.Table('messages')
    # Query all replies to a message, via in_reply_to key
    response = table.query(
        IndexName="replies",
        KeyConditionExpression=Key('in_reply_to').eq(messageId)
    )

    # If query result is empty
    if response["Count"] == 0:
        result['status'] = "200 OK"
        result['messages'] = []
        return HTTPResponse(body=json.dumps(result),status=200,headers=headers)

    # Get message ids and transform for batch get
    uuids = [{"message_id":i.get("message_id")} for i in response["Items"]]
    # print(uuids)

    # Batch get messages from messages table, via message_id keys
    response = dynamodb.batch_get_item(
        RequestItems={
            "messages": {
                "Keys": uuids
            }
        }
    )

    # Get retreived messages
    messages = response["Responses"]["messages"]

    # Return messages
    result['status'] = "200 OK"
    result['messages'] = messages
    return HTTPResponse(body=json.dumps(result),status=200,headers=headers)


