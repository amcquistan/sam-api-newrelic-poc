import hashlib
import json
import logging
import os

import boto3
import requests

from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from newrelic import agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Quote:
    def __init__(self, text, author, tags):
        self.text = text.strip().replace(r'“', '').replace(r'”', '')
        self.author = author
        self.tags = tags

        hash_input = f"{self.author}{self.text}".encode('utf-8')
        self.id = hashlib.sha256(hash_input).hexdigest()

    def save(self):
        tbl = boto3.resource('dynamodb').Table(os.environ['QUOTES_TABLE'])
        tbl.put_item(Item=self.to_dict())

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'author': self.author,
            'tags': self.tags
        }


def lambda_handler(event, context):
    # This is an example of a custom event. `FROM MyPythonEvent SELECT *` in New Relic will find this event.
    agent.record_custom_event("MyPythonEvent", {
        "zip": "zap"
    })
    # This attribute gets added to the normal AwsLambdaInvocation event
    agent.add_custom_parameter('customAttribute', 'customAttributeValue')
    try:
        logging.info({'event': event})
        response = requests.get("https://quotes.toscrape.com/random")
        soup = BeautifulSoup(response.content)
        quote_el = soup.find('div', class_='quote')

        quote = Quote(
            text=quote_el.find('span', class_='text').get_text(),
            author=quote_el.find('small', class_='author').get_text(),
            tags=[el.get_text() for el in quote_el.find_all('a', class_='tag')]
        )
        quote.save()
        return {
            'statusCode': 201,
            'body': json.dumps(quote.to_dict())
        }
    except RequestException as e:
        logger.error({'exception': repr(e)})
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to generate quote.'})
        }
