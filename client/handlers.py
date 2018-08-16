from lib.services import AppService, TaskStatus, TaskPriority
from client.parsers import exclude_keys
from lib.exceptions import BaseLibError


def error_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except BaseLibError as e:
            print(str(e))
        except Exception:
            print("Unhandled exception")
    return wrapper


def print_collection(collection, mes1=None, mes2=None):
    print()
    if collection:
        print(mes1)
        for item in collection:
            print(item)
    else:
        print(mes2)


def task_show_handler(service: AppService, namespace):
    if namespace.show_type == 'id':
        task = service.get_task_by_id(user_id=namespace.user_id,
                                      task_id=namespace.task_id)
        print(task)

    elif namespace.show_type == 'own':
        own_tasks = service.get_own_tasks(user_id=namespace.user_id)
        print_collection(own_tasks,
                         mes1='Your own tasks:',
                         mes2='You dont have any tasks')

    elif namespace.show_type == 'subtasks':
        subtasks = service.get_subtasks(user_id=namespace.user_id,
                                        task_id=namespace.task_id)
        print_collection(subtasks,
                         mes1='Task subtasks:',
                         mes2='Task dont have any subtasks')

    elif namespace.show_type == 'all':
        available_tasks = service.get_available_tasks(
            user_id=namespace.user_id)
        print_collection(available_tasks,
                         mes1='Accessible tasks:',
                         mes2='You dont have any tasks')

    elif namespace.show_type == 'assigned':
        assigned_tasks = service.get_user_assigned_tasks(user_id=namespace.user_id)
        print_collection(assigned_tasks,
                         mes1='Assigned tasks:',
                         mes2='You dont have assigned tasks')

    elif namespace.show_type == 'plan':
        generated_tasks = service.get_generated_tasks(
            user_id=namespace.user_id)
        print_collection(generated_tasks,
                         mes1='Tasks created by plan:',
                         mes2='You dont any created tasks by plan')

    elif namespace.show_type == 'planless':
        planless = [task for task in service.get_available_tasks(user_id=namespace.user_id)
                    if task.plan is None]
        print_collection(planless,
                         mes1='Tasks created by plan:',
                         mes2='You dont any created tasks by plan')


def task_handler(service: AppService, namespace):
    if namespace.action == 'create':
        task = service.create_task(user_id=namespace.user_id,
                                   name=namespace.name,
                                   description=namespace.description,
                                   start_date=namespace.start_date,
                                   end_date=namespace.end_date,
                                   parent_task_id=namespace.parent_task_id,
                                   priority=namespace.priority,
                                   status=namespace.status)
        print('Created task:')
        print(task)

    elif namespace.action == 'show':
        task_show_handler(service, namespace)

    elif namespace.action == 'edit':
        args = exclude_keys(namespace)
        if not args:
            print('Nothing to update.')
        else:

            task = service.update_task(user_id=namespace.user_id,
                                       task_id=namespace.task_id,
                                       name=namespace.name,
                                       description=namespace.description,
                                       status=namespace.status,
                                       priority=namespace.priority,
                                       start_date=namespace.start_date,
                                       end_date=namespace.end_date,
                                       parent_task_id=namespace.parent_task_id)
            print('Updated task:', task)

    elif namespace.action == 'share':
        service.share_task(user_id=namespace.user_id,
                           user_receiver_id=namespace.user_receiver_id,
                           task_id=namespace.task_id)
        print(f'Task(ID={namespace.task_id}) shared with user(ID={namespace.user_receiver_id})')

    elif namespace.action == 'unshare':
        service.unshare_task(user_id=namespace.user_id,
                             user_receiver_id=namespace.user_receiver_id,
                             task_id=namespace.task_id)

        print(f'Task(ID={namespace.task_id}) unshared with user(ID={namespace.user_receiver_id})')

    elif namespace.action == 'assign':
        service.assign_user(user_id=namespace.user_id,
                            task_id=namespace.task_id,
                            user_receiver_id=namespace.user_receiver_id)
        print(f'User(ID={namespace.user_receiver_id}) assigned as task(ID={namespace.task_id}) executor')

    elif namespace.action == 'set_subtask':
        service.add_subtask(user_id=namespace.user_id,
                            task_id=namespace.parent_task_id,
                            subtask_id=namespace.task_id)
        print(f'Task(ID={namespace.task_id}) set as parent task of task(ID={namespace.subtask_id})')

    elif namespace.action == 'done':
        task = service.get_task_by_id(user_id=namespace.user_id,
                                      task_id=namespace.task_id)

        if task.status == TaskStatus.DONE:
            print('Task already done')
            return

        service.change_task_status(user_id=namespace.user_id,
                                   task_id=namespace.task_id,
                                   status='done',
                                   apply_on_subtasks=namespace.done_subs)

        print(f'Task(ID={namespace.task_id}) successfully done')

        if namespace.done_subs:
            print('Subtasks were done too')

    elif namespace.action == 'archive':
        if task.status == TaskStatus.ARCHIVED:
            print('Task already archived')
            return

        service.change_task_status(user_id=namespace.user_id,
                                   task_id=namespace.task_id,
                                   status='archived',
                                   apply_on_subtasks=namespace.archive_subs)
        print(f'Task(ID={namespace.task_id}) has been archived')

        if namespace.archive_subs:
            print('Subtasks were archived too')

    elif namespace.action == 'delete':
        service.delete_task(user_id=namespace.user_id,
                            task_id=namespace.task_id)
        print(f'Task(ID={namespace.task_id}) has been deleted')


