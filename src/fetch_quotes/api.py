import json
import logging
import os

from base64 import b64decode

import boto3
from boto3.dynamodb.conditions import Key

from newrelic import agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # This is an example of a custom event. `FROM MyPythonEvent SELECT *` in New Relic will find this event.
    agent.record_custom_event("MyPythonEvent", {
        "zip": "zap"
    })
    # This attribute gets added to the normal AwsLambdaInvocation event
    agent.add_custom_parameter('customAttribute', 'customAttributeValue')
    headers = {}
    if event['headers']:
        headers = {k.lower(): v for k, v in event['headers'].items()}

    if 'authorization' not in headers:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'not authenticated'}),
            'headers': {
                'www-authenticate': 'Basic'
            }
        }

    auth_value = headers['authorization']
    _, creds_encoded = auth_value.split()
    username, passwd = b64decode(creds_encoded).decode('utf-8').split(':')
    username = username.lower()

    try:
        favorites_tbl = boto3.resource('dynamodb').Table(os.environ['FAVORITE_QUOTES_TABLE'])
        favorites_response = favorites_tbl.query(KeyConditionExpression=Key('username').eq(username))
        keys = [
            { 'id': { 'S':  'a02d34132913c901baef5707b2d3b2a6e7e38797ca4272ecf967c81f1e137e64' } },
            { 'id': { 'S':  'a5e94583af7b5c01d01e89ee6aa2104ee1246c5617e2a1820a2bcaf20f1e77eb' } }
        ]

        keys = [{'id': { 'S': fav_quote['quoteid'] }} for fav_quote in favorites_response['Items']]
        quotes_response = boto3.client('dynamodb').batch_get_item(RequestItems={ 'quotes': { 'Keys': keys } })

        quotes = []
        for quote in quotes_response['Responses']['quotes']:
            quotes.append({
                'id': quote['id']['S'],
                'author': quote['author']['S'],
                'text': quote['text']['S'],
                'tags': [t['S'] for t in quote['tags']['L']]
            })

        return {
            'statusCode': 200,
            'body': json.dumps(quotes)
        }

    except Exception as e:
        logger.error({'exception': repr(e)})
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to fetch favorite quotes.'})
        }