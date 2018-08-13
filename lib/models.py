from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Table,
    Enum,
    Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import enum
import datetime


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
# user_group_association_table = Table(
#     'user_groups', Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id')),
#     Column('group_id', Integer, ForeignKey('groups.id'))
# )
#

#
#
#
# class TaskUserEditors(Base):
#     __tablename__ = 'task_users_editors'
#     id = Column(Integer, primary_key=True)
#     user = Column(Integer, ForeignKey('users.id'))
#     task = Column(Integer, ForeignKey('tasks.id'))
#
#
# class TaskUserObservers(Base):
#     __tablename__ = 'task_users_observers'
#     id = Column(Integer, primary_key=True)
#     user = Column(Integer, ForeignKey('users.id'))
#     task = Column(Integer, ForeignKey('tasks.id'))


user_task_observer_association_table = Table(
    'task_users_observers', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('task_id', Integer, ForeignKey('tasks.id'))
)

user_task_editors_association_table = Table(
    'task_users_editors', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('task_id', Integer, ForeignKey('tasks.id'))
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

    # folders = relationship('Folder', back_populates='user')
    # managed_groups = relationship('Group', back_populates='owner')
    # tasks = relationship('Task', back_populates='owner')

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return self.username


class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    name = Column(String)
    tasks = relationship('Task', secondary=task_folder_association_table)

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __str__(self):
        return self.name


# due to add of user rights this model dont need anymore
# class Group(Base):
#     pass
    # __tablename__ = 'groups'
    # id = Column(Integer, primary_key=True)
    # user_id = Column(Integer, ForeignKey('users.id'))
    # name = Column(String)
    #
    # def __init__(self, name, user_id):
    #     self.name = name
    #     self.user_id = user_id


class Freezable:
    ...
#     def __new__(cls, *args, frozen=False, **kwargs):
#         obj = super().__new__(cls, *args, **kwargs)
#         super().__setattr__(obj, '_frozen', frozen)
#         return obj
#
#     def __setattr__(self, name, value):
#         if self._frozen:
#             raise TypeError(f'Frozen {type(self).__name__} do not support assignment')
#         super().__setattr__(name, value)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    name = Column(String)
    description = Column(String)
    # group = Column(Integer, ForeignKey('groups.id'), nullable=True)

    priority = Column(Enum(TaskPriority), default=TaskPriority.NONE,
                      nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.CREATED,
                    nullable=False)

    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)

    owner = relationship('User', foreign_keys=user_id)
    assigned = relationship('User', foreign_keys=assigned_id)

    observers = relationship('User',
                             secondary='task_users_observers')
    editors = relationship('User',
                           secondary='task_users_editors')
    # folders = relationship(
    #     'Folder',
    #     secondary=task_folder_association_table,
    #     back_populates='tasks'
    # )

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
    MIN = 'Min'
    HOUR = 'Hour'
    DAY = 'Day'
    WEEK = 'Week'
    MONTH = 'Month'
    YEAR = 'Year'


class EndType(enum.Enum):
    NEVER = 'Never'
    AMOUNT = 'Amount'
    DATE = 'Date'


class Repeat(Base):
    __tablename__ = 'repeats'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    task = relationship('Task', back_populates='repeat')

    period = Column(Enum(Period))
    period_amount = Column(Integer)
    end_type = Column(Enum(EndType))
    repetitions_amount = Column(Integer, nullable=False, default=0)
    repetitions_count = Column(Integer, nullable=False, default=0)
    last_activated = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    # interval = Column(DateTime)

    def __init__(self, user_id, task_id,
                 period, period_amount,
                 end_type,
                 repetitions_amount,
                 end_date, start_date):
        self.user_id = user_id
        self.task_id = task_id
        self.period = period
        self.period_amount = period_amount
        self.end_type = end_type
        self.repetitions_amount = repetitions_amount
        self.end_date = end_date
        self.start_date = start_date
        self.last_activated = self.start_date
        # self.interval = interval

    def __str__(self):
        return (f'''
                        user_id : {self.user_id}
                        task_id: {self.task_id}
                        period: {self.period.value}
                        period_amount: {self.period_amount}
                        end_type: {self.end_type.value}
                        repetitions_amount: {self.repetitions_amount}
                        repetitions count: {self.repetitions_amount}
                        start date: {self.start_date}
                        end date: {self.end_date}
                        last activated: {self.last_activated}
                ''')


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
