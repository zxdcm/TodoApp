from datetime import datetime
from dateutil.parser import parse
import argparse
from lib.models import TaskPriority, TaskStatus, Period
from os import sys


class DefaultHelpParser(argparse.ArgumentParser):
    def error(self, message):
        print('error: %s\n' % message, file=sys.stderr)
        self.print_help()
        sys.exit(2)


def valid_date(text):
    try:
        return parse(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Invalid date format. Supported format:  ')


def task_show_parser(show_subparser: argparse):
    task_show = show_subparser.add_subparsers(dest='show_type',
                                              title='Show tasks info',
                                              metavar='',
                                              description='Commands to show tasks')

    task_id = task_show.add_parser('id',
                                   help='Show task by id')
    task_id.add_argument('task_id',
                         help='Task id',
                         type=int)

    task_show.add_parser('own',
                         help='Show tasks created by user')

    subtasks = task_show.add_parser('subtasks',
                                    help='Show subtasks by task id')
    subtasks.add_argument('task_id',
                          type=int)

    task_show.add_parser('all',
                         help='Show all tasks user can access')

    task_show.add_parser('assigned',
                         help='Show tasks assigned on user')

    task_show.add_parser('archived',
                         help='Show archived tasks')

    task_show.add_parser('todo',
                         help='Show todo tasks')

    task_show.add_parser('done',
                         help='Show done tasks')

    task_show.add_parser('planless',
                         help='Show tasks without plan')


def task_parser(sup_parser: argparse):
    task_parser = sup_parser.add_parser('task',
                                        help='Manage tasks')
    task_subparser = task_parser.add_subparsers(dest='action',
                                                metavar='',
                                                description='Commands to work with tasks')

    create = task_subparser.add_parser('create',
                                       help='Create new task')
    create.add_argument('name',
                        help='Task name')
    create.add_argument('-d',
                        '--description',
                        help='Task description')
    create.add_argument('-s', '--start_date',
                        type=valid_date,
                        help='Start date (current time by default)',
                        default=datetime.now())
    create.add_argument('-e',
                        '--end_date',
                        type=valid_date,
                        help='End date')
    create.add_argument('-p',
                        '--parent_task_id',
                        type=int,
                        help='Parent task id')
    create.add_argument('--priority',
                        type=str,
                        choices=[x.name.lower() for x in TaskPriority])
    create.add_argument('--status',
                        type=str,
                        choices=[x.name.lower() for x in TaskStatus])

    show = task_subparser.add_parser('show',
                                     help='Show tasks')
    task_show_parser(show)

    edit = task_subparser.add_parser('edit',
                                     help='Edit task with provided id')
    edit.add_argument('-tid',
                      '--task_id',
                      required=True, type=int)
    edit.add_argument('-n',
                      '--name',
                      help='Task name')
    edit.add_argument('-d',
                      '--description',
                      help='Task description')
    edit.add_argument('-s', '--start_date',
                      type=valid_date,
                      help='Start date')
    edit.add_argument('-e', '--end_date',
                      type=valid_date,
                      help='End date')
    edit.add_argument('--priority',
                      type=str,
                      choices=[x.name.lower() for x in TaskPriority])
    edit.add_argument('--status',
                      type=str,
                      choices=['todo', 'inwork'])

    share = task_subparser.add_parser('share',
                                      help='Share task with user')
    share.add_argument('-tid',
                       '--task_id',
                       type=int,
                       help='Id of task to be shared',
                       required=True)
    share.add_argument('-ur',
                       '--user_receiver',
                       type=str,
                       help='User name to share task with',
                       required=True)

    unshare = task_subparser.add_parser(
        'unshare', help='Unshare shared task with user')
    unshare.add_argument('-tid',
                         '--task_id',
                         help='Task id',
                         required=True,
                         type=int)
    unshare.add_argument('-urn',
                         '--user_receiver',
                         help='User name to unshare task with',
                         required=True,
                         type=str)

    assign = task_subparser.add_parser(
        'assign', help='Assign task executor')
    assign.add_argument('-tid',
                        '--task_id',
                        help='Task id',
                        required=True,
                        type=int)
    assign.add_argument('-urn',
                        '--user_receiver',
                        help='User name to assign task',
                        required=True,
                        type=str)

    subtask = task_subparser.add_parser('add_subtask',
                                        help='Set task with task_id as the subtask of task with parent_id')
    subtask.add_argument('-tid',
                         '--task_id',
                         required=True,
                         help='Task id',
                         type=int)
    subtask.add_argument('-pid',
                         '--parent_task_id',
                         help='Parent task id',
                         required=True,
                         type=int)

    subtask = task_subparser.add_parser('rm_subtask',
                                        help='Remove relation between task and parent task')
    subtask.add_argument('-tid',
                         '--task_id',
                         required=True,
                         help='Task id',
                         type=int)

    archive = task_subparser.add_parser('archive',
                                        help='Archive task')
    archive.add_argument('--subtasks',
                         action='store_true',
                         help='Archive subtasks too')

    archive.add_argument('task_id',
                         help='task id',
                         type=int)
    done = task_subparser.add_parser('done',
                                     help='Done task')
    done.add_argument('task_id',
                      help='task id',
                      type=int)

    delete = task_subparser.add_parser('delete',
                                       help='Delete task with provided id')
    delete.add_argument('task_id',
                        type=int)


def folder_show_parser(show_subparser: argparse):
    task_show = show_subparser.add_subparsers(dest='show_type',
                                              title='Show folders and its info',
                                              metavar='',
                                              description='Commands to show folders')
    folder_id = task_show.add_parser('id',
                                     help='Show folder by id')
    folder_id.add_argument('folder_id',
                           help='Folder id', type=int)
    folder_id.add_argument('--tasks',
                           action='store_true',
                           help='Show folder tasks')

    folder_all = task_show.add_parser('all',
                                      help='Show all folders')
    folder_all.add_argument('--tasks',
                            action='store_true',
                            help='Show folder_tasks')


def folder_parser(sup_parser: argparse):

    folder_parser = sup_parser.add_parser('folder',
                                          help='Manage folders')
    folder_subparser = folder_parser.add_subparsers(dest='action',
                                                    metavar='',
                                                    description='Commands to work with folders')

    create = folder_subparser.add_parser('create',
                                         help='Create new folder')
    create.add_argument('name',
                        help='Folder name')

    show = folder_subparser.add_parser('show',
                                       help='Show folders  info')
    folder_show_parser(show)

    populate = folder_subparser.add_parser(
        'populate', help='Populate folder with provided task')
    populate.add_argument('-fid',
                          '--folder_id',
                          required=True,
                          type=int)
    populate.add_argument('-tid',
                          '--task_id',
                          required=True,
                          type=int)

    unpopulate = folder_subparser.add_parser(
        'unpopulate',
        help='delete task from folder')
    unpopulate.add_argument('-fid',
                            '--folder_id',
                            required=True,
                            type=int)
    unpopulate.add_argument('-tid',
                            '--task_id',
                            required=True,
                            type=int)

    edit = folder_subparser.add_parser(
        'edit',
        help='Edit folder by id')
    edit.add_argument('folder_id',
                      type=int)
    edit.add_argument('name',
                      help='Folder name')

    delete = folder_subparser.add_parser('delete',
                                         help='Delete folder by id')
    delete.add_argument('folder_id',
                        type=int)


def plan_show_parser(sup_parser: argparse):
    plan_show = sup_parser.add_subparsers(dest='show_type',
                                          title='Show plan and its info',
                                          metavar='',
                                          description='Commands to show plans')
    plan_id = plan_show.add_parser('id',
                                   help='Show plan by id')

    plan_id.add_argument('plan_id',
                         help='Plan id',
                         type=int)
    plan_id.add_argument('--tasks',
                         action='store_true',
                         help='Show plan. Task and generated tasks')

    plan_all = plan_show.add_parser('all',
                                    help='Show all plans')
    plan_all.add_argument('--tasks',
                          action='store_true',
                          help='Show plan. Task and generated tasks')


def plan_parser(sup_parser: argparse):

    plan_parser = sup_parser.add_parser('plan',
                                        help='Manage plan')
    plan_subparser = plan_parser.add_subparsers(dest='action',
                                                metavar='',
                                                description='Commands to work with plans')

    create = plan_subparser.add_parser('create',
                                       help='Create plan for existing task')
    create.add_argument('task_id',
                        help='task id',
                        type=int)
    create.add_argument('period_amount',
                        help='Period amount',
                        type=int)
    create.add_argument('period',
                        help='Period type',
                        choices=[x.name.lower() for x in Period])

    create.add_argument('-r', '--plan_amount',
                        type=int,
                        help='How much times plan should be executed')
    create.add_argument('-e', '--end_date',
                        type=valid_date,
                        help='Plan end date.')

    show = plan_subparser.add_parser('show', help='Show plans info')
    plan_show_parser(show)

    edit = plan_subparser.add_parser('edit',
                                     help='Edit plan')
    edit.add_argument('plan_id',
                      help='plan_id',
                      type=int)
    edit.add_argument('-p', '--period_amount',
                      help='Period amount',
                      type=int)
    edit.add_argument('-t', '--period',
                      help='Period type',
                      choices=[x.name.lower() for x in Period])
    edit.add_argument('-r', '--plan_amount',
                      type=int,
                      help='How much plan should be executed')
    edit.add_argument('-e', '--end_date',
                      type=valid_date,
                      help='Plan end date.')

    delete = plan_subparser.add_parser('delete',
                                       help='Delete plan by id')
    delete.add_argument('plan_id', type=int)


def user_parser(sup_parser: argparse):
    user_parser = sup_parser.add_parser('user',
                                        help='Manage users')
    user_subparser = user_parser.add_subparsers(dest='action',
                                                metavar='',
                                                description='Commands to work with user')

    create = user_subparser.add_parser('create', help='Register new user')
    create.add_argument('username')
    login = user_subparser.add_parser('login', help='Auth by username')
    login.add_argument('username')
    user_subparser.add_parser('logout', help='Logout user')
    user_subparser.add_parser('current', help='Show current user')
    user_subparser.add_parser('all', help='Show all users in app')


def get_args():
    main_parser = DefaultHelpParser(prog='todo',
                                    description='todo tracker',
                                    usage='todo <entity> [<args>]')
    entity_parser = main_parser.add_subparsers(
        dest='entity',
        title='Entities',
        description='Select entity you want to work with', metavar='')

    task_parser(entity_parser)
    folder_parser(entity_parser)
    plan_parser(entity_parser)
    user_parser(entity_parser)
    return main_parser.parse_args()
