from utils import EnumField, STATUS, PRIORITY
from datetime import datetime
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
        pass
        Session = sessionmaker(bind=create_engine('sqlite:///todoapp.db'))
        self.session = Session()
        #database = SqliteDatabase(DATABASE)

    @staticmethod
    def set_up_connection():
        engine = create_engine('sqlite:///todoapp.db')
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        return Session()
        #db_connection.connect(reuse_if_open=True)


# link tables later
user_group_association_table = Table('user_groups', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

task_folder_association_table = Table('task_folders', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('folder_id', Integer, ForeignKey('folders.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    password_salt = Column(String)
    email = Column(String, unique=True)

    folders = relationship('Folder')
    tasks = relationship('Task')

    def __init__(self, username, email):
        self.username = username
        self.email = email


class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))
    tasks = relationship(
        'Task',
        secondary=task_folder_association_table,
        back_populates='folders')

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner




class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

# class Event(Base):
#     __tablename__ = 'events'
#     id = Column(Integer, primary_key=True)
#     name = Column()
#     owner = Column(Integer, ForeignKey('users.id'))


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    owner = Column(Integer, ForeignKey('users.id'))
    parent_task = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    group = Column(Integer, ForeignKey('groups.id'), nullable=True)
    #status = EnumField(STATUS) # fix
    #assigned = Column(Integer, ForeignKey('users.id'), nullable=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)

    folders = relationship(
        'Folder',
        secondary=task_folder_association_table,
        back_populates='tasks'
    )

    def __init__(self, name, owner, description,
                 start_date, end_date,
                 parent_task, group):
        self.name = name
        self.owner = owner
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.parent_task = parent_task
        #self.assigned = assigned
        self.group = group


class Cyclicity(Base):
    __tablename__ = 'cyclicities'
    id = Column(Integer, primary_key=True)
    period = Column(DateTime)
    duration = Column(DateTime)
    task = Column(Integer, ForeignKey('tasks.id'))

    def __init__(self, period, duration, task):
        self.period = period
        self.duration = duration
        self.task = task

    #event = ForeignKeyField(Event, null=True)


# class Notification(Base):
#     __tablename__ = 'notifications'
#     id = Column(Integer, primary_key=True)
#     date = Column(DateTime)
#     task = Column(Integer, ForeignKey('tasks.id'))


#
# class Comment(ModelBase):
#     pass

