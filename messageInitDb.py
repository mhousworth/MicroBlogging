#!/usr/bin/env python3

# Microblogging - Message Database Initial Schema Script

import boto3
import uuid
import requests


def create_message_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        TableName='messages',
        KeySchema=[
            {
                'AttributeName': 'message_id',
                'KeyType': 'HASH'  # Partition key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'message_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'from_username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'to_username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'in_reply_to',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        },
        GlobalSecondaryIndexes=[
            {
                "IndexName": "author",
                "KeySchema": [
                    {
                        "AttributeName": "from_username",
                        "KeyType": "HASH"
                    }
                ],
                "Projection": {
                    "ProjectionType": "KEYS_ONLY"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                }
            },
            {
                "IndexName": "recipient",
                "KeySchema": [
                    {
                        "AttributeName": "to_username",
                        "KeyType": "HASH"
                    }
                ],
                "Projection": {
                    "ProjectionType": "KEYS_ONLY"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                }
            },
            {
                "IndexName": "replies",
                "KeySchema": [
                    {
                        "AttributeName": "in_reply_to",
                        "KeyType": "HASH"
                    }
                ],
                "Projection": {
                    "ProjectionType": "KEYS_ONLY"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                }
            }
        ],
    )
    return table


def populate_message_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    # Sample Authentication from users database
    joeAuth = ('Joe','Clone3')
    michaelAuth = ('Michael','SqwkBoi')

    # Sample use of sendDirectMessage() in messageService
    dt = {"to":"Michael","from":"Joe","message":"Pull Request?","quickReplies":["OK","Busy"]}
    r = requests.post(url = 'http://localhost:5000/messages/', json=dt, auth=joeAuth)

    # Sample use of listDirectMessagesFor() in messageService
    r = requests.get(url = 'http://localhost:5000/messages/?username=Michael', auth=michaelAuth)
    messages = r.json().get("messages")
    message_id = messages[0].get("message_id")

    # Sample use of replyToDirectMessage() in messageService, using quick reply option
    dt = {"message":1}
    r = requests.post(url = 'http://localhost:5000/messages/{}/replies/'.format(message_id), json=dt, auth=michaelAuth)

    # Sample use of listRepliesTo() in messageService
    r = requests.get(url = 'http://localhost:5000/messages/{}/replies/'.format(message_id), auth=joeAuth)
    messages = r.json().get("messages")
    message_id = messages[0].get("message_id")

    # Sample use of replyToDirectMessage() in messageService, using string message
    dt = {"message":"That's fine get back to me when you can."}
    r = requests.post(url = 'http://localhost:5000/messages/{}/replies/'.format(message_id), json = dt, auth=joeAuth)
    

if __name__ == '__main__':
    message_table = create_message_table()
    print("Table status:", message_table.table_status)
    populate_message_table()