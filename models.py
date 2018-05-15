from peewee import Model, SqliteDatabase, CharField, ForeignKeyField, DateTimeField
from playhouse.sqlite_ext import *
from utils import EnumField, STATUS

db = SqliteDatabase('todoapp.db')


class ModelBase(Model):
    class Meta:
        database = db


class User(ModelBase):
    username = CharField(unique=True)
    password_hash = None
    password_salt = None
    email = CharField(unique=True)

class Folder(ModelBase):

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    name = CharField()
    owner = ForeignKeyField(User, backref='folders')


class Group(ModelBase):

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    name = CharField()
    owner = ForeignKeyField(User, backref='groups')


class Event(ModelBase):

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    name = CharField()
    owner = ForeignKeyField(User, backref='events')


class Task(ModelBase):

    def __init__(self, name, description,
                 owner, parent_task, status,
                 start_date, end_date, assigned=None, Group=None):
        self.name = name
        self.description = description
        self.owner = owner
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.assigned = assigned
        self.group = self.group

    name = CharField()
    description = CharField()
    owner = ForeignKeyField(User, backref='tasks')
    parent_task = ForeignKeyField('self', null=True)
    group = ForeignKeyField(Group, null=True)
    status = EnumField(STATUS)
    assigned = ForeignKeyField(User, null=True)
    start_date = DateTimeField()
    end_date = DateTimeField()


class Cyclicity(ModelBase):

    def __init__(self, period, duration, event, task):
        self.period = period
        self.duration = duration
        self.event = event
        self.task = task

    period = DateTimeField()
    duration = DateTimeField()
    event = ForeignKeyField(Event, null=True)
    task = ForeignKeyField(Task, null=True)


class Notification(ModelBase):

    def __init__(self, date, task, event):
        self.date = date
        self.task = task
        self.event = event

    date = DateTimeField()
    event = ForeignKeyField(Event, null=True)
    task = ForeignKeyField(Task, null=True)


class UserToGroups(ModelBase):
    user = ForeignKeyField(User, backref='groups')
    group = ForeignKeyField(Group, backref='members')


class FolderTaskEvents(ModelBase):
    folder = ForeignKeyField(Folder)
    task = ForeignKeyField(Task, null=True)
    event = ForeignKeyField(Event, null=True)



class Comment(ModelBase):
    pass


def create_tables():
    with db:
        db.create_tables([Folder, Group, Event, Task,
                          Cyclicity, Notification, UserToGroups,
                          FolderTaskEvents])


def test_func_create_folder(name):
    folder = Folder.create(
        name = name,
        owner = None,
    )


def test_func_get_folders():
    return (Folder
            .select())
