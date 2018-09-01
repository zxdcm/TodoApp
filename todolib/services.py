from sqlalchemy import (orm,
                        exc)
from typing import List
from warnings import warn
from datetime import datetime

from todolib.models import (
    Task,
    Folder,
    Plan,
    TaskPriority,
    TaskStatus,
    Period,
    EndType,
    task_folder_association_table,
    TaskUserRelation,
    Reminder)
from todolib.exceptions import (ObjectNotFound,
                                RedundancyAction)
from todolib.utils import (get_end_type,
                           get_interval,
                           check_object_exist,
                           enum_converter)

from todolib.validators import (validate_task_dates,
                                validate_plan_end_date,
                                validate_reminder_date)
from todolib.logging import get_logger, log_decorator

logger = get_logger()


class AppService:
    """
    Class that includes CRUD (create, read, update, delete)
    and common used methods on lib objects
    Methods contains type and logic validators
    Methods might raise exceptions or warnings.
    ----------
    session : session object that provides interface to database
    Attributes
    ----------
    session

    Methods:
        Tasks actions
        -------------
        add_subtask - attach task with task_id as subtask of task with parent_task_id
        assign_user - assign user as task executor
        change_task_status - simply change task status
        _change_subtasks_status - change subtasks status recursively. Calls by change_task_status method
        create_folder - create new folder and add to storage
        create_plan - create new plan and add to storage
        create_reminder - create new reminder and add to storage
        create_task - create new task and add to storage
        delete task - remove task and its related objects from storage
        delete_folder - delete folder from storage
        delete_obj - delete object
        delete_plan - delete plan from storage
        delete_reminder - delete reminder from storage
        detach_task - detach task with task_id from its parent_task
        get_active_plans - passes through plans and retrive active plans
        get_all_plans - retrive plans user can access
        get_all_reminders - retrive all user reminders from storage
        get_all_folders - retrieve all user folders
        get_available_tasks - retrieve tasks user can access
        get_filtered_tasks - retrieve filtered tasks
        get_folder - retrieve folder
        get_folder_by_name - retreive folder by its name
        get_generated_tasks_by_plan - retrive tasks created by plan
        get_obj - get any object from storage by cls and id
        get_own_plans - retrive plans created by user
        get_own_tasks - retrieve tasks created by user
        get_plan - retrive plan
        get_reminder -  retrive reminder from storage
        get_subtasks - retrieve task subtasks
        get_task - retrieve task from storage
        get_task_by_name - retrieve case insensitive task by name matching
        get_task_reminders - retrive task reminders from storage for specific user
        get_task_user_relation - get relation between user and task
        get_user_assigned_tasks - return tasks user assignd as executor on
        populate_folder - add task in folder
        save_updates - save updates made out of the lib
        share_task - share task with user
        unpopulate_folder - remove task from folder
        unshare_task - unshare task with user
        update_folder - update folder info
        update_reminder - update reminder info
        update_task - update task info

    """

    @log_decorator
    def __init__(self, session):
        self.session = session

    @log_decorator
    def get_task_user_relation(self,
                               user,
                               task_id):
        """Method allows to get TaskUserRelation relation object.
           That indicates does the user has rights to access the task
        Parameters
        ----------
        user : str
        task_id : int
        Returns
        -------
        TaskUserRelation object or None
        """
        return self.session.query(TaskUserRelation).filter_by(
            user=user, task_id=task_id).one_or_none()

    @log_decorator
    def create_task(self,
                    user,
                    name,
                    status='todo',
                    priority='low',
                    start_date=datetime.now(),
                    event=False,
                    description=None,
                    end_date=None,
                    parent_task_id=None,
                    assigned=None,
                    ) -> Task:
        """Method allows to create task instance with provided arguments.
        Parameters
        ----------
        user : str
        name : str
        status : str
        priority : str
        start_date : datetime
        description : str
        end_date : datetime
        parent_task_id : int
        assigned : str : assigned user username
        Returns
        -------
        Task object or Exception
        """

        if priority:
            priority = enum_converter(priority, TaskPriority, 'Priority')

        if status:
            status = enum_converter(status, TaskStatus, 'Status')

        if parent_task_id:
            parent_task = self.get_task(user=user, task_id=parent_task_id)
            if parent_task.plan:
                raise ValueError('Task with plan cant have directly added subtasks')

        validate_task_dates(start_date, end_date)

        task = Task(owner=user,
                    name=name,
                    description=description,
                    start_date=start_date,
                    priority=priority,
                    end_date=end_date,
                    parent_task_id=parent_task_id,
                    assigned=assigned,
                    event=event,
                    status=status)

        task.members.append(TaskUserRelation(user=user,
                                             task_id=task.id))

        if assigned and assigned is not user:
            task.members.append(TaskUserRelation(user=assigned,
                                                 task_id=task.id))

        self.session.add(task)
        self.session.commit()
        logger.info(f'Task ID({task.id}) created by User({user})')
        return task

    @log_decorator
    def get_task(self,
                 user: str,
                 task_id: int) -> Task:
        """Allows to get task object .
        Parameters
        ----------
        user : str
        task_id : int
        Returns
        -------
        Task
        """
        task = self.session.query(Task).join(TaskUserRelation).filter(
            TaskUserRelation.user == user, Task.id == task_id).one_or_none()
        check_object_exist(task, f'ID {task_id}', 'Task')
        return task

    @log_decorator
    def update_task(self,
                    user: str,
                    task_id: int,
                    name=None,
                    description=None,
                    status=None,
                    priority=None,
                    end_date=None,
                    start_date=None,
                    event=None) -> Task:

        task = self.get_task(user, task_id)

        args = {}

        if name:
            args[Task.name] = name

        if description:
            args[Task.description] = description

        if status:
            status = enum_converter(status, TaskStatus, 'Status')
            args[Task.status] = status

        if priority:
            priority = enum_converter(priority, TaskPriority, 'Priority')
            args[Task.priority] = priority

        if event is not None:
            args[Task.event] = event

        if start_date or end_date:
            if start_date is None:
                start_date = task.start_date
            elif end_date is None:
                end_date = task.end_date
            validate_task_dates(start_date, end_date)
            args[Task.start_date] = start_date
            args[Task.end_date] = end_date

        args[Task.updated] = datetime.now()

        self.session.query(Task).filter_by(id=task_id).update(args)
        self.session.commit()

        logger.info(f'Task ID({task.id}) updated by User({user})')
        return task

    @log_decorator
    def assign_user(self, user: str,
                    task_id: int,
                    user_receiver: str):
        """Assign user as task executor.
        Parameters
        ----------
        user : str : user who assign receiver
        task_id : int
        user_receiver : str user who become task executor
        Returns
        -------
        None or Exception
        """
        task = self.get_task(user=user, task_id=task_id)

        if task.assigned == user_receiver:
            warn(
                'User already assigned as task executor',
                RedundancyAction)
            return

        rel = self.get_task_user_relation(user=user_receiver,
                                             task_id=task_id)

        if rel is None:
            rel = TaskUserRelation(user=user_receiver, task_id=task_id)
            task.members.append(rel)

        task.assigned = user_receiver

        self.session.commit()

        logger.info(f'User({user}) assigned as task(id={task.id}) executor')

    @log_decorator
    def share_task(self,
                   user: str,
                   task_id: int,
                   user_receiver: str):
        """Share access rights to task with particular user.
        Parameters
        ----------
        user : str
        task_id : int
        user_receiver : str
        Returns
        -------
        None or Exception
        """

        self.get_task(user=user, task_id=task_id)

        relation = self.get_task_user_relation(user=user_receiver,
                                               task_id=task_id)
        if relation:
            warn(f'Task already shared with user',
                 RedundancyAction)

        self.session.add(TaskUserRelation(user=user_receiver,
                                          task_id=task_id))

        self.session.commit()

        logger.info(f'Task ID({task_id}) shared with User({user_receiver})')

    @log_decorator
    def unshare_task(self,
                     user: str,
                     task_id: int,
                     user_receiver: str):
        """Unshare access rights with particular user.
        Parameters
        ----------
        user : str : user who unshare task
        task_id : int
        user_receiver : str : user that will lose access rights
        Returns
        -------
        None or Exception
        """

        task = self.get_task(user=user,
                             task_id=task_id)

        if user_receiver == task.owner:
            raise ValueError(f'User cant unshare task with its owner')

        relation = self.get_task_user_relation(user=user_receiver,
                                               task_id=task_id)
        if relation is None:
            raise ValueError(f'Task wasnt shared with this user')

        if user_receiver == task.assigned:
            task.assigned = None

        self.session.delete(relation)
        self.session.commit()

        logger.info(f'Task ID({task_id}) unshared with User({user_receiver})')

    @log_decorator
    def get_own_tasks(self, user: str) -> List[Task]:
        """Method allows to get all tasks created by user.
        Parameters
        ----------
        user : str
        Returns
        -------
        List[Task] List of Tasks
        """
        return self.session.query(Task).filter_by(owner=user).all()

    @log_decorator
    def get_user_assigned_tasks(self, user: str) -> List[Task]:
        return self.session.query(Task).filter_by(assigned=user).all()

    @log_decorator
    def get_available_tasks(self, user: str) -> List[Task]:
        """Method allows to get all tasks user can access.
        Returns
        -------
        List[Task]
        """
        return (self.session.query(Task)
                .join(TaskUserRelation)
                .filter_by(user=user)
                .all())

    def get_filtered_tasks(self,
                           user: str,
                           name=None,
                           description=None,
                           parent_task_id=None,
                           status=None,
                           start_date=None,
                           end_date=None,
                           priority=None,
                           event=None) -> List[Task]:
        """Method allow to tasks filtered by params
           start_date - from
           end_date -  till to
        Parameters
        ----------
        user : str
        name : str
        description : str
        parent_task_id : int
        status : str or TaskStatus object
        start_date : datetime : start from date
        end_date : datetime : end date till
        priority : str or TaskPriority object
        event : Bool
        Returns
        -------
        List[Task]
        """
        query = self.session.query(Task)

        if name:
            query = query.filter(Task.name.ilike(f'{name}'))
        if description:
            query = query.filter(Task.description.ilike(f'{description}'))

        if priority:
            if isinstance(priority, str):
                priority = enum_converter(priority, TaskPriority, 'Priority')
            query = query.filter(Task.priority == priority)
        if status:
            if isinstance(status, str):
                status = enum_converter(status, TaskStatus, 'Status')
            query = query.filter(Task.status == status)

        if start_date:
            query = query.filter(Task.start_date > start_date)
        if end_date:
            query = query.filter(Task.end_date < end_date)
        if event is not None:
            query = query.filter(Task.event == event)

        return (query.join(TaskUserRelation)
                .filter(TaskUserRelation.user == user)
                .all())

    def get_tasks_by_name(self, user: str, name) -> List[Task]:
        """Case insensitive search by name matching.
        Parameters
        ----------
        user : str
        name : str
        Returns
        -------
        List[Task]
        """
        return (self.session.query(Task)
                .join(TaskUserRelation).filter(TaskUserRelation.user == user)
                .filter(Task.name.ilike(f'%{name}%')).all())

    @log_decorator
    def delete_task(self,
                    user: str,
                    task_id: int):
        """Delete task
        Parameters
        ----------
        user : str : user who delete task
        task_id : int
        Returns
        -------
        None or Exception
        """
        task = self.get_task(user=user, task_id=task_id)

        if task.plan:
            self.session.delete(task.plan)
        for rel in task.members:
            self.session.delete(rel)
        for folder in self.get_task_folders(task_id=task.id):
            folder.tasks.remove(task)
        for reminder in task.reminders:
            self.session.delete(reminder)

        self.session.delete(task)
        self.session.commit()

        logger.info(f'User({user}) deleted task ID({task_id})')

    @log_decorator
    def add_subtask(self,
                    user: str,
                    task_id: int,
                    parent_task_id: int):
        """Add task as the subtask of task with parent_task_id.
        Parameters
        ----------
        user : str
        task_id : int
        parent_task_id : int
        Returns
        -------
        None or Exception
        """
        parent_task = self.get_task(user=user, task_id=parent_task_id)
        subtask = self.get_task(user=user, task_id=task_id)

        if parent_task.plan:
            raise ValueError('Task with plan cant have directly added subtasks')

        if parent_task.parent_task_id == task_id:
            raise ValueError('Loop dependecy error. You cant add parent task as subtask')

        if subtask.parent_task_id:
            raise ValueError('Task already have parent task')

        if task_id == parent_task_id:
            raise ValueError('You cant attach task to itself')

        subtask.parent_task_id = parent_task_id

        self.session.commit()

        logger.info(
            f'User({user}) added Task(ID{task_id}) as the subtask of Task ID({parent_task_id})')

    @log_decorator
    def detach_task(self, user: str, task_id: int):
        """Remove relation between task with task_id and its parent task.
        Parameters
        ----------
        user : str
        task_id : int
        Returns
        -------
        None or Exception
        """
        subtask = self.get_task(user=user, task_id=task_id)

        if subtask.parent_task_id is None:
            raise ValueError('Task dont have parent task')
        else:
            subtask.parent_task_id = None

        self.session.commit()

        logger.info(
            f'User({user}) removed Task(ID{task_id}) from subtasks of Task ID({subtask.parent_task_id})')

    @log_decorator
    def get_subtasks(self, user: str, task_id: int):
        """Allows to get task subtasks.
        Parameters
        ----------
        user : str
        task_id : int
        Returns
        -------
        Task[List] or Exception
        """

        task = self.get_task(user=user, task_id=task_id)

        return self.session.query(Task).filter_by(
            parent_task_id=task_id).join(
                TaskUserRelation).filter_by(user=user).all()

    def _change_subtasks_status(self,
                                user: str,
                                task_id: int,
                                status: TaskStatus):
        """Inner method that allow to change tasks status.
           Dont call this explicit or call save_updates to commit changes
        Parameters
        ----------
        user : str
        task_id : int
        status : TaskStatus
        Returns
        -------
        """
        task = self.get_task(user, task_id)
        for subtask in task.subtasks:
            subtask.status = status
            subtask.updated = datetime.now()
            self._change_subtasks_status(user=user,
                                         task_id=subtask.id,
                                         status=status)

    @log_decorator
    def change_task_status(self,
                           user: str,
                           task_id: int,
                           status: str,
                           apply_on_subtasks=False):
        """Method changes task and its subtasks(depends on status or
        apply_on_subtasks argument) status
        Parameters
        ----------
        user : str
        task_id : int
        status : str
        apply_on_subtasks : Bool
        Returns
        -------
        Task
        """

        task = self.get_task(user=user, task_id=task_id)

        status = enum_converter(status, TaskStatus, 'Status')
        task.status = status
        task.updated = datetime.now()

        if (task.status is TaskStatus.DONE or apply_on_subtasks):
            self._change_subtasks_status(user=user,
                                         task_id=task_id,
                                         status=status)

        self.session.commit()

        logger.info(
            f'User({user}) has changed Task(ID{task_id}) status to {task.status.value})')

    @log_decorator
    def create_folder(self, user: str, name: str) -> Folder:
        """Allow create folder with provided name for user
        Parameters
        ----------
        user: str
        name : str
        Returns
        -------
        Folder
        """

        folder = Folder(user=user, name=name)

        self.session.add(folder)
        self.session.commit()

        logger.info(f'Folder ID({folder.id}) created by User({user})')

        return folder

    @log_decorator
    def get_folder(self, user: str, folder_id: int) -> Folder:
        folder = self.session.query(Folder).filter_by(
            id=folder_id, user=user).one_or_none()
        check_object_exist(folder,
                           f'id : {folder_id}',
                           'Folder')

        return folder

    @log_decorator
    def get_folder_by_name(self, user: str, name: str) -> Folder:
        return self.session.query(Folder).filter_by(
            name=name, user=user).one_or_none()

    @log_decorator
    def get_all_folders(self, user: str) -> List[Folder]:
        return self.session.query(Folder).filter_by(user=user).all()

    @log_decorator
    def update_folder(self, user: str, folder_id: int, name):
        folder = self.get_folder(user=user, folder_id=folder_id)

        folder.name = name

        self.session.commit()

        logger.info(f'Folder ID({folder.id}) updated by User({user})')
        return folder

    @log_decorator
    def delete_folder(self, user: str, folder_id: int):
        folder = self.get_folder(user, folder_id)

        for task in folder.tasks:
            folder.tasks.remove(task)

        self.session.delete(folder)
        self.session.commit()

        logger.info(
            f'Folder ID({folder_id}) deleted by User({user})')

    @log_decorator
    def get_task_folders(self, task_id, user=None):
        query = self.session.query(Folder)
        if user:
            query = query.filter_by(user=user)
        return (query.join(task_folder_association_table).filter_by(task_id=task_id)).all()

    @log_decorator
    def populate_folder(self, user: str, folder_id: int, task_id: int):
        """Method allows to add task in folder.
        Parameters
        ----------
        user : str
        folder_id : int
        task_id : int
        Returns
        -------
        """
        folder = self.get_folder(user, folder_id)
        task = self.get_task(user, task_id)
        if task in folder.tasks:
            warn(f'Folder already have this task',
                 RedundancyAction)
            return

        folder.tasks.append(task)

        self.session.commit()

        logger.info(
            f'Folder ID({task_id}) populated with Task({task_id}) by User({user})')

    @log_decorator
    def unpopulate_folder(self,
                          user: str,
                          folder_id: int,
                          task_id: int):
        """Method removes task from folder.
        Parameters
        ----------
        user : str
        folder_id : int
        task_id : int
        Returns
        -------
        """
        folder = self.get_folder(user, folder_id)
        task = self.get_task(user, task_id)
        if task not in folder.tasks:
            raise ValueError(f'Folder dont have this task')

        folder.tasks.remove(task)

        self.session.commit()

        logger.info(
            f'Task({task_id}) removed from Folder ID({task.id}) by User({user})')

    @log_decorator
    def create_plan(self, user: str, task_id: int,
                    period_amount: int,
                    period: str,
                    start_date=datetime.now(),
                    repetitions_amount=None,
                    end_date=None) -> Plan:
        """Method allows to create plan for specific task
        Parameters
        ----------
        user : str
        task_id : int
        period_amount :
        period :
        repetitions_amount : int
        start_date : datetime
        end_date : datetime
        Returns
        -------
        Plan
        """
        task = self.get_task(user=user, task_id=task_id)

        if task.subtasks:
            raise ValueError('Task should be without subtasks')
        if task.plan:
            raise ValueError('Task already has a plan')

        if end_date:
            validate_plan_end_date(end_date)

        if start_date is None:
            start_date = datetime.now()
        if period:
            period = enum_converter(period, Period, 'Period')

        end_type = get_end_type(start_date, period, period_amount,
                                end_date, repetitions_amount)

        plan = Plan(user=user,
                    task_id=task_id,
                    period=period,
                    period_amount=period_amount,
                    end_type=end_type,
                    repetitions_amount=repetitions_amount,
                    end_date=end_date,
                    start_date=start_date)

        self.session.add(plan)
        self.session.commit()

        logger.info(f'Plan({plan.id}) created by User({user})')

        return plan

    @log_decorator
    def get_plan(self, user: str, plan_id: int) -> Plan:

        plan = self.session.query(Plan).get(plan_id)
        check_object_exist(plan, plan_id, 'Plan')
        try:
            self.get_task(user, plan.task_id)
        except ObjectNotFound as e:
            raise ObjectNotFound(
                f'Plan with id : {plan_id} not found') from e
        return plan

    @log_decorator
    def get_all_plans(self, user: str) -> List[Plan]:
        return self.session.query(Plan).join(Task).join(
            TaskUserRelation).filter(
            TaskUserRelation.user == user).all()

    @log_decorator
    def get_own_plans(self, user: str) ->Plan:
        return self.session.query(Plan).filter_by(user=user).all()

    @log_decorator
    def get_generated_tasks_by_plan(self, user: str,
                                    plan_id: int) -> List[Task]:
        """Return all tasks created by Plan
        ----------
        user : str
        plan_id : int
        Returns
        -------
        List[Task]
        """
        plan = self.get_plan(user=user, plan_id=plan_id)
        return self.session.query(Task).filter(
            Task.parent_task_id == plan.task_id).join(TaskUserRelation).all()

    @log_decorator
    def get_active_plans(self, user: str, plans=None) -> List[Plan]:
        """Method allows to get active plans.
        Parameters
        ----------
        user : str
        plans* : List[Plan] list of plans from which to get activeplans
        Returns
        -------
        List[Plan]
        """
        if plans is None:
            plans = self.get_all_plans(user)

        active_list = []

        for plan in plans:

            interval = get_interval(plan.period, plan.period_amount)
            near_activation = plan.last_activated + interval

            if plan.end_type == EndType.AMOUNT:
                if (near_activation < datetime.now() and
                        plan.repetitions_counter < plan.repetitions_amount):
                    active_list.append(plan)

            elif plan.end_type == EndType.DATE:
                if (near_activation < datetime.now() and
                        near_activation < plan.end_date):
                    active_list.append(plan)

            elif near_activation < datetime.now():
                active_list.append(plan)

        return active_list

    @log_decorator
    def execute_plans(self, user: str, active_plans=None) -> List[Task]:
        """Method passes through active plans and create proper amount tasks
        Parameters
        ----------
        user : str
        active_plans* :
        Returns
        -------
        None
        """
        '''
       foreach plan:
          calculate interval according to period and period amount
          sum last_activation and interval and get near activation
          if near activation < current time
              if EndType == AMOUNT or EndType == DATE and we reached the goal:
                  we dont have to create any task. Plan rule is completed now
              otherwise
                we keep creating tasks on every activation + interval
                                            until we reach current time
            '''
        if active_plans is None:
            active_plans = self.get_active_plans(user)
        if not active_plans:
            return
        for plan in active_plans:
            interval = get_interval(plan.period, plan.period_amount)
            near_activation = plan.last_activated + interval

            while near_activation < datetime.now():

                if (plan.end_type == EndType.AMOUNT and
                        plan.repetitions_counter == plan.repetitions_amount):
                    break
                if (plan.end_type == EndType.DATE and
                        near_activation > plan.end_date):
                    break

                task = self.create_task(user=user,
                                        name=plan.task.name,
                                        description=plan.task.description,
                                        start_date=near_activation,
                                        event=plan.task.event,
                                        assigned=plan.task.assigned)

                task.parent_task_id = plan.task.id

                plan.last_activated = near_activation
                near_activation = plan.last_activated + interval
                plan.repetitions_counter += 1
                for x in plan.task.members:
                    if x.user != user and x.user != plan.task.assigned:
                        task.members.append(
                            TaskUserRelation(user=x.user,
                                             task_id=task.id))

                self.session.add(task)

        self.session.commit()

        logger.info(
            f'({len(active_plans)}) Plans were executed. Tasks related to plan created')

    @log_decorator
    def delete_plan(self, user: str, plan_id: int):
        plan = self.get_plan(user, plan_id)
        self.session.delete(plan)
        self.session.commit()

    @log_decorator
    def update_plan(self, user: str,
                    plan_id: int,
                    period=None,
                    period_amount=None,
                    repetitions_amount=None,
                    end_date=None) -> Plan:

        plan = self.get_plan(user=user, plan_id=plan_id)
        args = {}

        args[Plan.period] = plan.period
        args[Plan.period_amount] = plan.period_amount
        args[Plan.repetitions_amount] = plan.repetitions_amount
        args[Plan.end_date] = plan.end_date
        args[Plan.start_date] = plan.start_date

        if period:
            period = enum_converter(period, Period, 'Period')
            args[Plan.period] = period

        if period_amount:
            args[Plan.period_amount] = period_amount
        if repetitions_amount:
            args[Plan.repetitions_amount] = repetitions_amount
        if end_date:
            validate_plan_end_date(end_date)
            args[Plan.end_date] = end_date

        args[Plan.end_type] = get_end_type(plan.last_activated,
                                           args[Plan.period],
                                           args[Plan.period_amount],
                                           args[Plan.end_date],
                                           args[Plan.repetitions_amount])

        self.session.query(Plan).filter_by(id=plan_id).update(args)
        self.session.commit()

        logger.info(f'Plan({plan.id}) updated by User({user})')

        return self.session.query(Plan).get(plan_id)

    def create_reminder(self, user, task_id, date):

        task = self.get_task(user=user, task_id=task_id)

        validate_reminder_date(date)

        reminder = Reminder(task_id=task_id, date=date, user=user)

        self.session.add(reminder)
        self.session.commit()

        logger.info(f'Reminder({reminder.id}) created by User({user})')

        return reminder

    def get_reminder(self, user: str, reminder_id: int):
        reminder = self.session.query(Reminder).filter_by(user=user,
                                                          id=reminder_id).one_or_none()
        check_object_exist(reminder,
                           f'id : {reminder_id}',
                           'Reminder')
        return reminder

    def get_all_reminders(self, user: str):
        return self.session.query(Reminder).filter_by(user=user).all()

    def get_task_reminders(self, user: str, task_id: int):
        return self.session.query(Reminder).filter_by(user=user,
                                                      task_id=task_id).all()

    def update_reminder(self, user: str,
                        reminder_id: int,
                        task_id=None,
                        date=None):
        reminder = self.get_reminder(user, reminder_id)

        if date:
            validate_reminder_date(date)
            reminder.date = date

        self.session.commit()

        logger.info(f'Reminder({reminder.id}) updated by User({user})')

        return reminder

    def delete_reminder(self, user: str,
                        reminder_id: int):

        reminder = self.get_reminder(user, reminder_id)

        self.session.delete(reminder)
        self.session.commit()

        logger.info(f'Reminder({reminder.id}) deleted by User({user})')

    @log_decorator
    def get_obj(self, cls, id: int):
        """This method allows to get any object from the db without validation
           Use this only if you are confident what are you doing
           After work with object - commit changes via save_updates method
        Parameters
        ----------
        cls : Library type (type from models.py)
        id : int
            Object id
        Returns
        -------
        Model
            Model or None
        """
        return self.session.query(cls).get(id)

    @log_decorator
    def delete_obj(self, obj):
        self.session.delete(obj)
        self.session.commit()

    @log_decorator
    def save_updates(self):
        """Allow to commit updates made out of the lib.
        """
        self.session.commit()
