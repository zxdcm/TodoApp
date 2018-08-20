from logging import (getLogger,
                     FileHandler,
                     Formatter,
                     getLevelName)
from functools import wraps
import os


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

    if not os.path.exists(os.path.dirname(log_file_path)):
        os.makedirs(os.path.dirname(log_file_path))
        try:
            open(log_file_path, 'r').close()
        except FileNotFoundError:
            open(log_file_path, 'w').close()

    handler = FileHandler(log_file_path)

    logger = get_logger()
    logger.setLevel(getLevelName(log_level))

    formatter = Formatter(format)
    handler.setFormatter(formatter)

    if log_enabled:
        logger.disabled = False
        logger.addHandler(handler)
    else:
        logger.disabled = True
