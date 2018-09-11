"""
    Module contains models used in library.
"""

from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Table,
    Boolean,
    Enum)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (relationship,
                            sessionmaker,
                            backref,
                            scoped_session)
from sqlalchemy import create_engine


FORMAT = '%Y-%m-%d %H:%M'
BaseModel = declarative_base()


def set_up_connection(driver_name, connection_string):
    """Allows to create session object.
    Parameters
    ----------
    driver_name: str
    connection_string: str
    Returns
    -------
    session object
    """
    engine = create_engine(f'{driver_name}:///{connection_string}',
                           connect_args={'check_same_thread': False})
    session = sessionmaker(bind=engine)
    BaseModel.metadata.create_all(engine)
    return scoped_session(session)


class TaskUserRelation(BaseModel):
    """
    Model that indicate user access to specific task
    """
    __tablename__ = 'task_users_relation'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.id'))


task_folder_association_table = Table(
    'task_folders', BaseModel.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('folder_id', Integer, ForeignKey('folders.id'))
)


class TaskStatus(enum.Enum):
    TODO = 'Todo'
    INWORK = 'InWork'
    DONE = 'Done'
    ARCHIVED = 'Archived'


class TaskPriority(enum.Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'


class Folder(BaseModel):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    user = Column(String)

    name = Column(String)
    tasks = relationship('Task', secondary=task_folder_association_table)

    def __init__(self, name, user):
        self.name = name
        self.user = user

    def __str__(self):
        return '\n'.join([f'id: {self.id}',
                          f'name: {self.name}',
                          f"tasks ids: {', '.join(str(task.id) for task in self.tasks)} "
                          ])


class Task(BaseModel):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    owner = Column(String)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned = Column(String, nullable=True)

    name = Column(String)
    description = Column(String)

    priority = Column(Enum(TaskPriority), default=TaskPriority.LOW,
                      nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO,
                    nullable=False)

    event = Column(Boolean, nullable=False, default=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created = Column(DateTime, nullable=False, default=datetime.now())
    updated = Column(DateTime, nullable=False, default=datetime.now())
    subtasks = relationship('Task', backref=backref('parent', remote_side='Task.id'))

    members = relationship('TaskUserRelation')

    #  uselist prop allows to set one to one relation
    plan = relationship('Plan', uselist=False, back_populates='task')
    reminders = relationship('Reminder', back_populates='task')

    def __init__(self,
                 name,
                 owner,
                 description=None,
                 start_date=None,
                 end_date=None,
                 priority=None,
                 status=None,
                 parent_task_id=None,
                 event=None,
                 assigned=None):
        self.name = name
        self.owner = owner
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.parent_task_id = parent_task_id
        self.assigned = assigned
        self.priority = priority
        self.status = status
        self.event = event

    def __str__(self):
        return(
            ''.join([
                f'id: {self.id}\n',
                f'name: {self.name}\n',
                f'owner: {self.owner}\n',
                f'parent task: {self.parent_task_id}\n' if self.parent_task_id else '',
                f'assigned user: {self.assigned}\n' if self.assigned else '',
                f'description: {self.description}\n' if self.description else '',
                f'status: {self.status.value}\n',
                f'priority: {self.priority.value}\n',
                f'event: {self.event}\n',
                f'users: {", ".join(rel.user for rel in self.members)}\n',
                f'start date: {self.start_date.strftime(FORMAT)}\n' if self.start_date else '',
                f'end date: {self.end_date.strftime(FORMAT)}\n' if self.end_date else '',
                f'created: {self.created.strftime(FORMAT)}\n',
                f'updated: {self.updated.strftime(FORMAT)}\n',
            ]))


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


class Plan(BaseModel):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user = Column(String)

    task = relationship('Task', back_populates='plan')

    period = Column(Enum(Period))
    period_amount = Column(Integer)
    end_type = Column(Enum(EndType))
    repetitions_amount = Column(Integer, nullable=False, default=0)
    repetitions_counter = Column(Integer, nullable=False, default=0)
    last_activated = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    def __init__(self,
                 user,
                 task_id,
                 period,
                 period_amount,
                 end_type,
                 repetitions_amount,
                 end_date,
                 start_date):
        self.user = user
        self.task_id = task_id
        self.period = period
        self.period_amount = period_amount
        self.end_type = end_type
        self.repetitions_amount = repetitions_amount
        self.end_date = end_date
        self.start_date = start_date
        self.last_activated = self.start_date

    def __str__(self):
        return (''.join([
            f'id: {self.id}\n',
            f'owner: {self.user}\n',
            f'task id: {self.task_id}\n',
            f'period: {self.period.value}\n',
            f'period amount: {self.period_amount}\n',
            f'end type: {self.end_type.value}\n',
            f'repetitions amount: {self.repetitions_amount}\n' if self.end_type == EndType.AMOUNT else '',
            f'repetitions counter: {self.repetitions_counter}\n' if self.end_type == EndType.AMOUNT else '',
            f'start date: {self.start_date.strftime(FORMAT)}\n' if self.start_date else '',
            f'end date: {self.end_date.strftime(FORMAT)}\n' if self.end_date else '',
        ]))


class Reminder(BaseModel):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task')
    user = Column(String)

    def __init__(self, user, task_id, date):
        self.user = user
        self.task_id = task_id
        self.date = date

    def __str__(self):
        return ('\n'.join([
            f'id: {self.id}',
            f'task id: {self.task_id}',
            f'date: {self.date}\n']))
