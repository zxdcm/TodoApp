from datetime import datetime
import argparse
from lib.models import TaskPriority


def exclude_keys(namespace):
    namespace = vars(namespace)
    keys = ['entity', 'action', 'user_id', 'task_id', 'folder_id']
    return {x: namespace[x] for x in namespace if x not in keys and
            namespace[x]}


def task_parser(sup_parser: argparse):
    task_parser = sup_parser.add_parser('task', help='Manage tasks')

    task_subparser = task_parser.add_subparsers(dest='action', metavar='')

    create = task_subparser.add_parser('create',
                                       help='Create new task')
    create.add_argument('name',
                        help='Task name')
    create.add_argument('-d',
                        '--description',
                        help='Task description')
    create.add_argument('-sd', '--start_date', type=datetime,
                        help='Start date. Current time by default')
    create.add_argument('-ed', '--end_date', type=datetime,
                        help='Eend date')
    create.add_argument('-p', '--parent_task_id', type=int,
                        help='Parent task id')
    create.add_argument('-priority', type=str,
                        choices=[x.name.lower() for x in TaskPriority])

    show = task_subparser.add_parser('show', help='Show task(s) info')
    show.add_argument('-tid', '--task_id', type=int,
                      help='Task id', default=-1)

    share = task_subparser.add_parser('share', help='Share task with user')
    share.add_argument('-tid', '--task_id', type=int,
                       help='Id of task to be shared', required=True)
    share.add_argument('-uid', '--user_receiver_id', type=int,
                       help='User id to share task with', required=True)

    unshare = task_subparser.add_parser(
        'unshare', help='Unshare shared task with user')
    unshare.add_argument('-tid', '--task_id', help='task id', required=True)
    unshare.add_argument('-uid', '--user_receiver_id',
                         help='user id', required=True)

    edit = task_subparser.add_parser('edit', help='Edit task with provided id')
    edit.add_argument('-tid', '--task_id', required=True)
    edit.add_argument('-n', '--name',
                      help='Task name')
    edit.add_argument('-d', '--description',
                      help='Task description')
    edit.add_argument('-sd', '--start_date', type=datetime,
                      help='Start date')
    edit.add_argument('-ed', '--end_date', type=datetime,
                      help='End date')
    edit.add_argument('-p', '--parent_task_id', type=int,
                      help='Parent task id')
    edit.add_argument('-priority', type=str,
                      choices=[x.name.lower() for x in TaskPriority])

    delete = task_subparser.add_parser('delete',
                                       help='Delete task with provided id')
    delete.add_argument('-tid', '--task_id', required=True, type=int)


def folder_parser(sup_parser: argparse):

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
                      help='Folder name')

    delete = folder_subparser.add_parser('delete',
                                         help='Delete folder with provided id')
    delete.add_argument('-fid', '--folder_id', required=True)


def get_args():
    main_parser = argparse.ArgumentParser(prog='Tracker',
                                          description='CLI for tracker',
                                          usage='Tracker')
    entity_parser = main_parser.add_subparsers(
        dest='entity',
        title='Entities',
        description='Select entity', metavar='')
    task_parser(entity_parser)
    folder_parser(entity_parser)
    return main_parser.parse_args()
