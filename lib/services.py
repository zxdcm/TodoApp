from .models import (
    Database,
    User,
    Task,
    Folder,
    Notification,
    Repeat,
    TaskPriority,
    TaskStatus,
    Period,
    EndType,
    user_task_editors_association_table,
    user_task_observer_association_table,
    task_folder_association_table,
    Freezable,
)

from sqlalchemy import orm, exc, or_, and_, union
from typing import List
from .exceptions import (AccessError,
                         FolderExist,
                         check_object_exist)
from .utils import get_end_type, get_interval
import datetime


class AppService:

    def __init__(self, session=None):
        if session is None:
            session = Database.set_up_connection()
        self.session = session

    def get_user_by_id(self, user_id) -> User:
        """Allows to get user object by id.
           Raises UserNotFound exception if user with given id doesnt exist

        Parameters
        ----------
        user_id : int

        Returns
        -------
        User
            User object or UserNotFound exception

        """
        user = self.session.query(User).get(user_id)
        check_object_exist(user, user_id, 'User')
        return user

    def get_user_by_email(self, email) -> User:
        user = self.session.query(User).filter_by(email=email).one_or_none()
        check_object_exist(user, email, 'User')
        return user

    def user_can_write_task(self, user_id, task_id):
        q1 = self.session.query(Task).filter_by(id=task_id).filter(
            or_(Task.user_id == user_id, Task.assigned_id == user_id)).one_or_none()
        if q1:
            return True
        q2 = self.session.query(user_task_editors_association_table).filter_by(
            task_id=task_id, user_id=user_id).one_or_none()
        if q2:
            return True
        raise AccessError('User doesnt have permissions to this task')

    def user_can_read_task(self, user_id, task_id):
        q1 = self.session.query(Task).filter_by(id=task_id).filter(
            or_(Task.user_id == user_id, Task.assigned_id == user_id)).one_or_none()
        if q1:
            return True
        q2 = self.session.query(user_task_editors_association_table,
                                user_task_observer_association_table).filter_by(
            task_id=task_id, user_id=user_id).one_or_none()
        if q2:
            return True
        raise AccessError('User doesnt have permissions to read the task')

    def create_task(self, user_id, name, description=None,  start_date=None,
                    priority=None, status=None,
                    end_date=None, parent_task_id=None,
                    assigned_id=None, group_id=None) -> Task:
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
        group_id : int

        Returns
        -------
        Task
            Task object

        """
        user = self.session.query(User).get(user_id)
        check_object_exist(user, user_id, 'User')

        if priority:
            priority = TaskPriority[priority.upper()]

        if parent_task_id:
            self.user_can_write_task(user_id, parent_task_id)

        task = Task(user_id=user_id, name=name, description=description,
                    start_date=start_date, priority=priority,
                    end_date=end_date, parent_task_id=parent_task_id,
                    assigned_id=assigned_id, group_id=group_id)

        self.session.add(task)
        self.session.commit()
        return task

    def update_task(self, user_id, task_id, args: dict):
        if 'priority' in args:
            args['priority'] = TaskPriority[args['priority'].upper()]

        self.user_can_write_task(user_id=user_id, task_id=task_id)

        self.session.query(Task).get(task_id).update(args)
        self.session.commit()
        return self.session.query(Task).get(task_id)

    def get_task_by_id(self, user_id, task_id) -> Task:
        self.user_can_read_task(user_id, task_id)
        return self.session.query(Task).get(task_id)

    def share_task_on_read(self, user_creator_id, task_id, user_receiver_id):
        self.user_can_read_task(user_creator_id, task_id)
        receiver = self.get_user_by_id(user_receiver_id)
        task = self.session.query(Task).get(task_id)
        task.observers.append(receiver)
        self.session.commit()

    def share_task_on_write(self, user_creator_id, task_id, user_receiver_id):
        self.user_can_write_task(user_creator_id, task_id)
        receiver = self.get_user_by_id(user_receiver_id)
        task = self.session.query(Task).get(task_id)
        task.editors.append(receiver)
        self.session.commit()

    def unshare_task_on_read(self, user_creator_id, task_id, user_receiver_id):
        self.user_can_write_task(user_creator_id, task_id)
        receiver = self.get_user_by_id(user_receiver_id)
        task = self.session.query(Task).get(task_id)
        task.observers.remove(receiver)
        self.session.commit()

    def unshare_task_on_write(self, user_owner_id, task_id, user_receiver_id):
        self.user_can_write_task(user_owner_id, user_receiver_id)
        receiver = self.get_user_by_id(user_receiver_id)
        task = self.session.query(Task).get(task_id)
        task.editors.remove(receiver)
        self.session.commit()

    def get_own_tasks(self, user_id) -> List[Task]:
        """Method allows to get all tasks created by user.

        Parameters
        ----------
        user_id : int

        Returns
        -------
        List[Task]
            List of tasks

        """
        self.get_user_by_id(user_id)
        return self.session.query(Task).filter_by(user_id=user_id).all()

    def get_user_assigned_tasks(self, user_id) -> List[Task]:
        self.get_user_by_id(user_id)
        return self.session.query(
            Task).filter_by(assigned_id=user_id).all()

    def get_observable_tasks(self, user_id) -> List[Task]:
        """Method allows to get all observable tasks.

        Returns
        -------
        List[Task]
            List of tasks

        """
        return self.session.query(Task).join(
            user_task_observer_association_table).filter_by(
                user_id=user_id
        ).all()

    # rename
    def get_writeble_tasks(self, user_id) -> List[Task]:
        return self.session.query(Task).join(
            user_task_editors_association_table).filter_by(
                user_id=user_id
        ).all()

    def delete_task(self, user_id, task_id):
        self.user_can_write_task(user_id, task_id)
        self.session.query(Task).get(task_id).delete()
        self.session.commit()

    def archive_task_by_id(self, user_id, task_id, archive_substasks=None):
        self.user_can_write_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)
        task.status = TaskStatus.ARCHIVED
        self.session.commit()

    def done_task_by_id(self, user_id, task_id):
        self.user_can_write_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)
        task.status = TaskStatus.DONE
        self.session.commit()

    def create_folder(self, user_id, name) -> Folder:
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
        self.get_user_by_id(user_id)
        folder = self.session.query(Folder).filter_by(user_id=user_id,
                                                      name=name).one_or_none()
        if folder:
            raise FolderExist('Folder with given name already exist')
        folder = Folder(user_id=user_id, name=name)
        self.session.add(folder)
        self.session.commit()
        return folder

    def get_folder_by_id(self, user_id, folder_id) -> Folder:
        self.get_user_by_id(user_id)
        folder = self.session.query(Folder).filter_by(
            id=folder_id, user_id=user_id).one_or_none()
        check_object_exist(folder, (user_id, folder_id), 'Folder')
        return folder

    def get_folder_by_name(self, user_id, folder_name) -> Folder:
        self.get_user_by_id(user_id)
        folder = self.session.query(Folder).filter_by(
            folder_name=folder_name, user_id=user_id)
        check_object_exist(folder, (user_id, folder_name), 'Folder')
        return folder

    def get_all_folders(self, user_id):
        self.get_user_by_id(user_id)
        return self.session.query(Folder).filter_by(user_id=user_id).all()

    def update_folder(self, user_id, folder_id, args: dict):
        folder = self.get_folder_by_id(user_id=user_id, folder_id=folder_id)
        folder.update(args)
        self.session.commit()

    def delete_folder(self, user_id, folder_id):
        folder = self.get_folder_by_id(user_id, folder_id)
        self.session.delete(folder)
        self.session.commit()

    def get_folder_tasks(self, user_id):
        self.get_user_by_id(user_id)
        return self.session.query(Folder).join(
            task_folder_association_table).filter_by(user_id=user_id).all()

    def get_task_folders(self, user_id, task_id):
        return self.session.query(Folder).filter_by(user_id=user_id,
                                                    task_id=task_id).all()

    def populate_folder(self, user_id, folder_id, task_id):
        folder = self.get_folder_by_id(user_id, folder_id)
        task = self.get_task_by_id(user_id, task_id)
        if task in folder.tasks:
            return
        folder.tasks.append(task)
        self.session.commit()

        # maybe raise exception
    def unpopulate_folder(self, user_id, folder_id, task_id):
        folder = self.get_folder_by_id(user_id, folder_id)
        task = self.get_task_by_id(user_id, task_id)
        if task not in folder.tasks:
            return
        folder.tasks.remove(task)
        self.session.commit()

    def create_repeat(self, user_id, task_id,
                      period_amount,
                      period_type,
                      bound=False,
                      repetitions_amount=None,
                      end_date=None) -> Repeat:

        self.user_can_write_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)

        if task.start_date is None:
            task.start_date = datetime.datetime.now()

        period = Period[period_type.upper()]
        end_type = get_end_type(task.start_date, end_date,
                                period_amount)

        repeat = Repeat(user_id=user_id, task_id=task_id, period=period,
                        period_amount=period_amount,
                        end_type=end_type,
                        repetitions_amount=repetitions_amount,
                        end_date=end_date, bound=bound)
        self.session.add(repeat)
        self.session.commit()
        return repeat

    def get_repeat_by_id(self, user_id, repeat_id):
        repeat = self.session.query(Repeat).get(repeat_id)
        check_object_exist(repeat, repeat_id, 'Repeat')
        self.user_can_read_task(user_id, repeat.task_id)
        return repeat

    def get_shared_repeats(self, user_id):
        return self.session.query(Repeat).join(
            Repeat.task, user_task_editors_association_table).filter_by(
                user_id=user_id).all()

    def get_own_repeats(self, user_id):
        return self.session.query(Repeat).filter_by(user_id=user_id).all()

    def get_all_repeats(self, user_id):
        repeats = self.session.query(Repeat).join(
            Repeat.task, user_task_editors_association_table).filter_by(
                user_id=user_id).all()
        repeats += self.session.query(Repeat).filter_by(user_id=user_id).all()
        return repeats

    def get_generated_tasks(self, user_id):
        pass
        # epeats = self.session.query(Task).filter()

    def get_active_repeats(self, user_id, repeats=None) -> List[Repeat]:
        if repeats is None:
            repeats = self.get_all_repeats(user_id)
        repeats = self.get_all_repeats(user_id)
        active_list = []
        for repeat in repeats:
            interval = get_interval(repeat.period, repeat.period_amount)
            near_activation = repeat.last_activated + interval
            if repeat.end_type == EndType.AMOUNT:
                if (near_activation < datetime.datetime.now() and
                        repeat.repetitions_count < repeat.repetitions_amount):
                    active_list.append(repeat)
            elif repeat.end_type == EndType.DATE:
                if (near_activation < datetime.datetime.now() and
                        near_activation < repeat.end_date):
                    active_list.append(repeat)
            elif near_activation < datetime.datetime.now():
                active_list.append(repeat)

        return active_list

    def delete_unactive_repeats(self, user_id):
        repeats = self.get_all_repeats(user_id)
        if repeats:
            active_list = self.get_active_repeats(repeats)
            unactive = [x for x in repeats + active_list if x not in repeats
                        or x not in active_list]
            # need to test does it work: for x in unactive: self.session.delete(x)
            self.session.delete(*unactive)
            self.session.commit()

    def generate_tasks(self, user_id, active_repeats=None):
        ...

    def delete_repeat(self, user_id, repeat_id):
        self.get_repeat_by_id(user_id, repeat_id).delete()
        self.session.commit()

    def update_repeat(self, user_id, repeat_id, args: dict) -> Repeat:
        repeat = self.session.query(Repeat).get(repeat_id)
        check_object_exist(repeat, repeat_id, 'Repeat')
        self.user_can_write_task(user_id, repeat.task_id)
        repeat.update(args)
        return repeat

    @staticmethod
    def create_user(name, email):
        session = Database.set_up_connection()
        try:
            user = User(name, email)
            session.add(user)
            session.commit()
            session.close()
        except exc.IntegrityError:
            print('Database error')

    def get_obj_by_id(self, cls, id):
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
