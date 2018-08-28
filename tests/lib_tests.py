import unittest
from datetime import datetime, timedelta

from todolib.services import AppService
from todolib import models as mo
from todolib import exceptions as ex

DRIVER_NAME = 'sqlite'
CONNECTIONSTRING = ':memory:'
TEST_USER = 'user'
TEST_NAME = 'name'
TEST_DESCRIPTION = 'description'
TEST_STATUS_VALUE = 'inwork'
TEST_STATUS = mo.TaskStatus.INWORK
TEST_PRIORITY_VALUE = 'high'
TEST_PRIORITY = mo.TaskPriority.HIGH
TEST_DATE_FIRST = datetime(2018, 8, 15, 20, 00)
TEST_DATE_SECOND = datetime.now()
TEST_DATE_THIRD = datetime.now() + timedelta(days=10)
TEST_RECEIVER = 'receiver'
TEST_RANDOM_INT = 100
TEST_RANDOM_STR = 'string'
TEST_PERIOD = mo.Period.DAY
TEST_PERIOD_VALUE = mo.Period.DAY.value
TEST_PLAN_END_DATE = datetime.now() + timedelta(days=TEST_RANDOM_INT)


class TaskTest(unittest.TestCase):

    def setUp(self):
        session = mo.set_up_connection(DRIVER_NAME, CONNECTIONSTRING)
        self.serv = AppService(session)

    def test_create_task(self):
        parent_task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME,
        )
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME,
            description=TEST_DESCRIPTION,
            start_date=TEST_DATE_FIRST,
            end_date=TEST_DATE_SECOND,
            priority=TEST_PRIORITY_VALUE,
            status=TEST_STATUS_VALUE,
            parent_task_id=parent_task.id)
        self.assertEqual(task.owner, TEST_USER)
        self.assertEqual(task.name, TEST_NAME)
        self.assertEqual(task.description, TEST_DESCRIPTION)
        self.assertEqual(task.priority, TEST_PRIORITY)
        self.assertEqual(task.status, TEST_STATUS)
        self.assertEqual(task.start_date, TEST_DATE_FIRST)
        self.assertEqual(task.end_date, TEST_DATE_SECOND)
        self.assertEqual(task.parent_task_id, parent_task.id)

        with self.assertRaises(KeyError):
            self.serv.create_task(user=TEST_USER, name=TEST_NAME,
                                  status=TEST_RANDOM_STR)
        with self.assertRaises(KeyError):
            self.serv.create_task(user=TEST_USER,
                                  name=TEST_NAME,
                                  priority=TEST_RANDOM_STR)

        plan = self.serv.create_plan(user=TEST_USER,
                                     task_id=task.id,
                                     period=TEST_PERIOD_VALUE,
                                     period_amount=TEST_RANDOM_INT)

        with self.assertRaises(ValueError):
            subtask = self.serv.create_task(user=TEST_USER,
                                            name=TEST_NAME,
                                            parent_task_id=task.id)

    def test_update_task(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name='TEST_NAME',
            description='TEST_DESCRIPTION',
            start_date=datetime(2018, 4, 4, 19, 00),
            end_date=datetime(2018, 4, 4, 21, 00),
            priority='low',
            status='todo')
        self.serv.update_task(user=TEST_USER,
                              task_id=task.id,
                              name=TEST_NAME,
                              description=TEST_DESCRIPTION,
                              start_date=TEST_DATE_FIRST,
                              end_date=TEST_DATE_SECOND,
                              priority=TEST_PRIORITY_VALUE,
                              status=TEST_STATUS_VALUE)
        self.assertEqual(task.name, TEST_NAME)
        self.assertEqual(task.description, TEST_DESCRIPTION)
        self.assertEqual(task.priority, TEST_PRIORITY)
        self.assertEqual(task.status, TEST_STATUS)
        self.assertEqual(task.start_date, TEST_DATE_FIRST)
        self.assertEqual(task.end_date, TEST_DATE_SECOND)

        with self.assertRaises(ValueError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  start_date=TEST_DATE_SECOND,
                                  end_date=TEST_DATE_FIRST)

        with self.assertRaises(ValueError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  end_date=TEST_DATE_FIRST)

        with self.assertRaises(ValueError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  start_date=TEST_DATE_SECOND)

        with self.assertRaises(KeyError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  priority=TEST_RANDOM_STR)

        with self.assertRaises(KeyError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  status=TEST_RANDOM_STR)

        with self.assertRaises(KeyError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  status=TEST_RANDOM_STR)

    def test_get_task_user_relation(self):
        task = self.serv.create_task(user=TEST_USER,
                                     name=TEST_NAME)
        rel = self.serv.get_task_user_relation(user=TEST_USER,
                                               task_id=task.id)
        self.assertTrue(rel)

        rel = self.serv.get_task_user_relation(user=TEST_USER,
                                               task_id=100)
        self.assertIsNone(rel)
        rel = self.serv.get_task_user_relation(user=TEST_RECEIVER,
                                               task_id=task.id)
        self.assertIsNone(rel)

    def test_get_task(self):
        task_created = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)
        task_expected = self.serv.get_task(user=TEST_USER,
                                           task_id=task_created.id)
        self.assertEqual(task_created, task_expected)

        with self.assertRaises(ex.ObjectNotFound):
            self.serv.get_task(user=TEST_RECEIVER,
                               task_id=task_created.id)
            self.serv.get_task(user=TEST_USER,
                               task_id=TEST_RANDOM_INT)

    def test_assign_user(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)

        self.serv.assign_user(user=TEST_USER,
                              task_id=task.id,
                              user_receiver=TEST_RECEIVER)

        self.assertTrue(task.assigned, TEST_RECEIVER)
        self.assertIn(TEST_RECEIVER, [rel.user for rel in task.members])

        with self.assertWarns(ex.RedundancyAction):
            self.serv.assign_user(user=TEST_USER,
                                  task_id=task.id,
                                  user_receiver=TEST_RECEIVER)

    def test_share_task(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)

        with self.assertRaises(ex.ObjectNotFound):
            self.serv.get_task(user=TEST_RECEIVER,
                               task_id=task.id)

        self.serv.share_task(user=TEST_USER,
                             task_id=task.id,
                             user_receiver=TEST_RECEIVER)
        task_rec = self.serv.get_task(user=TEST_RECEIVER,
                                      task_id=task.id)
        self.assertEqual(task, task_rec)

        with self.assertWarns(ex.RedundancyAction):
            self.serv.share_task(user=TEST_USER,
                                 task_id=task.id,
                                 user_receiver=TEST_RECEIVER)

    def test_unshare_task(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)

        with self.assertRaises(ValueError):
            self.serv.unshare_task(user=TEST_USER,
                                   task_id=task.id,
                                   user_receiver=TEST_USER)
        with self.assertRaises(ValueError):
            self.serv.unshare_task(user=TEST_USER,
                                   task_id=task.id,
                                   user_receiver=TEST_RECEIVER)

        self.serv.share_task(user=TEST_USER,
                             task_id=task.id,
                             user_receiver=TEST_RECEIVER)
        self.serv.unshare_task(user=TEST_USER,
                               task_id=task.id,
                               user_receiver=TEST_RECEIVER)
        self.assertNotIn(TEST_RECEIVER, [rel.user for rel in task.members])

    def test_delete_task(self):
        with self.assertRaises(ex.ObjectNotFound):
            self.serv.delete_task(user=TEST_USER,
                                  task_id=TEST_RANDOM_INT)

        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)
        self.serv.delete_task(user=TEST_USER,
                              task_id=task.id)

    def test_add_subtask(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)
        subtask = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)

        plan = self.serv.create_plan(user=TEST_USER,
                                     task_id=task.id,
                                     period='min',
                                     period_amount=10)

        with self.assertRaises(ValueError):

            self.serv.add_subtask(user=TEST_USER,
                                  task_id=subtask.id,
                                  parent_task_id=task.id)

        self.serv.delete_plan(user=TEST_USER,
                              plan_id=plan.id)

        self.serv.add_subtask(user=TEST_USER,
                              task_id=subtask.id,
                              parent_task_id=task.id)

        with self.assertRaises(ValueError):
            self.serv.add_subtask(user=TEST_USER,
                                  task_id=subtask.id,
                                  parent_task_id=task.id)

        with self.assertRaises(ValueError):
            self.serv.add_subtask(user=TEST_USER,
                                  task_id=task.id,
                                  parent_task_id=task.id)
        with self.assertRaises(ValueError):
            self.serv.add_subtask(user=TEST_USER,
                                  task_id=task.id,
                                  parent_task_id=subtask.id)

    def test_detach_task(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)
        subtask = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME,
            parent_task_id=task.id)

        self.serv.detach_task(TEST_USER, subtask.id)
        self.assertIsNone(subtask.parent_task_id)

        with self.assertRaises(ValueError):
            self.serv.detach_task(TEST_USER, subtask.id)

    def test_change_task_status(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)
        self.serv.change_task_status(user=TEST_USER,
                                     task_id=task.id,
                                     status=mo.TaskStatus.DONE.value)
        self.assertEqual(task.status, mo.TaskStatus.DONE)

        subtask = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)
        self.serv.add_subtask(user=TEST_USER,
                              task_id=subtask.id,
                              parent_task_id=task.id)

        self.serv.change_task_status(user=TEST_USER,
                                     task_id=task.id,
                                     status=mo.TaskStatus.DONE.value)

        self.assertEqual(subtask.status, mo.TaskStatus.DONE)

        with self.assertRaises(KeyError):
            self.serv.change_task_status(user=TEST_USER,
                                         task_id=task.id,
                                         status=TEST_RANDOM_STR)

    def test_get_filtered_tasks(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME,
            description=TEST_DESCRIPTION,
            status=TEST_STATUS_VALUE,
            priority=TEST_PRIORITY_VALUE,
            start_date=TEST_DATE_FIRST,
            end_date=TEST_DATE_THIRD)
        tasks = self.serv.get_filtered_tasks(user=TEST_USER,
                                             name=TEST_NAME,
                                             description=TEST_DESCRIPTION,
                                             start_date=TEST_DATE_FIRST,
                                             end_date=TEST_DATE_THIRD,
                                             priority=TEST_PRIORITY_VALUE,
                                             status=TEST_STATUS_VALUE)
        self.assertEqual(len(tasks), 0)


