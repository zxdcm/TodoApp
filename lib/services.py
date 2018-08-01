from .models import (
    Database,
    User,
    Task,
    Folder,
    Group,
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
from .exceptions import AccessError, UserNotFound, TaskNotFound


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
        user = self.session.query(User).filter_by(id=user_id).one_or_none()
        if user is None:
            raise UserNotFound('User with given id not found')
        return user

    def get_user_by_email(self, email):
        user = self.session.query(User).filter_by(email=email).one_or_none()
        if user is None:
            raise UserNotFound('User with given id not found')
        return user

    def user_can_write_task(self, user_id, task_id):
        self.get_user_by_id(user_id)
        rights = self.session.query(
            user_task_editors_association_table).filter_by(
                user_id=user_id, task_id=task_id).one_or_none()
        if rights is None:
            raise AccessError(
                'The user doesnt have permission to write the task')
        return True

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
        self.get_user_by_id(user_id)
        rights = self.session.query(
            user_task_observer_association_table).filter_by(
                user_id=user_id, task_id=task_id).one_or_none()
        if rights is None:
            raise AccessError(
                'The user doesnt have permission to access the task')
        return True

    def create_task(self, user_id, name, description,  start_date,
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
        user = self.get_user_by_id(user_id)
        if priority is not None:
            priority = TaskPriority[priority.upper()]

        if status is not None:
            status = TaskStatus[status.upper()]

        if parent_task_id is not None:
            self.get_task(user_id, parent_task_id)
        task = Task(user_id=user_id, name=name, description=description,
                    start_date=start_date, priority=priority,
                    end_date=end_date, parent_task_id=parent_task_id,
                    assigned_id=assigned_id, group_id=group_id)
        task.observers.append(user)
        task.editors.append(user)
        self.session.add(task)
        self.session.commit()
        return task

    def update_task(self, user_id, task_id, args):
        self.user_can_write_task(user_id=user_id, task_id=task_id)
        self.session.query(Task).filter_by(id=task_id).update(args)
        return self.session.query(Task).get(task_id)

    def get_task(self, user_id, task_id) -> Task:
        self.user_can_read_task(user_id, task_id)
        return self.session.query(Task).filter_by(id=task_id).one()

    def share_task(self, user_owner_id, task_id, user_receiver_id):
        task = self.get_task(user_owner_id, task_id)
        receiver = self.get_user_by_id(user_receiver_id)
        task.observers.append(receiver)
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

    def get_all_tasks(self, user_id) -> List[Task]:
        """Method allows to get all tasks.

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

        # maybe rework later
        # everyone who has access to task can perform this action.
    def delete_task(self, user_id, task_id):
        task = self.get_task(user_id, task_id)
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
        folder = Folder(user_id=user_id, name=name)
        self.session.add(folder)
        self.session.commit()
        return folder

    def create_group(self, user_id, name) -> Group:
        """Allows to create group

        Parameters
        ----------
        user_id : int
            id of user who create group
        name : str

        Returns
        -------
        Group
            Group object

        """
        group = Group(user_id=user_id, name=name)
        self.session.add(group)
        self.session.commit()
        return group

    def create_notification(self, task_id, date) -> Notification:
        """Allows to create notification.

        Parameters
        ----------
        task_id : int
            id of task to notify
        date : type
            notification date

        Returns
        -------
        Notification
            Notification object

        """
        notification = Notification(task_id=task_id, date=date)
        self.session.add(notification)
        self.session.commit()
        return notification

    def create_repeat(self, task_id, period, duration) -> Repeat:
        if period is not None:
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

    # def get_user_assigned_tasks(self) -> List[Task]:
    #     return self.session.query(
    #         Task).filter(Task.assigned == self.current_user).all()

    # def get_user_groups(self) -> List[Group]:
    #     return self.session.query(
    #         Task).filter(Group.owner == self.current_user or
    #                      Group.members.contains(self.current_user)
    #                      ).all()

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
