from utils import EnumField, STATUS, PRIORITY
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import  create_engine

Base = declarative_base()
DATABASE = 'todoapp.db'
#db_connection = SqliteDatabase(DATABASE)


class Database():

    def __init__(self, connectionstring):
        self.session = sessionmaker(bind=create_engine())
        pass
        #database = SqliteDatabase(DATABASE)

    @staticmethod
    def set_up_connection():
        pass
        #db_connection.connect(reuse_if_open=True)


# link tables later
user_group_association_table = Table('user_groups', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('group_id', Integer, ForeignKey('group.id'))
)

task_folder_association_table = Table('task_folders', Base.metadata,
    Column('task_id', Integer, ForeignKey('task.id')),
    Column('folder_id', Integer, ForeignKey('folder.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    password_salt = Column(String)
    email = Column(String, unique=True)


class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))
    tasks = relationship(
        'Task',
        secondary=task_folder_association_table,
        back_populates='folder')


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))


# class Event(Base):
#     __tablename__ = 'events'
#     id = Column(Integer, primary_key=True)
#     name = Column()
#     owner = Column(Integer, ForeignKey('user.id'))


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))
    parent_task = Column(Integer, ForeignKey('tasks.id'))
    group = Column(Integer, ForeignKey('groups.id'))
    #status = EnumField(STATUS)
    assigned = Column(Integer, ForeignKey('users.id'))
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    folders = relationship(
        'Folder',
        secondary=task_folder_association_table,
        back_populates='tasks'
    )


class Cyclicity(Base):
    __tablename__ = 'cyclicities'
    id = Column(Integer, primary_key=True)
    period = Column(DateTime)
    duration = Column(DateTime)
    task = Column(Integer, ForeignKey('tasks.id'))
    #event = ForeignKeyField(Event, null=True)


# class Notification(Base):
#     __tablename__ = 'notifications'
#     id = Column(Integer, primary_key=True)
#     date = Column(DateTime)
#     task = Column(Integer, ForeignKey('task.id'))


#
# class Comment(ModelBase):
#     pass

