from logging import (getLogger,
                     DEBUG,
                     WARNING,
                     Formatter,
                     FileHandler)
from functools import wraps
from lib.exceptions import BaseLibError


def get_logger():
    return getLogger('todolib')


def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.info(f'call: {func.__name__}')
        logger.debug(f'args: {args}')
        logger.debug(f'kwargs: {kwargs}')
        try:
            result = func(*args, **kwargs)
            logger.debug(f'result: {result}')
            return result
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            raise e
        return result
    return wrapper


def setup_lib_logging(FILEPATH, FORMAT):
    formatter = Formatter(FORMAT)
    handler = FileHandler(FILEPATH)
    handler.setLevel(DEBUG)
    handler.setFormatter(formatter)

    logger = get_logger()
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
