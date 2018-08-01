import argparse
import sys
from lib.services import AppService, Task, TaskPriority
from datetime import datetime


class UserSession:

    def __init__(self):
        pass

    def login(self, email, password):
        pass


def commands_handler(service: AppService, namespace, *args, **kwargs):
    if namespace.entity == 'task':
        if namespace.action == 'create':
            task = service.create_task(user_id=namespace.user_id,
                                       name=namespace.name,
                                       description=namespace.description,
                                       start_date=namespace.start_date,
                                       end_date=namespace.end_date,
                                       parent_task_id=namespace.parent,
                                       priority=namespace.priority)
            print(task)
        elif namespace.action == 'show':
            if namespace.task_id == -1:
                [print(x) for x in service.get_own_tasks(namespace.user_id)]
            else:
                print(service.get_task(namespace.user_id,
                                       namespace.task_id))
        elif namespace.action == 'share':
            if namespace.user_receiver_id is None:
                namespace.user_receiver_id = service.get_user_by_email(
                    namespace.user_receiver_email).id
            service.share_task(user_owner_id=namespace.user_id,
                               task_id=namespace.task_id,
                               user_receiver_id=namespace.user_receiver_id)
        elif namespace.action == 'edit':
            # rework
            task_args = {'name': namespace.name,
                         'description': namespace.description,
                         'start_date': namespace.start_date,
                         'end_date': namespace.end_date}

            service.update_task(user_id=namespace.user_id,
                                task_id=namespace.task_id,
                                args=task_args)
            # if kwargs['action'] == 'create':
            #     service.create_task(**kwargs)
            # elif kwargs['action'] == 'delete':
            #     service.delete_task_by_id(kwargs['id'])
            # elif kwargs['action'] == 'list':
            #     [print(x) for x in service.get_user_tasks()]
            # elif kwargs['action'] == 'archive':
            #     print(service.archive_task_by_id(kwargs['id']))


def func_task_parser(sup_parser: argparse):
    task_parser = sup_parser.add_parser('task')

    task_subparser = task_parser.add_subparsers(dest='action')
    create = task_subparser.add_parser('create',
                                       help='Create new task',
                                       )
    create.add_argument('name',
                        help='Task name')
    create.add_argument('-d', '--description',
                        help='Task description')
    create.add_argument('-sd', '--start_date', type=datetime,
                        help='Set start date. Current time by default')
    create.add_argument('-ed', '--end_date', type=datetime,
                        help='Set end date')
    create.add_argument('-p', '--parent', type=int,
                        help='Parent task id')
    create.add_argument('-priority', type=str,
                        choices=[x.name.lower() for x in TaskPriority])

    # update = task_subparser.add_parser('update', help='Update task info',
    #                                    parents=[create])

    show = task_subparser.add_parser('show', help='Show task(s) info')
    show.add_argument('--task_id', type=int,
                      help='Task id', default=-1)

    share_parent = task_subparser.add_parser('share',
                                             help='Share task with user')
    share_parent.add_argument('--task_id', required=True)
    share = share_parent.add_mutually_exclusive_group(required=True)
    share.add_argument('--user_receiver_id', type=int)
    share.add_argument('--user_receiver_email',
                       help='User email to share task with')

    edit = task_subparser.add_parser('edit', help='Edit task with provided id')
    edit.add_argument('--task_id', required=True)
    edit.add_argument('--name')
    edit.add_argument('--description')
    edit.add_argument('--start_date')
    edit.add_argument('--end_date')
    edit.add_argument('--priority',
                      choices=[x.name.lower() for x in TaskPriority])

    # share = task_subparser.add_parser('share', help='Share task with user')
    # share.add_argument('--task_id', required=True)
    # share.add_argument('--user_receiver_id', type=int)
    # share.add_argument('--user_email',
    #                    help='User email to share task with')

    # delete = task_subparser.add_parser('delete', help='Delete task')
    # delete.add_argument('--id', type=int,
    #                     help='Task id')


#  https://habr.com/post/144416/+
# https://stackoverflow.com/questions/43968006/support-for-enum-arguments-in-argparse

def parse_args():
    main_parser = argparse.ArgumentParser(prog='Tracker',
                                          description='CLI for tracker')
    entity_parser = main_parser.add_subparsers(
        dest='entity', help='Actions on selected entities')
    func_task_parser(entity_parser)
    return main_parser


if __name__ == '__main__':
    # AppService.create_user(name='Test2', email='newuser')
    main_parser = parse_args()
    args = main_parser.parse_args()
    service = AppService()
    args.user_id = 1
    commands_handler(service, args)
    print(args)
