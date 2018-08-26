from todolib.services import AppService
from todolib.logging import setup_lib_logging
from todolib.models import set_up_connection
from todocli.parsers import get_args
from todocli.handlers import commands_handler
from todocli.user_service import UserService
import todocli.config as config


import os
import warnings


def main():

    if not os.path.exists(config.APP_DATA_DIRECTORY):
        os.makedirs(config.APP_DATA_DIRECTORY)
    log_file_path = os.path.join(config.LOGS_DIRECTORY, config.LOG_FILE)

    setup_lib_logging(log_file_path=log_file_path,
                      format=config.LOG_FORMAT,
                      log_enabled=config.LOG_ENABLED,
                      log_level=config.LOG_LEVEL)

    session = set_up_connection(config.DRIVER_NAME, config.CONNECTION_STRING)
    service = AppService(session)
    user_serv = UserService(session, config.CONFIG_FILE)

    args = get_args()

    user = user_serv.get_current_user()
    if user:
        service.execute_plans(user.username)

    warnings.filterwarnings('error')
    commands_handler(service, args, user_serv)


if __name__ == '__main__':
    main()