def folder_show_handler(service: AppService, namespace):

    if namespace.show_type == 'id':
        folder = service.get_folder_by_id(user_id=namespace.user_id,
                                          folder_id=namespace.folder_id)
        print(folder)
        if folder and namespace.tasks:
            print(f'Your folder:{folder}')
            print_collection(folder.tasks, mes1='Folder tasks:',
                             mes2='Folder is empty')

    elif namespace.show_type == 'all':
        folders = service.get_all_folders(user_id=namespace.user_id)
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
        folder = service.create_folder(user_id=namespace.user_id,
                                       name=namespace.name)
        print('Created folder:')
        print(folder)

    elif namespace.action == 'show':
        folder_show_handler(service, namespace)

    elif namespace.action == 'edit':
        if namespace.name:
            folder = service.update_folder(folder_id=namespace.folder_id,
                                           user_id=namespace.user_id,
                                           name=namespace.name)
            print(f'Folder has been updated. New folder name = {folder}')
        else:
            print('Nothing to update')

    elif namespace.action == 'populate':

        service.populate_folder(user_id=namespace.user_id,
                                folder_id=namespace.folder_id,
                                task_id=namespace.task_id)
        print(
            f'Folder with ID={namespace.folder_id} has been populated with task ID={namespace.task_id}')

    elif namespace.action == 'unpopulate':

        service.unpopulate_folder(user_id=namespace.user_id,
                                  folder_id=namespace.folder_id,
                                  task_id=namespace.task_id)
        print('Task(ID={namespace.task_id}) no longer in this folder')

    elif namespace.action == 'delete':
        service.delete_folder(user_id=namespace.user_id,
                              folder_id=namespace.folder_id)
        print(f'Folder(ID={namespace.folder_id}) has been deleted')


def print_plan(plan, gen_tasks):
    print(plan)
    if gen_tasks:
        print(f'Plan task:')
        print(plan.task)
        print_collection(gen_tasks, mes1='Generated by plan tasks:',
                         mes2='There are no tasks generated by plan')


def plan_show_handlers(service: AppService, namespace):
    if namespace.show_type == 'id':
        plan = service.get_plan_by_id(user_id=namespace.user_id,
                                      plan_id=namespace.plan_id)
        tasks = None
        if namespace.tasks:
            tasks = service.get_generated_tasks_by_plan(user_id=namespace.user_id,
                                                        plan_id=plan.id)
        print_plan(plan, tasks)

    elif namespace.show_type == 'all':
        print('test')
        plans = service.get_all_plans(user_id=namespace.user_id)
        if namespace.tasks:
            for plan in plans:
                tasks = service.get_generated_tasks_by_plan(user_id=namespace.user_id,
                                                            plan_id=plan.id)
                print_plan(plan, tasks)
        else:
            for plan in plans:
                print(plan)


def plan_handler(service: AppService, namespace):
    if namespace.action == 'create':

        plan = service.create_plan(user_id=namespace.user_id,
                                   task_id=namespace.task_id,
                                   period_amount=namespace.period_amount,
                                   period_type=namespace.period_type,
                                   repetitions_amount=namespace.plan_amount,
                                   end_date=namespace.end_date)
        print('Created plan:')
        print(plan)

    elif namespace.action == 'show':

        plan_show_handlers(service, namespace)

    elif namespace.action == 'edit':

        plan = service.update_plan(user_id=namespace.user_id,
                                   plan_id=namespace.plan_id,
                                   period_amount=namespace.period_amount,
                                   period_type=namespace.period_type,
                                   repetitions_amount=namespace.plan_amount,
                                   end_date=namespace.end_date)
        print('Updated plan:')
        print(plan)

    elif namespace.action == 'delete':
        service.delete_plan(user_id=namespace.user_id,
                            plan_id=namespace.plan_id)
        print('Plan{ID={namespace.plan_id}) has been deleted')


def users_handler(service: AppService, namespace):
    if namespace.action == 'show':
        if namespace.show_type == 'id':
            if service.user_with_id_exist(user_id=namespace.user_id):
                print('User with following id exist')
            else:
                print('User not found')
        elif namespace.show_type == 'all':
            users = service.get_all_users_ids()
            if users:
                print('Users:')
                for user in users:
                    print(user)
            else:
                print('App dont have any users')


def commands_handler(service: AppService, namespace):

    if namespace.entity == 'task':
        task_handler(service, namespace)

    elif namespace.entity == 'folder':
        folder_handler(service, namespace)

    elif namespace.entity == 'plan':
        plan_handler(service, namespace)

    elif namespace.entity == 'users':
        users_handler(service, namespace)
