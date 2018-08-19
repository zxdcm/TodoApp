from lib.models import (
    Task,
    Folder,
    Plan,
    TaskPriority,
    TaskStatus,
    Period,
    EndType,
    task_folder_association_table,
    TaskUserEditors,
    set_up_connection)

from sqlalchemy import (orm,
                        exc,
                        or_)

from typing import List

from lib.exceptions import (AccessError,
                            UpdateError,
                            ObjectNotFound,
                            CreateError,
                            DuplicateRelation)

from lib.utils import (get_end_type,
                       get_interval,
                       check_object_exist)

from lib.validators import validate_task_dates, validate_plan_end_date
from datetime import datetime
from lib.logging import get_logger, log_decorator

Logger = get_logger()


class AppService:

    @log_decorator
    def __init__(self, connection_string):
        self.session = set_up_connection(connection_string)

    @log_decorator
    def get_task_user_relation(self,
                               user,
                               task_id):
        return self.session.query(TaskUserEditors).filter_by(
            user=user, task_id=task_id).one_or_none()

    @log_decorator
    def user_can_access_task(self,
                             user: str,
                             task_id: int):
        if self.get_task_user_relation(user=user, task_id=task_id):
            return True
        raise AccessError(
            f'User({user}) doesnt have permissions to task(ID={task_id})')

    @log_decorator
    def user_exist(self, user: str):
        user_tasks = self.session.query(
            TaskUserEditors).filter_by(user=user).all()
        if user_tasks:
            return True

    @log_decorator
    def get_all_users(self):
        users = set(x.user for x in self.session.query(
            TaskUserEditors).all())
        return users

    @log_decorator
    def create_task(self,
                    user,
                    name,
                    status='todo',
                    priority='medium',
                    start_date=datetime.now(),
                    description=None,
                    end_date=None,
                    parent_task_id=None,
                    assigned=None
                    ) -> Task:
        """Allow create task with provided parameters

        Parameters
        ----------
        user : str
            username of user who create task
        name : str
        start_date : datetime

        Optional
        ----------
        status   : str
        priority : str
        description : str
        end_date  : datetime
        parent_task_id : int
        assigned : str
            username of assigned user

        Returns
        -------
        Task
            Task object

        """

        if priority:
            try:
                priority = TaskPriority[priority.upper()]
            except KeyError as e:
                raise CreateError('Priority not found') from e

        if status:
            try:
                status = TaskStatus[status.upper()]
            except KeyError as e:
                raise CreateError('Status not found') from e

        if parent_task_id:
            self.user_can_access_task(user=user,
                                      task_id=parent_task_id)

        validate_task_dates(start_date, end_date)

        task = Task(owner=user,
                    name=name,
                    description=description,
                    start_date=start_date,
                    priority=priority,
                    end_date=end_date,
                    parent_task_id=parent_task_id,
                    assigned=assigned,
                    status=status)

        task.editors.append(TaskUserEditors(user=user,
                                            task_id=task.id))

        if assigned and assigned is not user:
            task.editors.append(TaskUserEditors(user=assigned,
                                                task_id=task.id))

        self.session.add(task)
        self.session.commit()
        return task

    @log_decorator
    def get_task_by_id(self,
                       user: str,
                       task_id: int) -> Task:

        self.user_can_access_task(user, task_id)
        task = self.session.query(Task).get(task_id)
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
                    start_date=None) -> Task:

        task = self.get_task_by_id(user, task_id)

        args = {}

        if name:
            args[Task.name] = name
        if description:
            args[Task.description] = description
        if status:
            try:
                args[Task.status] = TaskStatus[status.upper()]
            except KeyError:
                raise UpdateError('Status not found')

        if priority:
            try:
                args[Task.priority] = TaskPriority[priority.upper()]
            except KeyError:
                raise UpdateError('Priority not found')

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
        return task

    @log_decorator
    def assign_user(self, user: str,
                    task_id: int,
                    user_receiver: str):
        task = self.get_task_by_id(user=user, task_id=task_id)

        if task.assigned == user_receiver:
            raise UpdateError(
                f'User({user}) already assigned as Task(ID={task_id}) executor')
        editor = self.get_task_user_relation(user=user_receiver, task_id=task_id)

        if editor is None:
            editor = TaskUserEditors(user=user_receiver, task_id=task_id)
            task.editors.append(editor)

        task.assigned = user_receiver

        self.session.commit()

    @log_decorator
    def share_task(self,
                   user: str,
                   task_id: int,
                   user_receiver: str):

        self.user_can_access_task(user=user, task_id=task_id)
        relation = self.get_task_user_relation(user=user_receiver,
                                               task_id=task_id)
        if relation:
            raise DuplicateRelation(
                f'Task(ID={task_id}) already shared with user({user_receiver})')

        self.session.add(TaskUserEditors(user=user_receiver,
                                         task_id=task_id))
        self.session.commit()

    @log_decorator
    def unshare_task(self,
                     user: str,
                     task_id: int,
                     user_receiver: str):

        task = self.get_task_by_id(user=user,
                                   task_id=task_id)

        if user_receiver == task.owner:
            raise UpdateError(
                'User({user}) cant unshare task with its owner')

        relation = self.get_task_user_relation(user=user_receiver,
                                               task_id=task_id)
        if relation is None:
            raise UpdateError(
                f'Task(ID{task_id}) wasnt shared with the user({user_receiver})')
        self.session.delete(relation)
        self.session.commit()

    @log_decorator
    def get_own_tasks(self, user: str) -> List[Task]:
        """Method allows to get all tasks created by user.

        Parameters
        ----------
        user : str

        Returns
        -------
        List[Task]
            List of tasks

        """
        return self.session.query(
            Task).filter_by(owner=user).all()

    @log_decorator
    def get_user_assigned_tasks(self, user: str) -> List[Task]:
        return self.session.query(
            Task).filter_by(assigned=user).all()

    @log_decorator
    def get_available_tasks(self, user: str) -> List[Task]:
        """Method allows to get all available tasks.

        Returns
        -------
        List[Task]
            List of tasks

        """
        return self.session.query(Task).join(
            TaskUserEditors).filter_by(
                user=user).all()

    @log_decorator
    def delete_task(self,
                    user: str,
                    task_id: int):
        task = self.get_task_by_id(user=user, task_id=task_id)
        if task.plan:
            self.session.delete(task.plan)
        self.session.delete(task)
        self.session.commit()

    @log_decorator
    def add_subtask(self,
                    user: str,
                    task_id: int,
                    parent_task_id: int):
        parent_task = self.get_task_by_id(user=user, task_id=parent_task_id)
        subtask = self.get_task_by_id(user=user, task_id=task_id)

        if parent_task.plan:
            raise UpdateError('You cant add subtasks to task with plan directly')

        if parent_task.parent_task_id == task_id:
            raise UpdateError('Loop dependecy error')

        if subtask.parent_task_id:
            raise UpdateError(
                f'Task(ID={task_id}) already have parent task')
        if task_id == parent_task_id:
            raise UpdateError('You cant attach task to itself')

        subtask.parent_task_id = parent_task_id
        self.session.commit()

    @log_decorator
    def rm_subtask(self, user: str, task_id: int):
        subtask = self.get_task_by_id(user=user, task_id=task_id)

        if subtask.parent_task_id is None:
            raise UpdateError(
                f'Task(ID={task_id}) dont have parent task')
        else:
            subtask.parent_task_id = None

        self.session.commit()

    @log_decorator
    def get_subtasks(self, user: str, task_id: int):
        self.user_can_access_task(user, task_id)

        return self.session.query(Task).filter_by(
            parent_task_id=task_id).join(
                TaskUserEditors).filter_by(user=user).all()

    @log_decorator
    def change_task_status(self,
                           user: str,
                           task_id: int,
                           status: str,
                           apply_on_subtasks=False):

        task = self.get_task_by_id(user=user, task_id=task_id)

        try:
            status = TaskStatus[status.upper()]
        except KeyError:
            raise UpdateError('Status not found')

        task.status = status
        task.updated = datetime.now()
        if (task.status is TaskStatus.DONE or apply_on_subtasks):
            self.session.query(Task).filter_by(
                parent_task_id=task_id).update({Task.status: status,
                                                Task.updated: datetime.now()})

        self.session.commit()
        return self.session.query(Task).get(task_id)

    @log_decorator
    def create_folder(self, user: str, name: str) -> Folder:
        """Allow create folder with provided name for user

        Parameters
        ----------
        user: str
            id of user who create folder
        name : str
            Folder name

        Returns
        -------
        Folder
            Folder object

        """
        folder = self.session.query(Folder).filter_by(user=user,
                                                      name=name).one_or_none()
        if folder:
            raise CreateError(f'User({user}) already has folder {folder.name}')
        folder = Folder(user=user, name=name)
        self.session.add(folder)

        self.session.commit()
        return folder

    @log_decorator
    def get_folder_by_id(self, user: str, folder_id: int) -> Folder:
        folder = self.session.query(Folder).filter_by(
            id=folder_id, user=user).one_or_none()
        check_object_exist(folder,
                           f'id : {folder_id}',
                           'Folder')

        return folder

    @log_decorator
    def get_folder_by_name(self, user: str, name: int) -> Folder:
        folder = self.session.query(Folder).filter_by(
            name=name, user=user).one_or_none()
        check_object_exist(folder, f'name: {name}', 'Folder')

        return folder

    @log_decorator
    def get_or_create_folder(self, user: str, name: str) -> Folder:
        try:
            folder = self.get_folder_by_name(user, name)
        except ObjectNotFound as e:
            folder = Folder(user=user, name=name)
            self.session.add(folder)
            self.session.commit()
        finally:
            return folder

    @log_decorator
    def get_all_folders(self, user: str) -> List[Folder]:
        return self.session.query(Folder).filter_by(user=user).all()

    @log_decorator
    def update_folder(self, user: str, folder_id: int, name):
        folder = self.get_folder_by_id(user=user, folder_id=folder_id)

        dupl = self.session.query(Folder).filter_by(
            user=user, name=name).all()

        if len(dupl) > 1:
            raise UpdateError(
                f'User({user}) already has folder {name}')
        folder.name = name

        self.session.commit()
        return folder

    @log_decorator
    def delete_folder(self, user: str, folder_id: int):
        folder = self.get_folder_by_id(user, folder_id)
        self.session.delete(folder)

        self.session.commit()

    @log_decorator
    def get_task_folders(self, user: str, task_id: int):
        return self.session.query(Folder).filter_by(user=user,
                                                    task_id=task_id).all()

    @log_decorator
    def populate_folder(self, user: str, folder_id: int, task_id: int):
        folder = self.get_folder_by_id(user, folder_id)
        task = self.get_task_by_id(user, task_id)
        if task in folder.tasks:
            raise DuplicateRelation(
                f'Folder with ID={folder_id} already have task with ID={task_id}')
        folder.tasks.append(task)

        self.session.commit()

    @log_decorator
    def unpopulate_folder(self,
                          user: str,
                          folder_id: int,
                          task_id: int):
        folder = self.get_folder_by_id(user, folder_id)
        task = self.get_task_by_id(user, task_id)
        if task not in folder.tasks:
            raise UpdateError(
                f'Folder with ID={folder_id} dont have task with ID={task_id}')
        folder.tasks.remove(task)

        self.session.commit()

    @log_decorator
    def create_plan(self, user, task_id,
                    period_amount,
                    period,
                    repetitions_amount=None,
                    end_date=None) -> Plan:

        task = self.get_task_by_id(user=user, task_id=task_id)
        if task.subtasks:
            raise CreateError('Task should be without subtasks')
        if task.plan:
            raise CreateError('Task already has a plan')
        if task.start_date is None:
            raise CreateError('Task should have start date')

        if end_date:
            validate_plan_end_date(end_date)

        try:
            period = Period[period.upper()]
        except KeyError as e:
            raise CreateError('Period not found') from e

        start_date = task.start_date
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
        return plan

    @log_decorator
    def get_plan_by_id(self, user: str, plan_id: int) -> Plan:
        plan = self.session.query(Plan).get(plan_id)
        check_object_exist(plan, plan_id, 'Plan')

        try:
            self.user_can_access_task(user, plan.task_id)
        except AccessError as e:
            raise AccessError(
                f'User({user}) doesnt have permissions to Plan(ID={plan_id})') from e
        return plan

    @log_decorator
    def get_all_plans(self, user: str) -> List[Plan]:
        return self.session.query(Plan).join(Task).join(
            TaskUserEditors).filter(
                TaskUserEditors.user == user).all()

    @log_decorator
    def get_own_plans(self, user: str) ->Plan:
        return self.session.query(Plan).filter_by(user=user).all()

    @log_decorator
    def get_generated_tasks_by_plan(self, user: str,
                                    plan_id: int) -> List[Task]:
        plan = self.get_plan_by_id(user=user, plan_id=plan_id)
        return self.session.query(Task).filter(
            Task.parent_task_id == plan.task_id).join(TaskUserEditors).all()

    @log_decorator
    def get_active_plans(self, user: str, plans=None) -> List[Plan]:
        if plans is None:
            plans = self.get_all_plans(user)

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
        """

        Parameters
        ----------
        user : str
        active_plans :

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
                                        parent_task_id=plan.task.id,
                                        assigned=plan.task.assigned)

                plan.last_activated = near_activation
                near_activation = plan.last_activated + interval
                plan.repetitions_counter += 1

                editors = [x for x in plan.task.editors if x is not user]
                for x in editors:
                    task.editors.append(
                        TaskUserEditors(user=x.user,
                                        task_id=task.id))

                self.session.add(task)
        self.session.commit()

    @log_decorator
    def delete_plan(self, user: str, plan_id: int):
        plan = self.get_plan_by_id(user, plan_id)
        self.session.delete(plan)
        self.session.commit()

    @log_decorator
    def update_plan(self, user: str,
                    plan_id: int,
                    period=None,
                    period_amount=None,
                    repetitions_amount=None,
                    end_date=None) -> Plan:

        plan = self.get_plan_by_id(user=user, plan_id=plan_id)
        args = {}

        args[Plan.period] = plan.period
        args[Plan.period_amount] = plan.period_amount
        args[Plan.repetitions_amount] = plan.repetitions_amount
        args[Plan.end_date] = plan.end_date

        if period:
            try:
                args[Plan.period] = Period[period.upper()]
            except KeyError as e:
                raise UpdateError('Period not found') from e

        if period_amount:
            args[Plan.period_amount] = period_amount
        if repetitions_amount:
            args[Plan.repetitions_amount] = repetitions_amount
        if end_date:
            args[Plan.end_date] = end_date

        validate_plan_end_date(args[Plan.end_date])
        args[Plan.end_type] = get_end_type(plan.start_date,
                                           args[Plan.period],
                                           args[Plan.period_amount],
                                           args[Plan.end_date],
                                           args[Plan.repetitions_amount])
        try:
            self.session.query(Plan).filter_by(id=plan_id).update(args)
        except exc.SQLAlchemyError as e:
            raise UpdateError('Arguments Error. Check your arguments') from e
        self.session.commit()
        return self.session.query(Plan).get(plan_id)

        return plan

    @log_decorator
    def get_obj_by_id(self, cls, id: int):
        """This method allows to get any object from the db without validation
           Use this only if you are confident what are you doing
           After work with object - commit changes via save_updates method

        Parameters
        ----------
        cls : Library type
            Library type. (Any entity type from models.py)
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

    # Allows to commit updates made out of the lib
    @log_decorator
    def save_updates(self):
        self.session.commit()
