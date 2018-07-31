from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Table,
    Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import enum

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
        # db_connection.connect(reuse_if_open=True)


# link other tables later
user_group_association_table = Table(
    'user_groups', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

task_folder_association_table = Table(
    'task_folders', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('folder_id', Integer, ForeignKey('folders.id'))
)


class TaskStatus(enum.Enum):
    CREATED = 'Created'
    WORK = 'Work'
    DONE = 'Done'
    ARCHIVED = 'Archived'
    OVERDUE = 'Overdue'


class TaskPriority(enum.Enum):
    NONE = 'None'
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True)
    password_hash = Column(String)
    password_salt = Column(String)
    email = Column(String, unique=True)

    # folders = relationship('Folder', back_populates='owner')
    # managed_groups = relationship('Group', back_populates='owner')
    # tasks = relationship('Task', back_populates='owner')

    def __init__(self, username, email):
        self.username = username
        self.email = email


class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    name = Column(String)
    user = relationship('User', back_populates='folders')
    # tasks = relationship(
    #     'Task',
    #     secondary=task_folder_association_table,
    #     back_populates='folders')

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    name = Column(String)
    owner = relationship('User', foreign_keys=[user_id],
                         back_populates='managed_groups')

    # add members later

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    name = Column(String)
    description = Column(String)
    group = Column(Integer, ForeignKey('groups.id'), nullable=True)

    priority = Column(Enum(TaskPriority), default=TaskPriority.NONE)
    status = Column(Enum(TaskStatus, default=TaskStatus.CREATED))

    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)

    owner = relationship('User', foreign_keys=user_id)
    assigned = relationship('User', foreign_keys=assigned_id)

    folders = relationship(
        'Folder',
        secondary=task_folder_association_table,
        back_populates='tasks'
    )

    notifications = relationship('Notification', back_populates='task')

    #  uselist prop allows to set one to one relation
    repeat = relationship("Repeat", uselist=False, back_populates='task')

    def __init__(self, name, user_id, description,
                 start_date, end_date,
                 priority, parent_task_id,
                 group_id, assigned_id):
        self.name = name
        self.user_id = user_id
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.parent_task_id = parent_task_id
        self.assigned_id = assigned_id
        self.group_id = group_id
        self.priority = priority

    def __str__(self):
        return (
            f'''
                ID : {self.id}
                Name: {self.name}
                Owner: {self.owner.username}
                Description: {self.description}
                Status: {self.status.value}
                Priority: {self.priority.value}
                Start Date: {self.start_date}
                End Date: {self.end_date}
            '''
        )


class Period(enum.Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class Repeat(Base):
    __tablename__ = 'repeats'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))

    period = Column(Enum(Period))
    duration = Column(DateTime)
    task = relationship('Task', back_populates='repeat')

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

    def __str__(self):
        return (
            f'''
                ID : {self.id}
                Date: {self.date}
                Task: {self.task_id}
            '''
        )

#
# class Comment(Base):
#     pass
