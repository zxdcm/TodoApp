"""
    Module contains functions
"""

from logging import (getLogger,
                     FileHandler,
                     Formatter,
                     getLevelName)
from functools import wraps
import os


def get_logger():
    """
    Returns library logger
    """
    return getLogger('todolib')


def log_decorator(func):
    """
    Allows to wrap library methods with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.info(f'call: {func.__name__}')
        logger.debug(f'args: {args}')
        logger.debug(f'kwargs: {kwargs}')
        try:
            result = func(*args, **kwargs)
            logger.debug(f'result:\n {result}')
            return result
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            raise e
        return result
    return wrapper


def setup_lib_logging(log_file_path='/todoapp.log',
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                      log_level='DEBUG',
                      log_enabled=True):
    """Allows to setup logging settings
    Parameters
    ----------
    log_file_path : str
    format : str
    log_level : str
    log_enabled : Bool
    """

    logger = get_logger()

    if log_enabled:

        handler = FileHandler(log_file_path)

        formatter = Formatter(format)
        handler.setFormatter(formatter)

        level = getLevelName(log_level)
        logger.setLevel(level)

        if logger.hasHandlers():
            logger.handlers.clear()

        logger.disabled = False
        logger.addHandler(handler)

    else:
        logger.disabled = True

