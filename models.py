from peewee import Model, SqliteDatabase, CharField, ForeignKeyField, DateTimeField
from utils import EnumField, STATUS, PRIORITY


DATABASE = 'todoapp.db'
db_connection = SqliteDatabase(DATABASE)


class Database():

    def __init__(self, connectionstring):
        pass
        #database = SqliteDatabase(DATABASE)

    @staticmethod
    def create_tables():
        with db_connection:
            db_connection.create_tables([Folder, Task, Group,
                                         Event, User, UserToGroups,
                                         FolderTaskEvents])

    @staticmethod
    def set_up_connection():
        db_connection.connect(reuse_if_open=True)


class ModelBase(Model):
    class Meta:
        database = db_connection


class User(ModelBase):

    username = CharField(unique=True)
    password_hash = None
    password_salt = None
    email = CharField(unique=True)


class Folder(ModelBase):

    name = CharField(unique='True')
    owner = ForeignKeyField(User, backref='folders')


class Group(ModelBase):

    name = CharField()
    owner = ForeignKeyField(User, backref='groups')


class Event(ModelBase):

    name = CharField()
    owner = ForeignKeyField(User, backref='events')


class Task(ModelBase):

    name = CharField()
    description = CharField()
    owner = ForeignKeyField(User, backref='tasks')
    parent_task = ForeignKeyField('self', null=True)
    group = ForeignKeyField(Group, null=True)
    status = EnumField(STATUS)
    assigned = ForeignKeyField(User, null=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
    priority = EnumField(PRIORITY)


class Cyclicity(ModelBase):

    period = DateTimeField()
    duration = DateTimeField()
    event = ForeignKeyField(Event, null=True)
    task = ForeignKeyField(Task, null=True)


class Notification(ModelBase):

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

