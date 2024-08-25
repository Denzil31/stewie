import os
import logging
from datetime import datetime

import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

from src.stewie.exceptions import (
    DatabaseError,
    LinkExpiredError,
    ShortCodeNotFoundError,
)
from src.stewie.interfaces.database import DatabaseInterface

load_dotenv()
logger = logging.getLogger(__name__)


class DynamoDB(DatabaseInterface):
    def __init__(self, DynamoDBConfig):
        self.config = DynamoDBConfig
        self.dynamodb = (
            boto3.resource(
                self.config.resource,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region,
            )
            if os.getenv('ENV') == 'prod'
            else boto3.resource(
                self.config.resource,
                region_name=self.config.region,
                endpoint_url=self.config.url,
            )
        )

    def _update_access_count(self, short_code):
        # Increment the counter on every long URL get
        # Doc ref. https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html#WorkingWithItems.AtomicCounters
        try:
            table = self.dynamodb.Table(self.config.table)
            table.update_item(
                Key={'short_code': short_code},
                UpdateExpression='SET access_count = if_not_exists(access_count, :init) + :val',
                ExpressionAttributeValues={':val': 1, ':init': 0},
                ReturnValues='UPDATED_NEW',
            )
        except ClientError as e:
            # Doc ref. https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
            msg = f'{e.response["Error"]["Code"]} - {e.response["Error"]["Message"]}'
            logger.error(msg)
            raise DatabaseError()

    def add_url_mapping(self, short_code, long_url, expires_at):
        try:
            table = self.dynamodb.Table(self.config.table)
            item = {
                'short_code': short_code,
                'long_url': long_url,
                'access_count': 0,
                'created_at': int(datetime.now().timestamp()),
                'expires_at': expires_at,
            }
            table.put_item(Item=item)
            return item
        except ClientError as e:
            # Doc ref. https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
            msg = f'{e.response["Error"]["Code"]} - {e.response["Error"]["Message"]}'
            logger.error(msg)
            raise DatabaseError()

    def get_url_mapping(self, short_code, incr=True):
        try:
            table = self.dynamodb.Table(self.config.table)
            key = {'short_code': short_code}
            response = table.get_item(Key=key)
            item = response.get('Item')
            if not item:
                return None, ShortCodeNotFoundError()

            expires_at = item.get('expires_at')
            if expires_at and expires_at < int(datetime.now().timestamp()):
                return item.get('long_url'), LinkExpiredError()

            if incr:
                self._update_access_count(short_code)
            return item.get('long_url'), None
        except ClientError as e:
            # Doc ref. https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
            msg = f'{e.response["Error"]["Code"]} - {e.response["Error"]["Message"]}'
            logger.error(msg)
            raise DatabaseError()
