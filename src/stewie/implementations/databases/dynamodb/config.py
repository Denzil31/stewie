import os

from src.stewie.interfaces.database import DatabaseConfigInterface
from src.stewie.exceptions import ConfigError


class DynamoDBConfig(DatabaseConfigInterface):
    def __init__(self, config_file='config.ini'):
        self.resource = 'dynamodb'
        self.table = self.get_table_name()
        self.access_key = self.get_access_key()
        self.secret_key = self.get_secret_key()
        self.region = self.get_region()
        self.url = self.get_url()
        super().__init__()

    def get_table_name(self):
        table = os.getenv('DB_TABLE')
        if not table:
            raise ConfigError('Table name not found in configuration file.')
        return table

    def get_access_key(self):
        access_key = os.getenv('DB_ACCESS_KEY')
        if not access_key:
            raise ConfigError('Access key not found in configuration file.')
        return access_key

    def get_secret_key(self):
        secret_key = os.getenv('DB_SECRET_KEY')
        if not secret_key:
            raise ConfigError('Secret key not found in configuration file.')
        return secret_key

    def get_region(self):
        region = os.getenv('DB_REGION')
        if not region:
            raise ConfigError('Region not found in configuration file.')
        return region

    def get_url(self):
        url = os.getenv('DB_URL')
        if not url:
            raise ConfigError('URL not found in configuration file.')
        return url
