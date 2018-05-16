from models import *
from peewee import IntegrityError, DatabaseError


class AppService():

    def __init__(self, user=None):
        Database.create_tables()
        Database.set_up_connection()
        self.current_user = user

    def create_folder(self, name):
        try:
            with db_connection.atomic():
                Folder.create(name='test', owner=self.current_user)
        except IntegrityError:
            print('Such folder already exists')
        except DatabaseError:
            pass

    def create_task(self, name, description, end_date, start_date):
        try:
            with db_connection.atomic():
                Task.create(name=name, description=description,
                            end_date=end_date, start_date=start_date,
                            owner=self.current_user)
        except IntegrityError:
            print("Must be uniq")
        except DatabaseError:
            pass

    def get__user_folders(self):
        return self.current_user.folders

    def get_user_tasks(self):
        return self.current_user.tasks

    def get__user_events(self):
        return self.current_user.events

    @staticmethod
    def get_folder_by_id(id):
        return Folder.get_by_id(id)

    @staticmethod
    def get_task_by_id(id):
        return Task.get_by_id(id)

    @staticmethod
    def create_user(name, email):
        try:
            with db_connection.atomic():
                return User.create(name=name, email=email)
        except IntegrityError:
            print('Username and email must be uniq')
        except DatabaseError:
            pass

    @staticmethod # temp property
    def get_user(email):
        try:
            with db_connection.atomic():
                return User.get(User.email == email)
        except IntegrityError:
            print('Username and email must be uniq')
        except DatabaseError:
            pass
