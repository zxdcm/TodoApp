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

from lib.validators import validate_dates

from datetime import datetime


class AppService:

    def __init__(self, session=None):
        if session is None:
            session = set_up_connection()
        self.session = session

    def user_can_access_task(self, user_id: int, task_id: int):
        if self.session.query(Task).join(TaskUserEditors).filter_by(
                user_id=user_id, task_id=task_id).all():
            return True
        raise AccessError(
            f'User(ID={user_id}) doesnt have permissions to task(ID={task_id})')

    def user_with_id_exist(self, user_id: int):
        user_tasks = self.session.query(
            TaskUserEditors).filter_by(user_id=user_id).all()
        if user_tasks:
            return True

    def get_all_users_ids(self):
        user_ids = set(x.user_id for x in self.session.query(TaskUserEditors).all())
        return user_ids

    def create_task(self,
                    user_id,
                    name,
                    status='todo',
                    priority='medium',
                    start_date=datetime.now(),
                    description=None,
                    end_date=None,
                    parent_task_id=None,
                    assigned_id=None
                    ) -> Task:
        """Allow create task with provided parameters

        Parameters
        ----------
        user_id : int
            id of user who create task
        name : str
        start_date : datetime

        Optional
        ----------
        status   : str
        priority : str
        description : str
        end_date  : datetime
        parent_task_id : int
        assigned_id : int
            id of assigned user

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
            self.user_can_access_task(user_id=user_id, task_id=parent_task_id)

        if start_date and end_date:
            if start_date > end_date:
                raise CreateError('End date has to be after start date')

        task = Task(owner_id=user_id, name=name, description=description,
                    start_date=start_date, priority=priority,
                    end_date=end_date, parent_task_id=parent_task_id,
                    assigned_id=assigned_id, status=status)

        task.editors.append(TaskUserEditors(user_id=user_id, task_id=task.id))

        self.session.add(task)
        self.session.commit()
        return task

    def get_task_by_id(self,
                       user_id: int,
                       task_id: int) -> Task:
        self.user_can_access_task(user_id, task_id)
        task = self.session.query(Task).get(task_id)

        return task

    def update_task(self,
                    user_id: int,
                    task_id: int,
                    name=None,
                    description=None,
                    status=None,
                    priority=None,
                    end_date=None,
                    start_date=None,
                    parent_task_id=None) -> Task:

        task = self.get_task_by_id(user_id, task_id)

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

        task = self.session.query(Task).get(task_id)

        if start_date or end_date:
            if start_date is None:
                start_date = task.start_date
            elif end_date is None:
                end_date = task.end_date
            validate_dates(start_date, end_date)
            args[Task.start_date] = start_date
            args[Task.end_date] = end_date

        try:
            args[Task.updated] = datetime.now()
            self.session.query(Task).filter_by(id=task_id).update(args)

        except exc.SQLAlchemyError as e:
            raise UpdateError('Arguments Error. Check your arguments') from e

        self.session.commit()
        return task

    def assign_user(self, user_id: int,
                    task_id: int,
                    user_receiver_id: int):

        task = self.get_task_by_id(user_id=user_id, task_id=task_id)
        if task.assigned_id == user_receiver_id:
            raise UpdateError(
                f'User(ID={user_id}) already assigned as Task(ID={task_id}) executor')

        new_editor = TaskUserEditors(user_id=user_receiver_id, task_id=task_id)
        task.editors.append(new_editor)
        task.assigned_id = user_receiver_id

        self.session.commit()

    def share_task(self,
                   user_id: int,
                   task_id: int,
                   user_receiver_id: int):

        self.user_can_access_task(user_id, task_id)

        editor = self.session.query(TaskUserEditors).filter_by(
            user_id=user_receiver_id, task_id=task_id).one_or_none()
        if editor:
            raise DuplicateRelation(
                f'Task(ID={task_id}) already shared with user(ID={user_receiver_id})')

        new_editor = TaskUserEditors(user_id=user_receiver_id, task_id=task_id)
        self.session.add(new_editor)

        self.session.commit()

    def unshare_task(self,
                     user_id: int,
                     task_id: int,
                     user_receiver_id: int):

        task = self.get_task_by_id(user_id=user_id, task_id=task_id)

        if user_receiver_id == task.owner_id:
            raise AccessError(
                'User(ID={user_id}) cant unshare task with its owner')

        editor = self.session.query(TaskUserEditors).filter_by(
            user_id=user_receiver_id,
            task_id=task_id).one_or_none()
        if editor is None:
            raise UpdateError(
                f'Task(ID{task_id}) wasnt shared with the user(ID={user_receiver_id})')

        task.editors.remove(editor)
        self.session.commit()

    def get_own_tasks(self, user_id: int) -> List[Task]:
        """Method allows to get all tasks created by user.

        Parameters
        ----------
        user_id : int

        Returns
        -------
        List[Task]
            List of tasks

        """
        return self.session.query(
            Task).filter_by(owner_id=user_id).all()

    def get_user_assigned_tasks(self, user_id: int) -> List[Task]:
        return self.session.query(
            Task).filter_by(assigned_id=user_id).all()

    def get_available_tasks(self, user_id: int) -> List[Task]:
        """Method allows to get all available tasks.

        Returns
        -------
        List[Task]
            List of tasks

        """
        return self.session.query(Task).join(
            TaskUserEditors).filter_by(
                user_id=user_id).all()

    def delete_task(self, user_id: int, task_id: int, delete_plan=True):
        task = self.get_task_by_id(user_id=user_id, task_id=task_id)
        self.session.delete(task)
        if delete_plan:
            self.session.query(Plan).filter_by(task_id=task_id).delete()

        self.session.commit()

    def add_subtask(self, user_id: int, task_id: int, subtask_id: int):
        self.user_can_access_task(user_id, task_id)

        subtask = self.get_task_by_id(user_id=user_id, task_id=subtask_id)

        if subtask.parent_task_id:
            raise UpdateError(
                f'Subtask(ID={subtask_id}) already has parent task')
        subtask.parent_task_id = task_id

        self.session.commit()

    def get_subtasks(self, user_id: int, task_id: int):
        self.user_can_access_task(user_id, task_id)
        return self.session.query(Task).filter_by(
            parent_task_id=task_id).join(
                TaskUserEditors).filter_by(user_id=user_id).all()

    # def get_subtasks_t(self, user_id, task_id):
    #     task = self.get_task_by_id(user_id=user_id, task_id=task_id)
    #     return task.subtasks

    # def add_subtask(self, user_id, task_id, parent_task_id):
    #     task = self.get_task_by_id(user_id=user_id, task_id=task_id)
    #     rel = SubTaskRelation(task_id=task_id, parent_task_id=parent_task_id)
    #     if rel in task.subtasks:
    #         pass
    #     self.session.add(rel)
    #     self.session.commit()

    def change_task_status(self,
                           user_id: int,
                           task_id: int,
                           status: str,
                           apply_on_subtasks=None):

        task = self.get_task_by_id(user_id=user_id, task_id=task_id)

        try:
            status = TaskStatus[status.upper()]
        except KeyError:
            raise UpdateError('Status not found')

        task.status = status
        task.updated = datetime.now()

        if apply_on_subtasks:
            self.session.query(Task).filter_by(
                parent_task_id=task_id).join(
                    TaskUserEditors).filter_by(
                        user_id=user_id).update({Task.status: status,
                                                 Task.updated: datetime.now()})
        self.session.commit()
        return self.session.query(Task).get(task_id)

    def create_folder(self, user_id: int, name: str) -> Folder:
        """Allow create folder with provided name for user

        Parameters
        ----------
        user_id: int
            id of user who create folder
        name : str
            Folder name

        Returns
        -------
        Folder
            Folder object

        """
        folder = self.session.query(Folder).filter_by(user_id=user_id,
                                                      name=name).one_or_none()
        if folder:
            raise CreateError(f'User(ID={user_id}) already has folder {folder.name}')
        folder = Folder(user_id=user_id, name=name)

        self.session.add(folder)
        self.session.commit()
        return folder

    def get_folder_by_id(self, user_id: int, folder_id: int) -> Folder:
        folder = self.session.query(Folder).filter_by(
            id=folder_id, user_id=user_id).one_or_none()
        check_object_exist(folder,
                           f'id : {folder_id}',
                           'Folder')
        return folder

    def get_folder_by_name(self, user_id: int, name: int) -> Folder:
        folder = self.session.query(Folder).filter_by(
            name=name, user_id=user_id).one_or_none()
        check_object_exist(folder, f'name: {name}', 'Folder')
        return folder

    def get_or_create_folder(self, user_id: int, name: str) -> Folder:
        try:
            folder = self.get_folder_by_name(user_id, name)
        except ObjectNotFound as e:
            folder = Folder(user_id=user_id, name=name)
            self.session.add(folder)
            self.session.commit()
        finally:
            return folder

    def get_all_folders(self, user_id: int) -> List[Folder]:
        return self.session.query(Folder).filter_by(user_id=user_id).all()

    def update_folder(self, user_id: int, folder_id: int, name):
        folder = self.get_folder_by_id(user_id=user_id, folder_id=folder_id)

        dupl = self.session.query(Folder).filter_by(
            user_id=user_id, name=name).all()

        if len(dupl) > 1:
            raise UpdateError(
                f'User(ID={user_id}) already has folder {name}')
        folder.name = name

        self.session.commit()
        return folder

    def delete_folder(self, user_id: int, folder_id: int):
        folder = self.get_folder_by_id(user_id, folder_id)
        self.session.delete(folder)

        self.session.commit()

    def get_task_folders(self, user_id: int, task_id: int):
        return self.session.query(Folder).filter_by(user_id=user_id,
                                                    task_id=task_id).all()

    def populate_folder(self, user_id: int, folder_id: int, task_id: int):
        folder = self.get_folder_by_id(user_id, folder_id)
        task = self.get_task_by_id(user_id, task_id)
        if task in folder.tasks:
            raise DuplicateRelation(
                f'Folder with ID={folder_id} already have task with ID={task_id}')
        folder.tasks.append(task)
        self.session.commit()

    def unpopulate_folder(self,
                          user_id: int,
                          folder_id: int,
                          task_id: int):
        folder = self.get_folder_by_id(user_id, folder_id)
        task = self.get_task_by_id(user_id, task_id)
        if task not in folder.tasks:
            raise UpdateError(
                f'Folder with ID={folder_id} dont have task with ID={task_id}')
        folder.tasks.remove(task)
        self.session.commit()

    def create_plan(self, user_id, task_id,
                    period_amount,
                    period_type,
                    repetitions_amount=None,
                    end_date=None) -> Plan:

        task = self.get_task_by_id(user_id=user_id, task_id=task_id)

        if task.start_date is None:
            raise CreateError('Task should have start date')

        try:
            period = Period[period_type.upper()]
        except KeyError as e:
            raise CreateError('Period not found') from e

        start_date = task.start_date
        end_type = get_end_type(start_date, period, period_amount,
                                end_date, repetitions_amount)

        plan = Plan(user_id=user_id, task_id=task_id, period=period,
                    period_amount=period_amount,
                    end_type=end_type,
                    repetitions_amount=repetitions_amount,
                    end_date=end_date,
                    start_date=start_date)

        self.session.add(plan)
        self.session.commit()
        return plan

    def get_plan_by_id(self, user_id: int, plan_id: int) -> Plan:
        plan = self.session.query(Plan).get(plan_id)
        check_object_exist(plan, plan_id, 'Plan')

        try:
            self.user_can_access_task(user_id, plan.task_id)
        except AccessError as e:
            raise AccessError(
                f'User(ID={user_id}) doesnt have permissions to Plan(ID={plan_id})') from e
        return plan

    def get_all_plans(self, user_id: int) -> List[Plan]:
        return self.session.query(Plan).join(Task).join(
            TaskUserEditors).filter(
                TaskUserEditors.user_id == user_id).all()

    def get_own_plans(self, user_id: int) ->Plan:
        return self.session.query(Plan).filter_by(user_id=user_id).all()

    def get_generated_tasks_by_plan(self, user_id: int,
                                    plan_id: int) -> List[Task]:
        plan = self.get_plan_by_id(user_id=user_id, plan_id=plan_id)

        return self.session.query(Task).filter(
            Task.parent_task_id == plan.task_id).join(TaskUserEditors).all()

    def get_active_plans(self, user_id: int, plans=None) -> List[Plan]:
        if plans is None:
            plans = self.get_all_plans(user_id)

        plans = self.get_all_plans(user_id)
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

    def execute_plan(self, user_id: int, active_plans=None) -> List[Task]:
        """

        Parameters
        ----------
        user_id : type
            Description of parameter `user_id`.
        active_plans : type
            Description of parameter `active_plans`.

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
            active_plans = self.get_active_plans(user_id)
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

                task = self.create_task(user_id=user_id,
                                        name=plan.task.name,
                                        description=plan.task.description,
                                        start_date=near_activation,
                                        parent_task_id=plan.task.id,
                                        assigned_id=plan.task.assigned_id)
                plan.last_activated = near_activation
                near_activation = plan.last_activated + interval
                plan.repetitions_counter += 1
                for x in plan.task.editors:
                    if x.user_id is user_id:
                        continue
                    task.editors.append(
                        TaskUserEditors(user_id=x.user_id,
                                        task_id=task.id))
                self.session.add(task)
        self.session.commit()

    def delete_plan(self, user_id: int, plan_id: int):
        self.get_plan_by_id(user_id, plan_id).delete()
        self.session.commit()

    def update_plan(self,
                    user_id: int,
                    plan_id: int,
                    period_type=None,
                    period_amount=None,
                    repetitions_amount=None,
                    end_date=None) -> Plan:

        plan = self.get_plan_by_id(user_id=user_id, plan_id=plan_id)

        start_date = plan.start_date
        end_date = plan.end_date
        repetitions_amount = plan.repetitions_amount

        args = {}

        if period_type:
            try:
                args[Plan.period] = Period[period_type.upper()]
            except KeyError as e:
                raise UpdateError('Period not found') from e

        if period_amount:
            args[Plan.period_amount] = period_amount
        if repetitions_amount:
            args[Plan.repetitions_amount] = repetitions_amount
        if end_date:
            args[Plan.end_date] = end_date

        args[Plan.end_type] = get_end_type(start_date,
                                           end_date,
                                           repetitions_amount)

        try:
            self.session.query(Plan).filter_by(id=plan_id).update(args)
        except exc.SQLAlchemyError as e:
            raise UpdateError('Arguments Error. Check your arguments') from e
        self.session.commit()
        return self.session.query(Plan).get(plan_id)

        return plan

    def get_obj_by_id(self, cls, id: int):
        """This method allows to get any object from the db without validation
           Use this only if you are confident what are you doing
           After work with object - commit changes via save_updates method

        Parameters
        ----------
        cls : Library type
            Library type. (Any type from models.py)
        id : int
            Object id

        Returns
        -------
        Model
            Model or None

        """
        return self.session.query(cls).get(id)

    def delete_obj(self, obj):
        self.session.delete(obj)

        # Allows to commit updates made out of the lib
    def save_updates(self):
        self.session.commit()
