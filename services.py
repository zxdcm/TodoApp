
from models import Database, User, Task, Folder
from sqlalchemy import exc
from datetime import datetime

class AppService():

    def __init__(self, email):

        self.session = Database.set_up_connection()
        self.current_user = self.session.query(User).filter(User.email == email).first()

    def create_folder(self, name, owner):
        folder = Folder(name, owner)
        self.session.add(folder)
        self.session.commit()
        return folder

    def create_task(self, name, description='',  start_date=datetime.now(), end_date=None,
                    parent_task=None, group=None):
        task = Task(name, self.current_user.id, description, # fix models
                    start_date, end_date, parent_task,
                    group)
        self.session.add(task)
        self.session.commit()
        return task

    def get_user_folders(self):
        return self.current_user.folders

    def get_user_tasks(self):
        return self.current_user.tasks

    @staticmethod # temp func. need to rework with context manager
    def create_user(name, email):
        session = Database.set_up_connection()
        try:
            user = User(name, email)
            session.add(user)
            session.commit()
            session.close()
        except exc.IntegrityError:
            print('Database error')

    def __get_user__(self, email):
        return self.session.query(User).filter(User.email == email).first()


    def save_updates(self):
        'Allows to commit updates made out of the lib'
        self.session.commit()

