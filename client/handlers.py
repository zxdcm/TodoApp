from lib.services import AppService
from client.parsers import exclude_keys


def task_show_handler(service: AppService, namespace):
    if namespace.show_type == 'id':
        task = service.get_task_by_id(user_id=namespace.user_id,
                                      task_id=namespace.task_id)
        print(task)

    elif namespace.show_type == 'own':
        [print(x) for x in service.get_own_tasks(
            user_id=namespace.user_id)]

    elif namespace.show_type == 'inner':
        [print(x) for x in service.get_inner_tasks(
            user_id=namespace.user_id, task_id=namespace.parent_task_id)]

    elif namespace.show_type == 'access':
        [print(x) for x in service.get_available_tasks(
            user_id=namespace.user_id)]

    elif namespace.show_type == 'assigned':
        [print(x) for x in service.get_user_assigned_tasks(
            user_id=namespace.user_id)]

    elif namespace.show_type == 'repeat':
        [print(x) for x in service.get_generated_tasks(
            user_id=namespace.user_id)]

    elif namespace.show_type == 'repeatless':
        [print(x) for x in service.get_available_tasks(
            user_id=namespace.user_id) if x.repeat]


def task_handler(service: AppService, namespace):
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
        task_show_handler(service, namespace)
    elif namespace.action == 'share':
        service.share_task(user_id=namespace.user_id,
                           user_receiver_id=namespace.user_receiver_id,
                           task_id=namespace.task_id)
        print(f'Task with ID={namespace.task_id} shared with user ID={namespace.user_receiver_id}')

    elif namespace.action == 'unshare':
        service.unshared(user_id=namespace.user_id,
                         user_receiver_id=namespace.user_receiver_id,
                         task_id=namespace.task_id)

        print(f'Task {namespace.task_id} unshared on {namespace.user_receiver_id}')
    elif namespace.action == 'edit':
        args = exclude_keys(namespace)
        if len(args) == 0:
            print('Nothing to update.')
        else:
            service.update_task(user_id=namespace.user_id,
                                task_id=namespace.task_id,
                                args=args)
            print('Task updated')

    elif namespace.action == 'delete':
        service.delete_task(user_id=namespace.user_id,
                            task_id=namespace.task_id)
        print(f'Task with {namespace.task_id} ID deleted')


def folder_handler(service: AppService, namespace):
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

        service.populate_folder(user_id=namespace.user_id,
                                folder_id=namespace.folder_id,
                                task_id=namespace.task_id)

    elif namespace.action == 'unpopulate':

        service.unpopulate_folder(user_id=namespace.user_id,
                                  folder_id=namespace.folder_id,
                                  task_id=namespace.task_id)
        # folder = service.get_folder_by_id(user_id=namespace.user_id,
        #                                   folder_id=namespace.id)
        # task = folder.get_task_by_id(user_id=namespace.user_id,
        #                              task_id=namespace.task_id)
        # if task in folder.tasks:
        #     folder.tasks.remove(task)
        #     print(f'Task {task.id} no longer in {folder.name}')
        # else:
        #     print('Folder doesnt contain task with following id')
        # service.save_updates()


def repeat_handler(service: AppService, namespace):
    ...


def commands_handler(service: AppService, namespace):
    if namespace.entity == 'task':
        task_handler(service, namespace)

    elif namespace.entity == 'folder':
        folder_handler(service, namespace)

    elif namespace.entity == 'repeat':
        repeat_handler(service, namespace)
