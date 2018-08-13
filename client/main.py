from client.parsers import get_args
from client.handlers import commands_handler
from lib.services import AppService


def main():
    args = get_args()
    service = AppService()
    args.user_id = 1
    commands_handler(service, args)


if __name__ == '__main__':
    main()
