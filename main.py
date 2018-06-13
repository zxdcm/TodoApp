import argparse
from lib.services import AppService, Task
from datetime import datetime


def task_command(service: AppService, *args, **kwargs):
    if kwargs['action'] == 'create':
        service.create_task(**kwargs)
    elif kwargs['action'] == 'delete':
        service.delete_task_by_id(kwargs['id'])
    elif kwargs['action'] == 'list':
        [print(x) for x in service.get_user_tasks()]


if __name__ == '__main__':

    taskparser = argparse.ArgumentParser(
        prog='tracker', description='CLI for task tracker')
    taskparser.add_argument('action',
                            choices=['add', 'update', 'delete', 'list'])
    taskparser.add_argument('--name')
    taskparser.add_argument('--id')
    taskparser.add_argument('-d', '--description')
    taskparser.add_argument('-sd', '--start_date')
    taskparser.add_argument('-ed', '--end_date')
    taskparser.add_argument('-u', '--assign')
    taskparser.add_argument('-g', '--group')
    taskparser.add_argument('-s', '--status')
    taskparser.add_argument('-p', '--priority')
    # taskparser = parser.add_subparsers('task')

    # user = AppService.create_user(name='username', email='user')
    # api = AppService()
    api = AppService('user')
    # print(type(api.get_user_folders()))
    arguments = taskparser.parse_args()
    task_command(api, **vars(arguments))
    # api.create_task('nscame', 'descr')
    # dict = {'name': 'test', 'description': 'test',
    #         'start_date': datetime.now(), }
    # api.create_task(**dict)
    # [print(x.start_date) for type(x) in api.get_user_tasks()]
    # print(api.get_user_folders())
    # [print(x.description) for x in api.get_user_tasks()]
    # [print(x) for x in api.get_user_groups()]
