from lib.services import (AppService,
                          TaskStatus,
                          TaskPriority)

from lib.exceptions import LibError, LibWarning
from client.user_service import UserService
from os import sys
import textwrap


def error_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except LibError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except LibWarning as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except KeyError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        except Exception:
            print('Unhandled inner exception. Watch out log file',
                  file=sys.stderr)
            sys.exit(1)
    return wrapper


def print_collection(collection, mes1=None, mes2=None):
    print()
    if collection:
        print(mes1)
        for item in collection:
            print(item)
    else:
        print(mes2, file=sys.stderr)
        sys.exit(1)


def print_task_with_subtask(service: AppService,
                            user,
                            task,
                            indent=4,
                            level=0):
    print(textwrap.indent(str(task), ' ' * indent * level))
    for task in service.get_subtasks(user=user, task_id=task.id):
        print_task_with_subtask(service, user, task, indent, level+1)


def task_show_handler(service: AppService, namespace):
    if namespace.show_type == 'id':
        task = service.get_task(user=namespace.user,
                                task_id=namespace.task_id)
        print(task)

    elif namespace.show_type == 'own':
        own_tasks = service.get_own_tasks(user=namespace.user)
        print_collection(own_tasks,
                         mes1='Your own tasks:',
                         mes2='You dont have any tasks')

    elif namespace.show_type == 'subtasks':
        task = service.get_task(namespace.user, task_id=namespace.task_id)
        subtasks = service.get_subtasks(user=namespace.user,
                                        task_id=namespace.task_id)
        if subtasks:
            print_task_with_subtask(service, namespace.user, task)
        else:
            print('Task dont have any subtasks')

    elif namespace.show_type == 'all':
        available_tasks = service.get_available_tasks(
            user=namespace.user)
        print_collection(available_tasks,
                         mes1='Available tasks:',
                         mes2='You dont have any tasks')

    elif namespace.show_type == 'assigned':
        assigned_tasks = service.get_user_assigned_tasks(user=namespace.user)
        print_collection(assigned_tasks,
                         mes1='Assigned tasks:',
                         mes2='You dont have assigned tasks')

    elif namespace.show_type == 'todo':
        todo_tasks = service.get_filtered_tasks(user=namespace.user, status=TaskStatus.TODO)
        print_collection(todo_tasks,
                         mes1='Todo tasks:',
                         mes2='You dont have todo tasks')

    elif namespace.show_type == 'inwork':
        inwork_tasks = service.get_filtered_tasks(user=namespace.user, status=TaskStatus.INWORK)
        print_collection(inwork_tasks,
                         mes1='Inwork tasks:',
                         mes2='You dont have any inwork tasks')

    elif namespace.show_type == 'done':
        done_tasks = service.get_filtered_tasks(user=namespace.user, status=TaskStatus.DONE)
        print_collection(done_tasks,
                         mes1='Done tasks:',
                         mes2='You dont have any done tasks')

    elif namespace.show_type == 'archived':
        archived_tasks = service.get_filtered_tasks(user=namespace.user, status=TaskStatus.ARCHIVED)
        print_collection(archived_tasks,
                         mes1='Archived tasks:',
                         mes2='You dont have any archived tasks')

    elif namespace.show_type == 'planless':
        planless = [task for task in service.get_available_tasks(user=namespace.user)
                    if task.plan is None]
        print_collection(planless,
                         mes1='Tasks without plan:',
                         mes2='You dont have any tasks without a plan')


def event_converter(arg):
    if arg == 'yes':
        return True
    return False