class FolderTest(unittest.TestCase):

    def setUp(self):
        session = mo.set_up_connection(DRIVER_NAME, CONNECTIONSTRING)
        self.serv = AppService(session)

    def test_create_folder(self):
        folder = self.serv.create_folder(user=TEST_USER,
                                         name=TEST_RANDOM_STR)
        self.assertEqual(folder.user, TEST_USER)
        self.assertEqual(folder.name, TEST_RANDOM_STR)

    def test_update_folder(self):
        folder1 = self.serv.create_folder(user=TEST_USER,
                                          name='folder1')

        self.serv.update_folder(user=TEST_USER,
                                folder_id=folder1.id,
                                name='newfoldername')

        self.assertEqual(folder1.name, 'newfoldername')

    def test_get_folder(self):
        folder = self.serv.create_folder(user=TEST_USER,
                                         name=TEST_NAME)
        folder_copy = self.serv.get_folder(user=TEST_USER,
                                           folder_id=folder.id)
        self.assertEqual(folder, folder_copy)

        with self.assertRaises(ex.ObjectNotFound):
            self.serv.get_folder(user=TEST_USER,
                                 folder_id=TEST_RANDOM_INT)

    def test_delete_folder(self):
        folder = self.serv.create_folder(user=TEST_USER, name='randomstr')
        self.serv.delete_folder(user=TEST_USER,
                                folder_id=folder.id)
        with self.assertRaises(ex.ObjectNotFound):
            self.serv.get_folder(user=TEST_USER, folder_id=folder.id)

    def test_populate_folder(self):
        folder = self.serv.create_folder(user=TEST_USER, name='rand')
        self.assertEqual(len(folder.tasks), 0)
        task = self.serv.create_task(user=TEST_USER, name=TEST_NAME)
        self.serv.populate_folder(user=TEST_USER,
                                  folder_id=folder.id,
                                  task_id=task.id)
        self.assertEqual(len(folder.tasks), 1)

        with self.assertWarns(ex.RedundancyAction):
            self.serv.populate_folder(user=TEST_USER,
                                      folder_id=folder.id,
                                      task_id=task.id)

        self.serv.unpopulate_folder(user=TEST_USER, folder_id=folder.id,
                                    task_id=task.id)

        self.assertEqual(len(folder.tasks), 0)

        with self.assertRaises(ValueError):
            self.serv.unpopulate_folder(user=TEST_USER,
                                        folder_id=folder.id,
                                        task_id=task.id)


