from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Table,
    Enum)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from datetime import datetime
import enum

Base = declarative_base()
DATABASE = 'todoapp.db'
HUMANIZE = '%Y-%m-%d %H:%M'


def set_up_connection(connection_string=None):
    engine = create_engine(f'sqlite:///todoapp.db')
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return session()


class TaskUserEditors(Base):
    __tablename__ = 'task_users_editors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    task_id = Column(Integer, ForeignKey('tasks.id'))


task_folder_association_table = Table(
    'task_folders', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('folder_id', Integer, ForeignKey('folders.id'))
)


class TaskStatus(enum.Enum):
    TODO = 'Todo'
    INWORK = 'In work'
    DONE = 'Done'
    ARCHIVED = 'Archived'


class TaskPriority(enum.Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'


class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    name = Column(String)
    tasks = relationship('Task', secondary=task_folder_association_table)

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __str__(self):
        return self.name

#
# class SubTaskRelation(Base):
#     __tablename__ = 'sub_tasks_relation'
#     id = Column(Integer, primary_key=True)
#     task_id = Column(Integer, ForeignKey('tasks.id'))
#     parent_task_id = Column(Integer, ForeignKey('tasks.id'))
#


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_id = Column(Integer, nullable=True)

    name = Column(String)
    description = Column(String)

    priority = Column(Enum(TaskPriority), default=TaskPriority.LOW,
                      nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO,
                    nullable=False)

    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created = Column(DateTime, nullable=False, default=datetime.now())
    updated = Column(DateTime, nullable=False, default=datetime.now())

    editors = relationship('TaskUserEditors')
    #
    # subtasks = relationship('Task',
    #                         secondary='sub_tasks_relation',
    #                         primaryjoin=SubTaskRelation.task_id == id,
    #                         secondaryjoin=SubTaskRelation.parent_task_id == id,
    #                         backref='children')

    #  uselist prop allows to set one to one relation
    plan = relationship("Plan", uselist=False, back_populates='task')

    def __init__(self, name, owner_id, description=None,
                 start_date=None, end_date=None,
                 priority=None, status=None, parent_task_id=None, assigned_id=None):
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.parent_task_id = parent_task_id
        self.assigned_id = assigned_id
        self.priority = priority
        self.status = status

    def __str__(self):
        created = self.created.strftime(HUMANIZE)
        updated = self.updated.strftime(HUMANIZE)
        if self.start_date:
            start_date = self.start_date.strftime(HUMANIZE)
        if self.end_date:
            end_date = self.end_date.strftime(HUMANIZE)
        return (
            f'\n'
            f'ID : {self.id}\n'
            f'Owner id: {self.owner_id}\n'
            f'Parent taskid: {self.parent_task_id}\n'
            f'Name: {self.name}\n'
            f'Description: {self.description}\n'
            f'Status: {self.status.value}\n'
            f'Priority: {self.priority.value}\n'
            f'Created: {created}\n'
            f'Updated: {updated}\n'
            f'Start Date: {start_date if self.start_date else None}\n'
            f'End Date: {end_date if self.end_date else None}\n'
            f'Assigned user id: {self.assigned_id}'
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


class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer)

    task = relationship('Task', back_populates='plan')

    period = Column(Enum(Period))
    period_amount = Column(Integer)
    end_type = Column(Enum(EndType))
    repetitions_amount = Column(Integer, nullable=False, default=0)
    repetitions_counter = Column(Integer, nullable=False, default=0)
    last_activated = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    def __init__(self, user_id, task_id,
                 period, period_amount,
                 end_type,
                 repetitions_amount,
                 end_date, start_date,
                 interval):
        self.user_id = user_id
        self.task_id = task_id
        self.period = period
        self.period_amount = period_amount
        self.end_type = end_type
        self.repetitions_amount = repetitions_amount
        self.end_date = end_date
        self.start_date = start_date
        self.last_activated = self.start_date
        #self.interval = self.interval

    def __str__(self):
        if self.end_date:
            end_date = self.end_date.strftime(HUMANIZE)
        start_date = self.start_date.strftime(HUMANIZE)
        last_activated = self.last_activated.strftime(HUMANIZE)
        return (f'\n'
                f'ID: {self.id}\n'
                f'Owner ID: {self.user_id}\n'
                f'Task ID: {self.task_id}\n'
                f'Period: {self.period.value}\n'
                f'Period amount: {self.period_amount}\n'
                f'End type: {self.end_type.value}\n'
                f'Repetitions_amount: {self.repetitions_amount}\n'
                f'Repetitions count: {self.repetitions_amount}\n'
                f'Start date: {start_date if self.start_date else None}\n'
                f'End date: {end_date if self.end_date else None}\n'
                f'Last activated: {last_activated if self.last_activated else None}\n'
                f'')