def task_handler(service: AppService, namespace):
    if namespace.action == 'create':
        event = event_converter(namespace.event)
        task = service.create_task(user=namespace.user,
                                   name=namespace.name,
                                   description=namespace.description,
                                   start_date=namespace.start_date,
                                   end_date=namespace.end_date,
                                   parent_task_id=namespace.parent_task_id,
                                   priority=namespace.priority,
                                   event=event,
                                   status=namespace.status)
        print('Created task:')
        print(task)

    elif namespace.action == 'show':
        task_show_handler(service, namespace)

    elif namespace.action == 'edit':
        event = event_converter(namespace.event)
        task = service.update_task(user=namespace.user,
                                   task_id=namespace.task_id,
                                   name=namespace.name,
                                   description=namespace.description,
                                   status=namespace.status,
                                   priority=namespace.priority,
                                   start_date=namespace.start_date,
                                   end_date=namespace.end_date,
                                   event=event)
        print('Updated task:')
        print(task)

    elif namespace.action == 'share':
        service.share_task(user=namespace.user,
                           user_receiver=namespace.user_receiver,
                           task_id=namespace.task_id)
        print(f'Task(ID={namespace.task_id}) shared with user({namespace.user_receiver})')

    elif namespace.action == 'unshare':
        service.unshare_task(user=namespace.user,
                             user_receiver=namespace.user_receiver,
                             task_id=namespace.task_id)

        print(f'Task(ID={namespace.task_id}) unshared with user({namespace.user_receiver})')

    elif namespace.action == 'assign':
        service.assign_user(user=namespace.user,
                            task_id=namespace.task_id,
                            user_receiver=namespace.user_receiver)
        print(f'User({namespace.user_receiver}) assigned as task(ID={namespace.task_id}) executor')

    elif namespace.action == 'add_subtask':
        service.add_subtask(user=namespace.user,
                            task_id=namespace.task_id,
                            parent_task_id=namespace.parent_task_id)
        print(
            f'Subtask(ID={namespace.task_id}) set as parent task of task(ID={namespace.parent_task_id})')

    elif namespace.action == 'rm_subtask':
        service.rm_subtask(user=namespace.user,
                           task_id=namespace.task_id)
        print(
            f'Subtask(ID={namespace.task_id}) is detached from parent task now')

    elif namespace.action == 'done':
        task = service.get_task(user=namespace.user,
                                task_id=namespace.task_id)
        service.change_task_status(user=namespace.user,
                                   task_id=namespace.task_id,
                                   status='done')
        print(f'Task(ID={namespace.task_id}) and its subtasks successfully done')

    elif namespace.action == 'archive':
        service.change_task_status(user=namespace.user,
                                   task_id=namespace.task_id,
                                   status='archived',
                                   apply_on_subtasks=namespace.subtasks)
        print(f'Task(ID={namespace.task_id}) has been archived')

    elif namespace.action == 'delete':
        service.delete_task(user=namespace.user,
                            task_id=namespace.task_id)
        print(f'Task(ID={namespace.task_id}) has been deleted')

    elif namespace.action == 'search':
        tasks = service.get_tasks_by_name(user=namespace.user,
                                          name=namespace.name)
        if tasks:
            for task in tasks:
                print(task)
        else:
            print('Task(s) not found', file=sys.stderr)

    elif namespace.action == 'filter':
        if not any([namespace.name, namespace.start_date, namespace.end_date,
                    namespace.parent_task_id, namespace.priority, namespace.status]):
            print('You didnt specified filter arguments', file=sys.stderr)
            sys.exit(1)
        tasks = service.get_filtered_tasks(user=namespace.user,
                                           name=namespace.name,
                                           start_date=namespace.start_date,
                                           end_date=namespace.end_date,
                                           parent_task_id=namespace.parent_task_id,
                                           priority=namespace.priority,
                                           status=namespace.status)
        if tasks:
            for task in tasks:
                print(task)
        else:
            print('Task(s) not found', file=sys.stderr)


def folder_show_handler(service: AppService, namespace):

    if namespace.show_type == 'id':
        folder = service.get_folder(user=namespace.user,
                                    folder_id=namespace.folder_id)
        print(folder)
        if folder and namespace.tasks:
            print_collection(folder.tasks, mes1='Folder tasks:',
                             mes2='Folder is empty')

    elif namespace.show_type == 'all':
        folders = service.get_all_folders(user=namespace.user)
        if folders and namespace.tasks:
            for folder in folders:
                print(folder)
                print_collection(folder.tasks, mes1='Folder tasks:',
                                 mes2='Folder is empty')
        else:
            print_collection(folders, mes1='Your folders:',
                             mes2='You dont have folders')


def folder_handler(service: AppService, namespace):
    if namespace.action == 'create':
        folder = service.create_folder(user=namespace.user,
                                       name=namespace.name)
        print('Created folder:')
        print(folder)

    elif namespace.action == 'show':
        folder_show_handler(service, namespace)

    elif namespace.action == 'edit':
        if namespace.name:
            folder = service.update_folder(folder_id=namespace.folder_id,
                                           user=namespace.user,
                                           name=namespace.name)
            print(f'Folder has been updated. New folder name = {folder.name}')
        else:
            print('Nothing to update')

    elif namespace.action == 'populate':

        service.populate_folder(user=namespace.user,
                                folder_id=namespace.folder_id,
                                task_id=namespace.task_id)
        print(
            f'Folder with ID={namespace.folder_id} has been populated with task ID={namespace.task_id}')

    elif namespace.action == 'unpopulate':

        service.unpopulate_folder(user=namespace.user,
                                  folder_id=namespace.folder_id,
                                  task_id=namespace.task_id)
        print(f'Task(ID={namespace.task_id}) no longer in this folder')

    elif namespace.action == 'delete':
        service.delete_folder(user=namespace.user,
                              folder_id=namespace.folder_id)
        print(f'Folder(ID={namespace.folder_id}) has been deleted')


def print_plan(plan, gen_tasks):
    print(plan)
    if gen_tasks:
        print(f'Plan task:')
        print(plan.task)
        print_collection(gen_tasks, mes1='Created by plan tasks:',
                         mes2='There are no tasks created by plan')