class PlanTest(unittest.TestCase):

    def setUp(self):
        session = mo.set_up_connection(DRIVER_NAME, CONNECTIONSTRING)
        self.serv = AppService(session)

    def test_create_plan(self):

        task = self.serv.create_task(user=TEST_USER, name=TEST_NAME,
                                     start_date=TEST_DATE_FIRST)

        with self.assertRaises(ex.ObjectNotFound):
            plan = self.serv.create_plan(user=TEST_RECEIVER, task_id=task.id,
                                         period_amount=TEST_RANDOM_INT,
                                         period=TEST_PERIOD_VALUE)

        DATE = datetime.now()
        plan = self.serv.create_plan(user=TEST_USER, task_id=task.id,
                                     period_amount=TEST_RANDOM_INT,
                                     period=TEST_PERIOD_VALUE,
                                     end_date=TEST_PLAN_END_DATE,
                                     repetitions_amount=TEST_RANDOM_INT,
                                     start_date=DATE)

        self.assertEqual(plan.user, TEST_USER)
        self.assertEqual(plan.task.id, task.id)
        self.assertEqual(plan.period_amount, TEST_RANDOM_INT)
        self.assertEqual(plan.period, TEST_PERIOD)
        self.assertEqual(plan.end_date, TEST_PLAN_END_DATE)
        self.assertEqual(plan.repetitions_amount, TEST_RANDOM_INT)
        self.assertEqual(plan.start_date, DATE)

        with self.assertRaises(ValueError):
            plan = self.serv.create_plan(user=TEST_USER,
                                         task_id=task.id,
                                         period=TEST_PERIOD_VALUE,
                                         period_amount=TEST_RANDOM_INT)

        with self.assertRaises(KeyError):
            task.plan = None
            self.serv.save_updates()
            plan = self.serv.create_plan(user=TEST_USER,
                                         task_id=task.id,
                                         period=TEST_RANDOM_STR,
                                         period_amount=TEST_RANDOM_INT)

        task.plan = None
        subtask = self.serv.create_task(user=TEST_USER, name=TEST_NAME)
        self.serv.add_subtask(user=TEST_USER, task_id=subtask.id, parent_task_id=task.id)
        with self.assertRaises(ValueError):
            plan = self.serv.create_plan(user=TEST_USER,
                                         task_id=task.id,
                                         period=TEST_PERIOD_VALUE,
                                         period_amount=TEST_RANDOM_INT)

    def test_update_plan(self):
        task = self.serv.create_task(user=TEST_USER, name=TEST_NAME,
                                     start_date=TEST_DATE_FIRST)
        plan = self.serv.create_plan(user=TEST_USER, task_id=task.id,
                                     period_amount=10,
                                     period=mo.Period.MONTH.value,
                                     end_date=TEST_PLAN_END_DATE,
                                     repetitions_amount=100)
        with self.assertRaises(KeyError):
            self.serv.update_plan(user=TEST_USER, plan_id=plan.id,
                                  period=TEST_RANDOM_STR)
        with self.assertRaises(ValueError):
            self.serv.update_plan(user=TEST_USER, plan_id=plan.id,
                                  end_date=TEST_DATE_FIRST)

        plan = self.serv.update_plan(user=TEST_USER, plan_id=plan.id,
                                     period=TEST_PERIOD_VALUE,
                                     period_amount=TEST_RANDOM_INT,
                                     end_date=TEST_DATE_THIRD,
                                     repetitions_amount=TEST_RANDOM_INT)

        self.assertEqual(plan.period, TEST_PERIOD)
        self.assertEqual(plan.period_amount, TEST_RANDOM_INT)
        self.assertEqual(plan.end_date, TEST_DATE_THIRD)
        self.assertEqual(plan.repetitions_amount, TEST_RANDOM_INT)

    def test_execute_and_get_active_plans(self):
        taskslen = len(self.serv.get_available_tasks(user=TEST_USER))
        self.assertEqual(taskslen, 0)
        plans = self.serv.get_active_plans(TEST_USER)
        self.assertEqual(len(plans), 0)

        task1 = self.serv.create_task(user=TEST_USER, name=TEST_NAME,
                                      start_date=TEST_DATE_FIRST)

        plan1 = self.serv.create_plan(user=TEST_USER, task_id=task1.id,
                                      period_amount=1,
                                      period=TEST_PERIOD_VALUE,
                                      end_date=TEST_PLAN_END_DATE,
                                      start_date=TEST_DATE_FIRST)

        self.assertEqual(plan1.task.id, task1.id)

        task2 = self.serv.create_task(user=TEST_USER, name=TEST_NAME,
                                      start_date=TEST_DATE_FIRST)
        plan2 = self.serv.create_plan(user=TEST_USER, task_id=task2.id,
                                      period_amount=1,
                                      period=TEST_PERIOD_VALUE,
                                      repetitions_amount=100,
                                      start_date=TEST_DATE_FIRST)

        task3 = self.serv.create_task(user=TEST_USER, name=TEST_NAME,
                                      start_date=TEST_DATE_FIRST)
        plan3 = self.serv.create_plan(user=TEST_USER, task_id=task3.id,
                                      period_amount=1,
                                      period=TEST_PERIOD_VALUE,
                                      start_date=TEST_DATE_FIRST)

        plans = self.serv.get_active_plans(TEST_USER)
        self.assertEqual(len(plans), 3)
        self.assertEqual(plan1.end_type, mo.EndType.DATE)
        self.assertEqual(plan2.end_type, mo.EndType.AMOUNT)
        self.assertEqual(plan3.end_type, mo.EndType.NEVER)

        self.serv.execute_plans(user=TEST_USER)
        taskslen = len(self.serv.get_available_tasks(user=TEST_USER))
        res = plan1.repetitions_counter + plan2.repetitions_counter
        res += plan3.repetitions_counter + 3
        self.assertTrue(len, res)


