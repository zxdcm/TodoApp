from client.parsers import get_args
from client.handlers import commands_handler
from lib.services import AppService
from lib.logging import setup_lib_logging
from lib.models import set_up_connection
from client.user_service import UserService
import client.config as config
import os
import warnings

def main():

    log_file_path = os.path.join(config.LOGS_DIRECTORY, config.LOG_FILE)

    setup_lib_logging(log_file_path=log_file_path,
                      format=config.LOG_FORMAT,
                      log_enabled=config.LOG_ENABLED,
                      log_level=config.LOG_LEVEL)

    session = set_up_connection(config.CONNECTION_STRING)

    service = AppService(session)
    user_serv = UserService(session, config.CONFIG_FILE)
    args = get_args()
    warnings.filterwarnings('error')
    user = user_serv.get_current_user()
    if user:
        service.execute_plans(user.username)

    commands_handler(service, args, user_serv)


main()