def plan_show_handlers(service: AppService, namespace):
    if namespace.show_type == 'id':
        plan = service.get_plan(user=namespace.user,
                                plan_id=namespace.plan_id)
        tasks = None
        if namespace.tasks:
            tasks = service.get_generated_tasks_by_plan(user=namespace.user,
                                                        plan_id=plan.id)
        print_plan(plan, tasks)

    elif namespace.show_type == 'all':
        plans = service.get_all_plans(user=namespace.user)
        if not plans:
            print('You dont have plans')
            sys.exit(1)
        if namespace.tasks:
            for plan in plans:
                tasks = service.get_generated_tasks_by_plan(user=namespace.user,
                                                            plan_id=plan.id)
                print_plan(plan, tasks)
        else:
            for plan in plans:
                print(plan)


def plan_handler(service: AppService, namespace):
    if namespace.action == 'create':

        plan = service.create_plan(user=namespace.user,
                                   task_id=namespace.task_id,
                                   period_amount=namespace.period_amount,
                                   period=namespace.period,
                                   repetitions_amount=namespace.plan_amount,
                                   start_date=namespace.start_date,
                                   end_date=namespace.end_date)
        print('Created plan:')
        print(plan)

    elif namespace.action == 'show':

        plan_show_handlers(service, namespace)

    elif namespace.action == 'edit':

        plan = service.update_plan(user=namespace.user,
                                   plan_id=namespace.plan_id,
                                   period_amount=namespace.period_amount,
                                   period=namespace.period,
                                   repetitions_amount=namespace.plan_amount,
                                   end_date=namespace.end_date)
        print('Updated plan:')
        print(plan)

    elif namespace.action == 'delete':
        service.delete_plan(user=namespace.user,
                            plan_id=namespace.plan_id)
        print(f'Plan(ID={namespace.plan_id}) has been deleted')


def reminder_show_handler(service, namespace):
    if namespace.show_type == 'id':
        reminder = service.get_reminder(user=namespace.user,
                                        reminder_id=namespace.reminder_id)
        print(reminder)
        if namespace.task:
            print()
            print(reminder.task)

    elif namespace.show_type == 'all':
        reminders = service.get_all_reminders(user=namespace.user)
        if not reminders:
            print('You dont have any reminders')
            sys.exit(1)
        if namespace.tasks:
            for reminder in reminders:
                print(reminder, end='\n\n')
                print(reminder.task)
        else:
            for reminder in reminders:
                print(reminder)


def reminder_handler(service: AppService, namespace):
    if namespace.action == 'create':
        reminder = service.create_reminder(user=namespace.user,
                                           task_id=namespace.task_id,
                                           date=namespace.date)
        print('Created reminder:')
        print(reminder)

    elif namespace.action == 'show':

        reminder_show_handler(service, namespace)

    elif namespace.action == 'edit':
        reminder = service.update_reminder(user=namespace.user,
                                           reminder_id=namespace.reminder_id,
                                           date=namespace.date)
        print('Updated reminder:')
        print(reminder)

    elif namespace.action == 'delete':
        service.delete_reminder(user=namespace.user,
                                reminder_id=namespace.reminder_id)
        print(f'Reminder(ID={namespace.reminder_id}) has been deleted')


def users_handler(service: AppService, namespace, user_serv: UserService):

    if namespace.action == 'create':

        user = user_serv.create_user(namespace.username)
        if user:
            user_serv.login_user(namespace.username)
            print(f'User {namespace.username} registered')
        else:
            print(f'Error. User {namespace.username} already exists',
                  file=sys.stderr)

    elif namespace.action == 'login':

        if user_serv.login_user(namespace.username):
            print(f'User {namespace.username} logged in')
        else:
            print(f'User {namespace.username} doesnt exist', file=sys.stderr)

    elif namespace.action == 'logout':

        user_serv.logout_user()
        print('User logged out')

    elif namespace.action == 'current':

        user = user_serv.get_current_user()
        if user:
            print(f'Current user: {user}')
        else:
            print('You should login first', file=sys.stderr)

    elif namespace.action == 'all':

        user_list = user_serv.get_all_users()
        if user_list:
            print('Users:')
            [print(x) for x in user_list]
        else:
            print('App dont have any users', file=sys.stderr)


def ensure_user_exist(user_serv, username):
    user = user_serv.get_user(username)
    if user is None:
        print(f'User {username} not found.', file=sys.stderr)
        sys.exit(1)


def check_auth(user_serv):
    user = user_serv.get_current_user()
    if user:
        return user.username
    print('You have to login to perform this action',
          file=sys.stderr)
    sys.exit(1)


# @error_catcher
def commands_handler(service: AppService, namespace,
                     user_serv: UserService):

    if namespace.entity == 'user':
        users_handler(service, namespace, user_serv)

    elif namespace.entity == 'task':
        namespace.user = check_auth(user_serv)
        if hasattr(namespace, 'user_receiver'):
            ensure_user_exist(user_serv, namespace.user_receiver)
        task_handler(service, namespace)

    elif namespace.entity == 'folder':
        namespace.user = check_auth(user_serv)
        folder_handler(service, namespace)

    elif namespace.entity == 'plan':
        namespace.user = check_auth(user_serv)
        plan_handler(service, namespace)

    elif namespace.entity == 'reminder':
        namespace.user = check_auth(user_serv)
        reminder_handler(service, namespace)
