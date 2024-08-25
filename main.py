import os
import logging
from logging.config import dictConfig
from urllib.parse import urlparse

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from src.stewie.implementations.databases import DynamoDB, DynamoDBConfig
from src.stewie import URLShortener, LogConfig
from src.stewie.exceptions import (
    ShortCodeNotFoundError,
    ShortCodeAlreadyExistsError,
    LinkExpiredError,
    MaxRetriesExceededError,
    DatabaseError,
    InvalidShortCodeError,
    ExpiryTooHighError,
    InvalidLongUrlError,
)

# Load configuration
load_dotenv()


# Initialize logging
logging_config = LogConfig()
dictConfig(logging_config.dict())
logger = logging.getLogger(logging_config.LOGGER_NAME)


# Initialize FastAPI app
app = FastAPI(
    title='URL Shortener',
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['OPTIONS', 'GET', 'POST'],
    allow_headers=['*'],
)


# Initialize database
config = DynamoDBConfig()
db = DynamoDB(config)


# Define Pydantic models
class ShortenRequest(BaseModel):
    long_url: str
    short_code: str = None
    expires_in: int = None  # Expiration timestamp in minutes


class ShortURL(BaseModel):
    short_code: str


# Define an API key header
api_key_header = APIKeyHeader(name='X-API-Key')


# Function to validate API key
def validate_api_key(api_key: str = Depends(api_key_header)):
    valid_keys = [key for key in os.getenv('API_KEYS').split(',') if key]
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API key',
        )
    return api_key


# Endpoint to shorten URLs
@app.post('/shorten', response_model=ShortURL)
async def shorten_url(
    request: ShortenRequest, api_key: str = Depends(validate_api_key)
):
    try:
        shortener = URLShortener(db)

        expires_in = request.expires_in
        if not expires_in:
            expires_in = 30

        short_code = shortener.shorten_url(
            request.long_url, short_code=request.short_code, expires_in=expires_in
        )
        content = {'short_code': short_code}
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)
    except (
        ShortCodeAlreadyExistsError,
        MaxRetriesExceededError,
        DatabaseError,
        InvalidShortCodeError,
        ExpiryTooHighError,
        InvalidLongUrlError,
    ) as e:
        content = {'message': e.message}
        return JSONResponse(status_code=e.code, content=content)


# Endpoint for health check
@app.get('/ping')
async def ping():
    logger.info('pong')
    return {'message': 'pong'}


# Endpoint to redirect to long URL
@app.get('/{short_code}')
async def redirect_to_long_url(short_code: str, request: Request):
    try:
        shortener = URLShortener(db)
        long_url = shortener.get_long_url(short_code)
        # Check if the scheme is missing and add 'https' as the default scheme
        # Else, redirect will fail and treats the long_url
        # as the short_code and will try to redirect to it
        if not urlparse(long_url).scheme:
            long_url = f'https://{long_url}'
        return RedirectResponse(long_url, status_code=status.HTTP_302_FOUND)
    except (
        ShortCodeNotFoundError,
        LinkExpiredError,
        DatabaseError,
        InvalidShortCodeError,
    ) as e:
        content = {'message': e.message}
        return JSONResponse(status_code=e.code, content=content)
