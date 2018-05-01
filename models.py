from peewee import *
import datetime

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
    name = CharField()
    owner = ForeignKeyField(User, null=True)


class Group(ModelBase):
    name = CharField()
    owner = ForeignKeyField(User)


class Event(ModelBase):
    name = CharField()
    owner = ForeignKeyField(User, backref='events')


class Task(ModelBase):
    name = CharField()
    description = CharField()
    owner = ForeignKeyField(User, backref='tasks')
    parent_task = ForeignKeyField('self', null=True)
    status = None
    start_date = DateTimeField()
    end_date = DateTimeField()


class Cyclicity(ModelBase):
    period = DateTimeField()
    duration = DateTimeField()
    event = ForeignKeyField(Event, null=True)
    task = ForeignKeyField(Task, null=True)


class Notification(ModelBase):
    event = ForeignKeyField(Event, null=True)
    task = ForeignKeyField(Task, null=True)
    date = DateTimeField()


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