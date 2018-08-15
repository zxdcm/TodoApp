from datetime import datetime
import argparse
from lib.models import TaskPriority, TaskStatus, Period


def exclude_keys(namespace):
    namespace = vars(namespace)
    keys = ['entity', 'action', 'user_id', 'task_id', 'folder_id']
    return {x: namespace[x] for x in namespace if x not in keys and
            namespace[x]}


def task_show_parser(show_subparser: argparse):
    task_show = show_subparser.add_subparsers(dest='show_type',
                                              title='Show tasks info',
                                              metavar='')

    task_id = task_show.add_parser('id',
                                   help='Show task by id')
    task_id.add_argument('task_id',
                         help='Task id')

    task_show.add_parser('own',
                         help='Show tasks created by user')

    inner = task_show.add_parser('inner',
                                 help='Show inner tasks by its parent id')
    inner.add_argument('parent_task_id')

    task_show.add_parser('access',
                         help='Show tasks that user can access')

    task_show.add_parser('assigned',
                         help='Show tasks assigned on user')

    task_show.add_parser('archived',
                         help='Show archived tasks')

    task_show.add_parser('repeat',
                         help='Show tasks created by repeat')
    task_show.add_parser('repeatless', help='Show tasks without repeat')


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
                        help='End date')
    create.add_argument('-p', '--parent_task_id', type=int,
                        help='Parent task id')
    create.add_argument('-priority', type=str,
                        choices=[x.name.lower() for x in TaskPriority])

    show = task_subparser.add_parser('show', help='Show tasks')
    task_show_parser(show)

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
    edit.add_argument('-status', type=str,
                      choices=[x.name.lower() for x in TaskStatus])

    share = task_subparser.add_parser('share', help='Share task with user')
    share.add_argument('-tid', '--task_id', type=int,
                       help='Id of task to be shared', required=True)
    share.add_argument('-uid', '--user_receiver_id', type=int,
                       help='User id to share task with', required=True)

    unshare = task_subparser.add_parser(
        'unshare', help='Unshare shared task with user')
    unshare.add_argument('-tid', '--task_id', help='Task id', required=True)
    unshare.add_argument('-uid', '--user_receiver_id',
                         help='user id', required=True)

    assign = task_subparser.add_parser(
        'assign', help='Assign task executor')
    assign.add_argument('-tid', '--task_id', help='Task id', required=True)
    assign.add_argument('-uid', '--assigner_user_id',
                        help='user id', required=True)

    subtask = task_subparser.add_parser('set_subtask',
                                        help='Set task with task_id as the subtask of task with parent_id')
    subtask.add_argument('-tid', '--task_id', required=True, help='Task id')
    subtask.add_argument('-pid', '--parent_task_id', help='Parent task id',
                         required=True)

    archive = task_subparser.add_parser('archive', help='Archive task')
    archive.add_argument('task_id', help='task id')
    archive.add_argument('--archive_subs', action='store_true',
                         help='Archive subtasks')

    done = task_subparser.add_parser('done', help='Done task')
    done.add_argument('task_id', help='task id')
    done.add_argument('--done_subs', action='store_true',
                      help='Done subtasks')

    delete = task_subparser.add_parser('delete',
                                       help='Delete task with provided id')
    delete.add_argument('task_id', type=int)


def folder_show_parser(show_subparser: argparse):
    task_show = show_subparser.add_subparsers(dest='show_type',
                                              title='Show repeat and its info',
                                              metavar='')
    folder_id = task_show.add_parser('id',
                                     help='Show repeat by id')
    folder_id.add_argument('folder_id',
                           help='Folder id')
    folder_id.add_argument('--tasks',
                           action='store_true',
                           help='Show folder tasks')

    folder_all = task_show.add_parser('all',
                                      help='Show all folders')
    folder_all.add_argument('--tasks',
                            action='store_true',
                            help='Show folder_tasks')


def folder_parser(sup_parser: argparse):

    folder_parser = sup_parser.add_parser('folder', help='Manage folders')
    folder_subparser = folder_parser.add_subparsers(dest='action', metavar='')

    create = folder_subparser.add_parser('create', help='Create new folder')
    create.add_argument('name', help='Folder name')

    show = folder_subparser.add_parser('show', help='Show folders  info')
    folder_show_parser(show)

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
    edit.add_argument('folder_id')
    edit.add_argument('name',
                      help='Folder name')

    delete = folder_subparser.add_parser('delete',
                                         help='Delete folder by id')
    delete.add_argument('folder_id')


def repeat_show_parser(sup_parser: argparse):
    repeat_show = sup_parser.add_subparsers(dest='show_type',
                                            title='Show folder and its info',
                                            metavar='')
    repeat_id = repeat_show.add_parser('id',
                                       help='Show folder by id')

    repeat_id.add_argument('repeat_id',
                           help='Repeat id')
    repeat_id.add_argument('--tasks',
                           action='store_true',
                           help='Show repeat. Task and generated tasks')

    repeat_all = repeat_show.add_parser('all',
                                        help='Show all folders')
    repeat_all.add_argument('--tasks',
                            action='store_true',
                            help='Show repeat. Task and generated tasks')


def repeat_parser(sup_parser: argparse):

    repeat_parser = sup_parser.add_parser('repeat',
                                          help='Manage repeat')
    repeat_subparser = repeat_parser.add_subparsers(dest='action',
                                                    metavar='')

    create = repeat_subparser.add_parser('create',
                                         help='Create repeat for existing task')
    create.add_argument('task_id',
                        help='task id')
    create.add_argument('period_amount',
                        help='Period amount')
    create.add_argument('period_type',
                        help='Period type',
                        choices=[x.name.lower() for x in Period])

    create.add_argument('-ra', '--repeat_amount',
                        type=int,
                        help='How much repeat should be executed')
    create.add_argument('-ed', '--end_date',
                        type=datetime,
                        help='Repeat end date.')

    show = repeat_subparser.add_parser('show', help='Show folders  info')
    repeat_show_parser(show)

    edit = repeat_subparser.add_parser('edit',
                                       help='Edit repeat')
    edit.add_argument('repeat_id',
                      help='repeat_id')
    edit.add_argument('-pa', '--period_amount',
                      help='Period amount')
    edit.add_argument('-pt', '--period_type',
                      help='Period type',
                      choices=[x.name.lower() for x in Period])
    edit.add_argument('-ra', '--repeat_amount',
                      type=int,
                      help='How much repeat should be executed')
    edit.add_argument('-ed', '--end_date',
                      type=datetime,
                      help='Repeat end date.')

    delete = repeat_subparser.add_parser('delete',
                                         help='Delete repeat by id')
    delete.add_argument('repeat_id')


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
    repeat_parser(entity_parser)
    return main_parser.parse_args()
