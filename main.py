import argparse
import sys
from lib.services import AppService, Task, TaskPriority, Period
from datetime import datetime


class UserSession:

    def __init__(self):
        pass

    def login(self, email, password):
        pass


def exclude_keys(namespace):
    namespace = vars(namespace)
    keys = ['entity', 'action', 'user_id', 'task_id', 'folder_id']
    return {x: namespace[x] for x in namespace if x not in keys and
            namespace[x]}


def task_handler(service: AppService, namespace, *args, **kwargs):
    if namespace.action == 'create':
        task = service.create_task(user_id=namespace.user_id,
                                   name=namespace.name,
                                   description=namespace.description,
                                   start_date=namespace.start_date,
                                   end_date=namespace.end_date,
                                   parent_task_id=namespace.parent_task_id,
                                   priority=namespace.priority)
        print(task)
    elif namespace.action == 'show':
        if namespace.task_id == -1:
            [print(x) for x in service.get_own_tasks(namespace.user_id)]
        else:
            print(service.get_task_by_id(namespace.user_id,
                                         namespace.task_id))
    elif namespace.action == 'share':
        if namespace.user_receiver_id is None:
            namespace.user_receiver_id = service.get_user_by_email(
                namespace.user_receiver_email).id
        if namespace.share_type == 'read':
            service.share_task_on_read(
                user_owner_id=namespace.user_id,
                task_id=namespace.task_id,
                user_receiver_id=namespace.user_receiver_id)
        else:
            service.share_task_on_write(
                user_owner_id=namespace.user_id,
                task_id=namespace.task_id,
                user_receiver_id=namespace.user_receiver_id
            )
        print(f'Task {namespace.task_id} shared with {namespace.user_receiver_id}')
    elif namespace.action == 'unshare':
        if namespace.share_type == 'read':
            service.unshare_task_on_read(
                user_owner_id=namespace.user_id,
                task_id=namespace.task_id,
                user_receiver_id=namespace.user_receiver_id)
        else:
            service.unshare_task_on_write(
                user_owner_id=namespace.user_id,
                task_id=namespace.task_id,
                user_receiver_id=namespace.user_receiver_id)
        print()
    elif namespace.action == 'edit':
        service.update_task(user_id=namespace.user_id,
                            task_id=namespace.task_id,
                            args=exclude_keys(namespace))


def folder_handler(service: AppService, namespace, args, kwargs):
    if namespace.action == 'create':
        folder = service.create_folder(user_id=namespace.user_id,
                                       name=namespace.name)
    elif namespace.action == 'show':
        if namespace.folder_id == -1:
            [print(x) for x in service.get_all_folders(user_id=namespace.user_id)]
        else:
            folder = service.get_folder_by_id(user_id=namespace.user_id,
                                              folder_id=namespace.folder_id)
            print(f'Folder name: {folder.name}')
            print(f'Folder tasks:')
            for x in folder.tasks:
                print(x)
    elif namespace.action == 'edit':
        service.update_folder(folder_id=namespace.folder_id,
                              user_id=namespace.user_id,
                              args=exclude_keys(namespace))

    elif namespace.action == 'populate':
        folder = service.get_folder_by_id(user_id=namespace.user_id,
                                          folder_id=namespace.folder_id)
        task = service.get_task_by_id(user_id=namespace.user_id,
                                      task_id=namespace.task_id)
        folder.tasks.append(task)
        service.save_updates()

    elif namespace.action == 'unpopulate':
        folder = service.get_folder_by_id(user_id=namespace.user_id,
                                          folder_id=namespace.id)
        task = folder.get_task_by_id(user_id=namespace.user_id,
                                     task_id=namespace.task_id)
        if task in folder.tasks:
            folder.tasks.remove(task)
            print(f'Task {task.id} no longer in {folder.name}')
        else:
            print('Folder doesnt contain task with following id')
        service.save_updates()


def commands_handler(service: AppService, namespace, *args, **kwargs):
    if namespace.entity == 'task':
        task_handler(service, namespace, args, kwargs)

    elif namespace.entity == 'folder':
        folder_handler(service, namespace, args, kwargs)

    elif namespace.entity == 'repeat':
        repeat_handler(service, namespace)


