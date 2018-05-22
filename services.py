
from models import Database, User, Task, \
    Folder, Group, Notification, Cyclicity
from sqlalchemy import exc
from datetime import datetime


class AppService:

    def __init__(self, email):

        self.session = Database.set_up_connection()
        self.current_user = self.session.query(User).filter(User.email == email).first()

    def create_folder(self, name, owner):
        folder = Folder(name, owner)
        self.session.add(folder)
        self.session.commit()
        return folder

    def create_task(self, name, description='',  start_date=datetime.now(), end_date=None,
                    parent_task=None, group=None, assigned=None):
        task = Task(name, self.current_user, description, # fix models
                    start_date, end_date, parent_task,
                    group, None)
        self.session.add(task)
        self.session.commit()
        return task

    def create_group(self, name, owner):
        group = Group(name, owner)
        self.session.add(group)
        self.session.commit()
        return group

    def create_notification(self, task, date=datetime.now()):
        notification = Notification(task, date)
        self.session.add(notification)
        self.session.commit()
        return notification

    def create_cyclicity(self, task, period, duration):
        cyclicity = Cyclicity(task, period, duration)
        self.session.add(cyclicity)
        self.session.commit()
        return cyclicity

    def get_user_folders(self):
        return self.current_user.folders

    def get_user_tasks(self):
        return self.session.query(
            User).filter(Task.owner.id == self.current_user)

    def get_user_assigned_tasks(self):
        return self.session.query(
            Task).filter(Task.assigned == self.current_user)

    def get_user_groups(self):
        return self.session.query(
            Task).filter(Group.owner == self.current_user or
                         Group.members.contains(self.current_user)
                         )

    def get_task_by_id(self, task_id):
        return self.session.query(
            Task).filter(Task.id == task_id)
        pass


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

