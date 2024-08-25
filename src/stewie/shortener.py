import re
import hashlib
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlparse

from .exceptions import (
    ShortCodeAlreadyExistsError,
    MaxRetriesExceededError,
    InvalidShortCodeError,
    ExpiryTooHighError,
    InvalidLongUrlError,
)


class URLShortener:
    def __init__(self, database):
        self.database = database

    def sanitize(self, short_code):
        pattern = re.compile(r'^[a-zA-Z0-9-]+$')
        if not pattern.match(short_code):
            raise InvalidShortCodeError()
        return short_code

    def validate_url(self, long_url):
        try:
            # Check if the scheme is missing and add 'https' as the default scheme
            if not urlparse(long_url).scheme:
                long_url = f'https://{long_url}'
            parsed_url = urlparse(long_url)
            if parsed_url.scheme not in ['http', 'https'] or not parsed_url.netloc:
                raise InvalidLongUrlError
        except ValueError:
            raise InvalidLongUrlError

    def shorten_url(self, long_url, short_code=None, expires_in=30):
        if expires_in > 525960:  # A year in minutes
            raise ExpiryTooHighError()

        self.validate_url(long_url)

        if short_code:
            short_code = self.sanitize(short_code)
            url, _ = self.database.get_url_mapping(short_code, incr=False)
            if url:
                raise ShortCodeAlreadyExistsError()
        else:
            short_code = self.get_short_code(long_url)

        expires_at = int((datetime.now() + timedelta(minutes=expires_in)).timestamp())

        # Add the URL mapping to the database
        self.database.add_url_mapping(short_code, long_url, expires_at)
        return short_code

    def get_short_code(self, data, length=5, max_retries=10):
        salt = secrets.token_hex(4)
        salted_data = f'{data}-{salt}'

        sha256 = hashlib.sha256()
        sha256.update(salted_data.encode('utf-8'))
        hash_value = sha256.hexdigest()

        while True:
            if max_retries == 0:
                raise MaxRetriesExceededError()

            short_code = hash_value[:length]
            long_url, _ = self.database.get_url_mapping(short_code, incr=False)
            if not long_url:
                return short_code

            length += 1
            max_retries -= 1

    def get_long_url(self, short_code):
        short_code = self.sanitize(short_code)
        long_url, error = self.database.get_url_mapping(short_code)
        if error:
            raise error
        return long_url