def func_task_parser(sup_parser: argparse):
    task_parser = sup_parser.add_parser('task', help='Manage tasks')

    task_subparser = task_parser.add_subparsers(dest='action', metavar='')
    create = task_subparser.add_parser('create',
                                       help='Create new task')
    create.add_argument('name',
                        help='Task name')
    create.add_argument('-d', '--description',
                        help='Task description')
    create.add_argument('-sd', '--start_date', type=datetime,
                        help='Set start date. Current time by default')
    create.add_argument('-ed', '--end_date', type=datetime,
                        help='Set end date')
    create.add_argument('-p', '--parent_task_id', type=int,
                        help='Parent task id')
    create.add_argument('-priority', type=str,
                        choices=[x.name.lower() for x in TaskPriority])

    show = task_subparser.add_parser('show', help='Show task(s) info')
    show.add_argument('-tid', '--task_id', type=int,
                      help='Task id', default=-1)

    share_parent = task_subparser.add_parser('share',
                                             help='Share task with user')
    share_parent.add_argument('--tid', '--task_id', help='task id',
                              required=True)
    share = share_parent.add_mutually_exclusive_group(required=True)
    share.add_argument('-uid', '--user_receiver_id', type=int,
                       help='User id to share task with')
    share.add_argument('--uemail', '--user_receiver_email',
                       help='User email to share task with')
    share.add_argument('--st', '--share_type', help='Share type',
                       default='read', choices=['read', 'write'])

    unshare = task_subparser.add_parser(
        'unshare', help='Unshare shared task with user')
    unshare.add_argument('-tid', '--task_id', help='task id', required=True)
    unshare.add_argument('-uid', '--user_id', help='user id', required=True)
    unshare.add_argument('-st', '--share_type', '--share_type',
                         help='Share type',
                         default='read', choices=['read', 'write'])

    edit = task_subparser.add_parser('edit', help='Edit task with provided id')
    edit.add_argument('-tid', '--task_id', required=True)
    edit.add_argument('--name',
                      help='Task name')
    edit.add_argument('-d', '--description',
                      help='Task description')
    edit.add_argument('-sd', '--start_date', type=datetime,
                      help='Set start date')
    edit.add_argument('-ed', '--end_date', type=datetime,
                      help='Set end date')
    edit.add_argument('-p', '--parent_task_id', type=int,
                      help='Parent task id')
    edit.add_argument('-priority', type=str,
                      choices=[x.name.lower() for x in TaskPriority])

    delete = task_subparser.add_parser('delete',
                                       help='Delete task with provided id')
    delete.add_argument('-tid', '--task_id', required=True, type=int)
    # share = task_subparser.add_parser('share', help='Share task with user')
    # share.add_argument('--task_id', required=True)
    # share.add_argument('--user_receiver_id', type=int)
    # share.add_argument('--user_email',
    #                    help='User email to share task with')

    # delete = task_subparser.add_parser('delete', help='Delete task')
    # delete.add_argument('--id', type=int,
    #                     help='Task id')


def func_folder_parser(sup_parser: argparse):
    folder_parser = sup_parser.add_parser('folder', help='Manage folders')
    folder_subparser = folder_parser.add_subparsers(dest='action', metavar='')
    create = folder_subparser.add_parser('create', help='Create new folder')
    create.add_argument('name', help='Folder name')

    show = folder_subparser.add_parser('show', help='Show folder(s) info')
    show.add_argument('-fid', '--folder_id', type=int,
                      help='Folder id', default=-1)

    populate = folder_subparser.add_parser(
        'populate', help='Populate folder with provided task')
    populate.add_argument('-fid', '--folder_id', required=True)
    populate.add_argument('-tid', '--task_id', required=True)

    unpopulate = folder_subparser.add_parser(
        'unpopulate', help='delete task from folder')

    unpopulate.add_argument('-fid', '--folder_id', required=True)
    unpopulate.add_argument('-tid', '--task_id', required=True)

    edit = folder_subparser.add_parser(
        'edit', help='Edit folder with provided id')
    edit.add_argument('-fid', '--folder_id', required=True)
    edit.add_argument('-n', '--name',
                      help='Task name')

    delete = folder_subparser.add_parser('delete',
                                         help='Delete folder with provided id')
    delete.add_argument('-fid', '--folder_id', required=True)

#  https://habr.com/post/144416/+
# https://stackoverflow.com/questions/43968006/support-for-enum-arguments-in-argparse


def parse_args():
    main_parser = argparse.ArgumentParser(prog='Tracker',
                                          description='CLI for tracker',
                                          usage='Tracker')
    entity_parser = main_parser.add_subparsers(
        dest='entity',
        title='Entities',
        description='Select entity', metavar='')
    func_task_parser(entity_parser)
    func_folder_parser(entity_parser)
    return main_parser


if __name__ == '__main__':
    # AppService.create_user(name='Test2', email='newuser2')
    # sys.exit()
    main_parser = parse_args()
    service = AppService()
    # task = service.get_frozen_task_by_id(user_id=1, task_id=1)
    # try:
    #     task.name = 'Test'
    # except TypeError:
    #     print('bingo')
    # task = service.create_task(user_id=1, name='test', priority='Low')
    # [print(x) for x in service.get_own_tasks(1)]
    #repeat = service.create_repeat(user_id=2, task_id=1, period_amount=1)
    # print(repeat)
    repeat = service.get_repeat_by_id(user_id=1, repeat_id=1)
    [print(x) for x in service.get_all_repeats(user_id=1)]
    # service.share_task_on_write(user_owner_id=1, user_receiver_id=2, task_id=1)
    #repeat = service.create_repeat(user_id=1, task_id=2, period_amount=1)

    # service.save()
#    service.get_observable_tasks(1)
#    service.user_can_read_task(user_id=1, task_id=5)
    # args = main_parser.parse_args()
    # args.user_id = 1
    # commands_handler(service, args)
    # print(args)
