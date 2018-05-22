from utils import STATUS, PRIORITY
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


class Database:

    def __init__(self, connectionstring):
        pass

    @staticmethod
    def set_up_connection():
        engine = create_engine('sqlite:///todoapp.db')
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        return session()
        #db_connection.connect(reuse_if_open=True)


# link other tables later
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

    folders = relationship('Folder', back_populates='owner')
    managed_groups = relationship('Group', back_populates='owner')

    def __init__(self, username, email):
        self.username = username
        self.email = email


class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    name = Column(String)

    owner = relationship('User', back_populates='folders')
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
    owner_id = Column(Integer, ForeignKey('users.id'))

    name = Column(String)
    owner = relationship('User', foreign_keys=[owner_id],
                         back_populates='managed_groups')

    # add members later

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    name = Column(String)
    description = Column(String)
    group = Column(Integer, ForeignKey('groups.id'), nullable=True)
    #status = EnumField(STATUS) # fix
    start_date = Column(DateTime)

    end_date = Column(DateTime, nullable=True)
    owner = relationship('User', foreign_keys=owner_id)
    assigned = relationship('User', foreign_keys=assigned_id)

    folders = relationship(
        'Folder',
        secondary=task_folder_association_table,
        back_populates='tasks'
    )
    notifications = relationship('Notification', back_populates='task')

    #  uselist param allows to set one to one relation
    cyclicity = relationship("Cyclicity", uselist=False, back_populates='task')

    def __init__(self, name, owner, description,
                 start_date, end_date,
                 parent_task, group, assigned):
        self.name = name
        self.owner = owner
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.parent_task = parent_task
        self.assigned = assigned
        self.group = group


# rename class and fix in readme
class Cyclicity(Base):
    __tablename__ = 'cyclicities'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))

    period = Column(DateTime)
    duration = Column(DateTime)
    task = relationship('Task', back_populates='task')

    def __init__(self, task, period, duration):
        self.period = period
        self.duration = duration
        self.task = task


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', back_populates='notifications')

    def __init__(self, task, date):
        self.task = task
        self.date = date

#
# class Comment(ModelBase):
#     pass

