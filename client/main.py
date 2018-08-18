from client.parsers import get_args
from client.handlers import commands_handler
from lib.services import AppService


def main():

    args = get_args()
    service = AppService()
#    x = service.get_task_by_id(user_id=1, task_id=2)
    args.user_id = 2
    service.execute_plans(args.user_id)
    commands_handler(service, args)


main()
