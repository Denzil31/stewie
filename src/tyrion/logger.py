import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class LogConfig(BaseModel):
    LOGGER_NAME: str = 'tyrion'
    LOG_FORMAT: str = '%(levelprefix)s | %(asctime)s | %(message)s'
    LOG_LEVEL: str = 'DEBUG'
    LOG_FILE_PATH: str = os.getenv('LOG_PATH')

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': LOG_FORMAT,
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    }
    handlers: dict = {
        'rotating_file': {
            'formatter': 'default',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'when': 'midnight',
            'interval': 1,
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    }
    loggers: dict = {
        LOGGER_NAME: {'handlers': ['rotating_file', 'default'], 'level': LOG_LEVEL},
    }
