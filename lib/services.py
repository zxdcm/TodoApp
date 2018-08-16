from lib.models import (
    Task,
    Folder,
    Notification,
    Repeat,
    TaskPriority,
    TaskStatus,
    Period,
    EndType,
    task_folder_association_table,
    TaskUserEditors,
    set_up_connection,
)

from sqlalchemy import (orm,
                        exc,
                        or_)
from typing import List

from lib.exceptions import (AccessError,
                            FolderExist,
                            UpdateError,
                            ObjectNotFound,
                            CreateError)

from lib.utils import (get_end_type,
                       get_interval,
                       check_object_exist)

from datetime import datetime


class AppService:

    def __init__(self, session=None):
        if session is None:
            session = set_up_connection()
        self.session = session

    def user_can_access_task(self, user_id: int, task_id: int):
        if self.session.query(Task).filter_by(
                id=task_id, owner_id=user_id).one_or_none():
            return True
        if self.session.query(Task).join(TaskUserEditors).filter_by(
                user_id=user_id, task_id=task_id).all():
            return True
        raise AccessError('User doesnt have permissions to this task')

    def user_with_id_exist(self, user_id: int):
        user_tasks = self.session.query(TaskUserEditors).filter_by(user_id=user_id).all()
        if user_tasks:
            return True

    def get_all_users_ids(self):
        user_ids = set(x.user_id for x in self.session.query(TaskUserEditors).all())
        return user_ids

    def create_task(self,
                    user_id,
                    name,
                    status='todo',
                    priority='medium',
                    description=None,
                    start_date=datetime.now(),
                    end_date=None,
                    parent_task_id=None,
                    assigned_id=None
                    ) -> Task:
        """Allow create task with provided parameters

        Parameters
        ----------
        user_id : int
            id of user who create task
        name : str
        description : str
        start_date : datetime

        Optional
        ----------
        priority : str
        status : str
        end_date  : datetime
        parent_task_id : int
        assigned_id : int
            id of assigned user

        Returns
        -------
        Task
            Task object

        """

        if priority:
            try:
                priority = TaskPriority[priority.upper()]
            except KeyError as e:
                raise CreateError('Priority not found') from e

        if status:
            try:
                status = TaskStatus[status.upper()]
            except KeyError as e:
                raise CreateError('Status not found') from e

        if parent_task_id:
            self.user_can_access_task(user_id=user_id, task_id=parent_task_id)

        if start_date and end_date:
            if start_date > end_date:
                raise CreateError('End date has to be after start date')
        if start_date:
            start_date.replace(microsecond=0)

        task = Task(owner_id=user_id, name=name, description=description,
                    start_date=start_date, priority=priority,
                    end_date=end_date, parent_task_id=parent_task_id,
                    assigned_id=assigned_id, status=status)
        task.editors.append(TaskUserEditors(user_id=user_id, task_id=task.id))

        self.session.add(task)
        self.session.commit()
        return task

    def update_task(self,
                    user_id: int,
                    task_id: int,
                    args: dict) -> Task:

        if 'priority' in args:
            try:
                args['priority'] = TaskPriority[args['priority'].upper()]
            except KeyError:
                raise UpdateError('Priority not found')
        if 'status' in args:
            try:
                args['status'] = TaskStatus[args['status'].upper()]
            except KeyError:
                raise UpdateError('Priority not found')

        if 'start_date' and 'end_date' in args:
            if args['start_date'] > args['end_date']:
                raise UpdateError('End date has to be after start date')

        self.user_can_access_task(user_id=user_id, task_id=task_id)

        try:
            args['updated'] = datetime.now().replace(microsecond=0)
            self.session.query(Task).filter_by(id=task_id).update(args)
        except exc.SQLAlchemyError as e:
            raise UpdateError('Args error. Args dict can not be empty') from e

        self.session.commit()
        return self.session.query(Task).get(task_id)

    def get_task_by_id(self,
                       user_id: int,
                       task_id: int) -> Task:
        task = self.session.query(Task).get(task_id)
        check_object_exist(task,
                           f'user_id : {user_id} task_id : {task_id}',
                           'Task')
        self.user_can_access_task(user_id, task_id)
        return task

    def assign_user(self, user_id: int,
                    task_id: int,
                    user_receiver_id: int):

        self.user_can_access_task(user_id, task_id)
        new_editor = TaskUserEditors(user_id=user_receiver_id, task_id=task_id)
        task = self.session.query(Task).get(task_id)
        task.editors(new_editor)
        task.assigned_id = user_id
        self.session.commit()

    def share_task(self,
                   user_id: int,
                   task_id: int,
                   user_receiver_id: int):

        self.user_can_access_task(user_id, task_id)
        new_editor = TaskUserEditors(user_id=user_receiver_id, task_id=task_id)

        self.session.add(new_editor)
        self.session.commit()

    def unshare_task(self,
                     user_id: int,
                     task_id: int,
                     user_receiver_id: int):
        self.user_can_access_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)

        if user_receiver_id == task.owner_id:
            raise AccessError('You can not unshare task with its owner')
        editor = self.session.query(TaskUserEditors).filter_by(
            user_id=user_id,
            task=task.id)

        task.editors.remove(editor)

        self.session.commit()

    def get_own_tasks(self, user_id: int) -> List[Task]:
        """Method allows to get all tasks created by user.

        Parameters
        ----------
        user_id : int

        Returns
        -------
        List[Task]
            List of tasks

        """
        return self.session.query(
            Task).filter_by(owner_id=user_id).all()

    def get_user_assigned_tasks(self, user_id: int) -> List[Task]:
        return self.session.query(
            Task).filter_by(assigned_id=user_id).all()

    def get_available_tasks(self, user_id: int) -> List[Task]:
        """Method allows to get all available tasks.

        Returns
        -------
        List[Task]
            List of tasks

        """
        return self.session.query(Task).join(
            TaskUserEditors).filter_by(
                user_id=user_id).all()

    def delete_task(self, user_id: int, task_id: int, delete_repeat=True):
        self.user_can_access_task(user_id, task_id)
        self.session.query(Task).filter_by(id=task_id).delete()
        if delete_repeat:
            self.session.query(Repeat).filter_by(task_id=task_id).delete()
        self.session.commit()

    def add_subtask(self, user_id: int, task_id: int, subtask_id: int):
        self.user_can_access_task(user_id, task_id)
        self.user_can_access_task(user_id, subtask_id)
        subtask = self.session.query(Task).get(subtask_id)
        if subtask.parent_task_id:
            raise UpdateError('Subtask already has parent task.')
        subtask.parent_task_id = task_id
        self.session.commit()

    def get_subtasks(self, user_id: int, task_id: int):
        self.user_can_access_task(user_id, task_id)
        return self.session.query(Task).filter_by(
            parent_task_id=task_id).join(
                TaskUserEditors).filter_by(user_id=user_id)

    def change_task_status(self,
                           user_id: int,
                           task_id: int,
                           status: str,
                           apply_subtasks=None):
        self.user_can_access_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)

        try:
            status = TaskStatus[status.upper()]
        except KeyError:
            raise UpdateError('Status not found')

        task.status = status
        if apply_subtasks:
            self.session.query(Task).filter_by(
                parent_task_id=task_id).join(
                    TaskUserEditors).filter_by(
                        user_id=user_id).update({'status': status})
        self.session.commit()

    def create_folder(self, user_id: int, name: str) -> Folder:
        """Allow create folder with provided name for user

        Parameters
        ----------
        user_id: int
            id of user who create folder
        name : str
            Folder name

        Returns
        -------
        Folder
            Folder object

        """
        folder = self.session.query(Folder).filter_by(user_id=user_id,
                                                      name=name).one_or_none()
        if folder:
            raise FolderExist('User already has folder with following name')
        folder = Folder(user_id=user_id, name=name)
        self.session.add(folder)
        self.session.commit()
        return folder

    def get_folder_by_id(self, user_id: int, folder_id: int) -> Folder:
        folder = self.session.query(Folder).filter_by(
            id=folder_id, user_id=user_id).one_or_none()
        check_object_exist(folder,
                           f'folder_id : {folder_id}',
                           'Folder')
        return folder

    def get_folder_by_name(self, user_id: int, folder_name: int) -> Folder:
        folder = self.session.query(Folder).filter_by(
            folder_name=folder_name, user_id=user_id)
        check_object_exist(folder, (user_id, folder_name), 'Folder')
        return folder

    def get_or_create_folder(self, user_id: int, name: str) -> Folder:
        try:
            folder = self.get_folder_by_name(user_id, name)
        except ObjectNotFound as e:
            folder = Folder(user_id=user_id, name=name)
            self.session.add(folder)
            self.session.commit()
        finally:
            return folder

    def get_all_folders(self, user_id: int) -> List[Folder]:
        return self.session.query(Folder).filter_by(user_id=user_id).all()

    def update_folder(self, user_id: int, folder_id: int, args: dict):
        self.get_folder_by_id(user_id=user_id, folder_id=folder_id)
        try:
            self.session.query(Folder).update(args)
        except exc.SQLAlchemyError as e:
            raise UpdateError('Args error. Args dict can not be empty')
        self.session.commit()

    def delete_folder(self, user_id: int, folder_id: int):
        folder = self.get_folder_by_id(user_id, folder_id)
        self.session.delete(folder)
        self.session.commit()

    # def get_folder_tasks(self, user_id: int): # probably that is pointless
    #     return self.session.query(Folder).join(
    #         task_folder_association_table).filter_by(user_id=user_id).all()

    def get_task_folders(self, user_id: int, task_id: int):
        return self.session.query(Folder).filter_by(user_id=user_id,
                                                    task_id=task_id).all()

    def populate_folder(self, user_id: int, folder_id: int, task_id: int):
        folder = self.get_folder_by_id(user_id, folder_id)
        task = self.get_task_by_id(user_id, task_id)
        if task in folder.tasks:
            return
        folder.tasks.append(task)
        self.session.commit()

        # maybe raise exception
    def unpopulate_folder(self,
                          user_id: int,
                          folder_id: int,
                          task_id: int):
        folder = self.get_folder_by_id(user_id, folder_id)
        task = self.get_task_by_id(user_id, task_id)
        if task not in folder.tasks:
            return
        folder.tasks.remove(task)
        self.session.commit()

    def create_repeat(self, user_id, task_id,
                      period_amount,
                      period_type,
                      repetitions_amount=None,
                      end_date=None) -> Repeat:

        self.user_can_access_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)
        if task.start_date is None:
            raise CreateError('Task should have start date')

        period = Period[period_type.upper()]
        start_date = task.start_date

        end_type = get_end_type(start_date, period, period_amount,
                                end_date, repetitions_amount)
        repeat = Repeat(user_id=user_id, task_id=task_id, period=period,
                        period_amount=period_amount,
                        end_type=end_type,
                        repetitions_amount=repetitions_amount,
                        end_date=end_date,
                        start_date=start_date)
        self.session.add(repeat)
        self.session.commit()
        return repeat

    def get_repeat_by_id(self, user_id: int, repeat_id: int) -> Repeat:
        repeat = self.session.query(Repeat).get(repeat_id)
        check_object_exist(repeat, repeat_id, 'Repeat')
        try:
            self.user_can_access_task(user_id, repeat.task_id)
        except AccessError as e:
            raise AccessError('User doesnt have permission to access this Repeat') from e
        return repeat

    def get_all_repeats(self, user_id: int) -> List[Repeat]:
        return self.session.query(Repeat).join(Task).join(
            TaskUserEditors).filter(
                TaskUserEditors.user_id == user_id).all()

    def get_own_repeats(self, user_id: int) ->Repeat:
        return self.session.query(Repeat).filter_by(user_id=user_id).all()

    def get_generated_tasks_by_repeat(self, user_id: int,
                                      repeat_id: int) -> List[Task]:
        repeat = self.session.query(Repeat).get(repeat_id)
        return self.session.query(Task).filter_by(
            parent_task_id=repeat.task_id).join(
            TaskUserEditors).all()

    def get_active_repeats(self, user_id: int, repeats=None) -> List[Repeat]:
        if repeats is None:
            repeats = self.get_all_repeats(user_id)

        repeats = self.get_all_repeats(user_id)
        active_list = []

        for repeat in repeats:

            interval = get_interval(repeat.period, repeat.period_amount)
            near_activation = repeat.last_activated + interval

            if repeat.end_type == EndType.AMOUNT:

                if (near_activation < datetime.now() and
                        repeat.repetitions_counter < repeat.repetitions_amount):
                    active_list.append(repeat)

            elif repeat.end_type == EndType.DATE:

                if (near_activation < datetime.now() and
                        near_activation < repeat.end_date):
                    active_list.append(repeat)

            elif near_activation < datetime.now():
                active_list.append(repeat)

        return active_list

    def generate_tasks(self, user_id: int, active_repeats=None) -> List[Task]:
        """

        Parameters
        ----------
        user_id : type
            Description of parameter `user_id`.
        active_repeats : type
            Description of parameter `active_repeats`.

        Returns
        -------
        None

        """
        '''
       foreach repeat:
          calculate interval according to period and period amount
          sum last_activation and interval and get near activation
          if near activation < current time
              if EndType == AMOUNT or EndType == DATE and we reached the goal:
                  we dont have to create any task. Repeat rule is completed now
              otherwise
                we keep creating tasks on every activation + interval
                                            until we reach current time
            '''
        if active_repeats is None:
            active_repeats = self.get_active_repeats(user_id)
        for repeat in active_repeats:
            interval = get_interval(repeat.period, repeat.period_amount)
            near_activation = repeat.last_activated + interval

            while near_activation < datetime.now():

                if (repeat.end_type == EndType.AMOUNT and
                        repeat.repetitions_counter == repeat.repetitions_amount):
                    break
                if (repeat.end_type == EndType.DATE and
                        near_activation > repeat.end_date):
                    break

                task = self.create_task(user_id=user_id,
                                        name=repeat.task.name,
                                        description=repeat.task.description,
                                        start_date=near_activation,
                                        parent_task_id=repeat.task.id,
                                        assigned_id=repeat.task.assigned_id)
                repeat.last_activated = near_activation
                near_activation = repeat.last_activated + interval
                repeat.repetitions_counter += 1
                for x in repeat.task.editors:
                    if x.user_id is user_id:
                        continue
                    task.editors.append(
                        TaskUserEditors(user_id=x.user_id,
                                        task_id=task.id))
                    # # TODO:  fix
                self.session.add(task)

        self.session.commit()

    def delete_repeat(self, user_id: int, repeat_id: int):
        self.get_repeat_by_id(user_id, repeat_id).delete()
        self.session.commit()

    def update_repeat(self,
                      user_id: int,
                      repeat_id: int,
                      args: dict) -> Repeat:
        repeat = self.get_repeat_by_id(user_id=user_id, repeat_id=repeat_id)

        start_date = repeat.start_date
        end_date = repeat.end_date
        repetitions_amount = repeat.repetitions_amount

        if 'start_date' in args:
            start_date = args['start_date']
        if 'end_date' in args:
            end_date = args['end_date']
        if 'repetitions_amount' in args:
            repetitions_amount = args['repetitions_amount']
        args['end_type'] = get_end_type(start_date,
                                        end_date,
                                        repetitions_amount)

        try:
            repeat.update(args)
        except exc.SQLAlchemyError as e:
            raise UpdateError('Args error. Args dict can not be empty') from e
        return repeat

    def get_obj_by_id(self, cls, id: int):
        """This method allows to get any object from the db without validation
           Use this only if you are confident what are you doing
           After work with object - commit changes via save_updates method

        Parameters
        ----------
        cls : Library type
            Library type. (Any type from models.py)
        id : int
            Object id

        Returns
        -------
        Model
            Model or None

        """
        return self.session.query(cls).get(id)

    def delete_obj(self, obj):
        self.session.delete(obj)

        # Allows to commit updates made out of the lib
    def save_updates(self):
        self.session.commit()
