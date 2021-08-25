
import json
import logging
import os

from base64 import b64decode

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
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

    quote_id = json.loads(event['body']).get('id')

    try:
        quotes_tbl = boto3.resource('dynamodb').Table(os.environ['QUOTES_TABLE'])
        quotes_response = quotes_tbl.get_item(Key={'id': quote_id})
        if 'Item' not in quotes_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'No quote associated with id {quote_id}'})
            }

        favorites_tbl = boto3.resource('dynamodb').Table(os.environ['FAVORITE_QUOTES_TABLE'])
        favorites_tbl.put_item(Item={'username': username, 'quoteid': quote_id})

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'saved to favorites'})
        }

    except Exception as e:
        logger.error({'exception': repr(e)})
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to save quote to favorites.'})
        }