class ReminderTest(unittest.TestCase):

    def setUp(self):
        session = mo.set_up_connection(DRIVER_NAME, CONNECTIONSTRING)
        self.serv = AppService(session)
        self.task = self.serv.create_task(user=TEST_USER, name=TEST_NAME)
        self.reminder = self.serv.create_reminder(task_id=self.task.id,
                                                  user=TEST_USER,
                                                  date=TEST_DATE_THIRD)

    def test_create_reminder(self):

        self.assertTrue(self.reminder.task, self.task)
        self.assertTrue(self.reminder.date, TEST_DATE_FIRST)
        self.serv.update_task(user=TEST_USER,
                              task_id=self.task.id,
                              end_date=TEST_DATE_THIRD)
        with self.assertRaises(ValueError):
            reminder = self.serv.create_reminder(task_id=self.task.id,
                                                 user=TEST_USER,
                                                 date=TEST_DATE_FIRST)

    def test_delete_reminder(self):
        with self.assertRaises(ex.ObjectNotFound):
            self.serv.delete_reminder(user=TEST_USER,
                                      reminder_id=TEST_RANDOM_INT)
        self.serv.delete_reminder(user=TEST_USER,
                                  reminder_id=self.reminder.id)

    def test_update_reminder(self):
        with self.assertRaises(ex.ObjectNotFound):
            self.serv.update_reminder(user=TEST_USER,
                                      reminder_id=TEST_RANDOM_INT)

        reminder = self.serv.update_reminder(user=TEST_USER,
                                             reminder_id=self.reminder.id,
                                             date=TEST_DATE_THIRD)
        self.assertEqual(reminder.date, TEST_DATE_THIRD)

        with self.assertRaises(ValueError):
            reminder = self.serv.update_reminder(user=TEST_USER,
                                                 reminder_id=self.reminder.id,
                                                 date=TEST_DATE_FIRST)
