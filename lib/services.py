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
    user_task_editors_association_table,
    user_task_observer_association_table
)

from sqlalchemy import orm, exc
from datetime import datetime
from typing import List
from .exceptions import (AccessError,
                         UserNotFound,
                         TaskNotFound,
                         FolderNotFound,
                         FolderExist)


class AppService:
    """AppService class contains methods which allow
    to perform most frequent actions with library entities

    Parameters
    ----------
    email:
        Description of parameter `email`.

    Attributes
    ----------
    session : type
        Description of attribute `session`.
    """

    def __init__(self, session=None):
        if session is None:
            session = Database.set_up_connection()
        self.session = session
        # self.current_user = self.session.query(
        #     User).filter(User.email == email).first()

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
        if user is None:
            raise UserNotFound('User with given id not found')
        return user

    def get_user_by_email(self, email) -> User:
        user = self.session.query(User).filter_by(email=email).one_or_none()
        if user is None:
            raise UserNotFound('User with given email not found')
        return user

    def user_can_write_task(self, user_id, task_id):
        user = self.get_user_by_id(user_id)
        task = self.session.query(Task).get(task_id)
        if task:
            if (task.user_id == user_id or user in task.editors or
                    task.assigned_id == user_id):
                return True
            raise AccessError('User doesnt have permissions to write the task')
        raise TaskNotFound('Task with given id doesnt exist')

    def user_can_read_task(self, user_id, task_id):
        """Check user permissions on task with given id.

        Parameters
        ----------
        user_id : int
        task_id : int

        Returns
        -------
        Bool or AccessError exception

        """
        user = self.get_user_by_id(user_id)
        task = self.session.query(Task).get(task_id)
        if task:
            if (task.user_id == user_id or user in task.observers or
                    task.assigned_id == user_id):
                return True
            raise AccessError('User doesnt have permissions to read the task')
        raise TaskNotFound('Task with given id doesnt exist')

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
        self.get_user_by_id(user_id)
        if priority:
            priority = TaskPriority[priority.upper()]

        if status:
            status = TaskStatus[status.upper()]

        if parent_task_id:
            self.get_task_by_id(user_id, parent_task_id)
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
        self.session.query(Task).filter_by(id=task_id).update(args)
        self.session.commit()
        # return self.session.query(Task).get(task_id)

    def get_task_by_id(self, user_id, task_id) -> Task:
        self.user_can_read_task(user_id, task_id)
        return self.session.query(Task).get(task_id)

    def share_task_on_read(self, user_owner_id, task_id, user_receiver_id):
        self.user_can_write_task(user_owner_id, task_id)
        receiver = self.get_user_by_id(user_receiver_id)
        task = self.session.query(Task).get(task_id)
        task.observers.append(receiver)
        self.session.commit()

    def share_task_on_write(self, user_owner_id, task_id, user_receiver_id):
        self.user_can_write_task(user_owner_id, task_id)
        receiver = self.get_user_by_id(user_receiver_id)
        task = self.session.query(Task).get(task_id)
        task.editors.append(receiver)
        self.session.commit()

    def unshare_task_on_read(self, user_owner_id, task_id, user_receiver_id):
        self.user_can_write_task(user_owner_id, task_id)
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
        return self.session.query(Task).filter_by(user_id=user_id)

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
        self.get_user_by_id(user_id)
        return self.session.query(Task).join(
            user_task_observer_association_table).filter_by(
                user_id=user_id
        ).all()

    # rename
    def get_writeble_tasks(self, user_id) -> List[Task]:
        self.get_user_by_id(user_id)
        return self.session.query(Task).join(
            user_task_editors_association_table).filter_by(
                user_id=user_id
        ).all()

    def delete_task(self, user_id, task_id):
        self.user_can_write_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)
        self.session.delete(task)

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
        if folder is None:
            raise FolderNotFound('Folder with following id not found')
        return folder

    def get_folder_by_name(self, user_id, folder_name) -> Folder:
        self.get_user_by_id(user_id)
        folder = self.session.query(Folder).filter_by(
            folder_name=folder_name, user_id=user_id)
        if folder is None:
            raise FolderNotFound('Folder with following name not found')
        return folder

    def get_all_folders(self, user_id):
        self.get_user_by_id(user_id)
        return self.session.query(Folder).filter_by(user_id=user_id).all()

    def update_folder(self, user_id, folder_id, args: dict):
        self.session.query(Task).filter_by(id=folder_id,
                                           user_id=user_id).update(args)
        self.session.commit()

    def delete_folder(self, user_id, folder_id):
        folder = self.get_folder_by_id(user_id, folder_id)
        self.session.delete(folder)

    def create_notification(self, user_id, task_id, date) -> Notification:
        """Allows to create notification for task

        Parameters
        ----------
        user_id : int
            id of user who create notification
        task_id : int
            id of task to notify
        date : type
            notification date

        Returns
        -------
        Notification
            Notification object

        """
        self.user_can_write_task(user_id, task_id)
        notification = Notification(task_id=task_id, date=date)
        self.session.add(notification)
        self.session.commit()
        return notification

    def create_repeat(self, task_id, period, duration) -> Repeat:
        if period:
            period = Period[period.upper()]

        repeat = Repeat(task_id=task_id, period=period,
                        duration=duration)
        self.session.add(period)
        self.session.commit()
        return repeat

    # def get_user_folders(self, user_id) -> List[Folder]:
    #     """Methods allow get user folders.
    #
    #     Parameters
    #     ----------
    #     user_id : type
    #         id of user who get folders
    #
    #     Returns
    #     -------
    #     List[Folder]
    #         List of user folders.
    #
    #     """
        # return self.session.query(
        #     Folder).filter(Folder.owner == self.current_user).all()

    # def add_system_folder(self, name):
    #     if name not in self.sysfolders:
    #         self.sysfolders.append(name)
    #         self.create_folder(name)
    #     else:
    #         print('System folder already exist')

    # def remove_system_folder(self, name):
    #     if name not in self.sysfolders:
    #         print('System folder doesnt exist')
    #     else:
    #         self.sysfolders.remove(name)
    #         self.delete_folder_by_name(name)
    #
    # def delete_folder_by_name(self, name):
    #     if name in self.sysfolders:
    #         print('Error. System folder can''t be removed')
    #     else:
    #         self.session.query(
    #             Folder).filter(Folder.name == self.name).delete()
    #
    # def archive_task_by_id(self, id):
    #     task = self.session.query(
    #         Task).get(id)
    #     folder = self.session.query(
    #         Folder).filter(
    #             Folder.owner == self.current_user and
    #             Folder.name == 'Archive').first()
    #     if folder is None:
    #         folder = self.create_folder('Archive')
    #     folder.tasks.append(task)
    #     self.session.commit()

    @staticmethod   # temp func. need to rework with context manager
    def create_user(name, email):
        session = Database.set_up_connection()
        try:
            user = User(name, email)
            session.add(user)
            session.commit()
            session.close()
        except exc.IntegrityError:
            print('Database error')

    # Allows to commit updates made out of the lib
    def save_updates(self):
        self.session.commit()
