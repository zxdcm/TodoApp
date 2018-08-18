from client.parsers import get_args
from client.handlers import commands_handler
from lib.services import AppService
from lib.logging import setup_lib_logging

FILEPATH = './todolib.log'
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def main():

    setup_lib_logging(FILEPATH, FORMAT)
    args = get_args()
    service = AppService()
    args.user_id = 2
    service.execute_plans(args.user_id)
    commands_handler(service, args)


main()
