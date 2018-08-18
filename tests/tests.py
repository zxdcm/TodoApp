import unittest

from lib.services import AppService
from lib import models as mo
from lib import exceptions as ex
from datetime import datetime


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
TEST_RECEIVER = 'receiver'
TEST_RANDOM_INT = 100
TEST_RANDOM_STR = 'string'


class TaskTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.serv = AppService(CONNECTIONSTRING)

    def test_create_task(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME,
            description=TEST_DESCRIPTION,
            start_date=TEST_DATE_FIRST,
            end_date=TEST_DATE_SECOND,
            priority=TEST_PRIORITY_VALUE,
            status=TEST_STATUS_VALUE)
        self.assertEqual(task.owner, TEST_USER)
        self.assertEqual(task.name, TEST_NAME)
        self.assertEqual(task.description, TEST_DESCRIPTION)
        self.assertEqual(task.priority, TEST_PRIORITY)
        self.assertEqual(task.status, TEST_STATUS)
        self.assertEqual(task.start_date, TEST_DATE_FIRST)
        self.assertEqual(task.end_date, TEST_DATE_SECOND)

        with self.assertRaises(ex.CreateError):
            self.serv.create_task(user=TEST_USER,
                                  name=TEST_NAME,
                                  priority=TEST_RANDOM_STR)
            self.serv.create_task(user=TEST_USER, name=TEST_NAME,
                                  status=TEST_RANDOM_STR)

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

        with self.assertRaises(ex.TimeError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  start_date=TEST_DATE_SECOND,
                                  end_date=TEST_DATE_FIRST)
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  end_date=TEST_DATE_FIRST)
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  start_date=TEST_DATE_SECOND)

        with self.assertRaises(ex.UpdateError):
            self.serv.update_task(user=TEST_USER,
                                  task_id=task.id,
                                  name=TEST_NAME,
                                  priority=TEST_RANDOM_STR)
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

    def test_user_can_access_task(self):

        task = self.serv.create_task(user=TEST_USER,
                                     name=TEST_NAME)

        val = self.serv.user_can_access_task(user=TEST_USER,
                                             task_id=task.id)
        self.assertTrue(val)

        with self.assertRaises(ex.AccessError):
            self.serv.user_can_access_task(user=TEST_RECEIVER,
                                           task_id=task.id)
            self.serv.user_can_access_task(user=TEST_USER,
                                           task_id=TEST_RANDOM_INT)

    def test_get_task(self):
        task_created = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)
        task_expected = self.serv.get_task_by_id(user=TEST_USER,
                                                 task_id=task_created.id)
        self.assertEqual(task_created, task_expected)

        with self.assertRaises(ex.AccessError):
            self.serv.get_task_by_id(user=TEST_RECEIVER,
                                     task_id=task_created.id)
            self.serv.get_task_by_id(user=TEST_USER,
                                     task_id=TEST_RANDOM_INT)

    def test_share_task(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)

        with self.assertRaises(ex.AccessError):
            self.serv.get_task_by_id(user=TEST_RECEIVER,
                                     task_id=task.id)

        self.serv.share_task(user=TEST_USER,
                             task_id=task.id,
                             user_receiver=TEST_RECEIVER)
        task_rec = self.serv.get_task_by_id(user=TEST_RECEIVER,
                                            task_id=task.id)
        self.assertEqual(task, task_rec)

        with self.assertRaises(ex.DuplicateRelation):
            self.serv.share_task(user=TEST_USER,
                                 task_id=task.id,
                                 user_receiver=TEST_RECEIVER)

    def test_unshare_task(self):
        task = self.serv.create_task(
            user=TEST_USER,
            name=TEST_NAME)

        with self.assertRaises(ex.UpdateError):
            self.serv.unshare_task(user=TEST_USER,
                                   task_id=task.id,
                                   user_receiver=TEST_USER)
            self.serv.unshare_task(user=TEST_USER,
                                   task_id=task.id,
                                   user_receiver=TEST_RECEIVER)

        self.serv.share_task(user=TEST_USER,
                             task_id=task.id,
                             user_receiver=TEST_RECEIVER)
        self.assertIn(TEST_RECEIVER, [rel.user for rel in task.editors])

    def test_delete_task(self):
        with self.assertRaises(ex.AccessError):
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

        with self.assertRaises(ex.UpdateError):
            self.serv.add_subtask(user=TEST_USER,
                                  task_id=task.id,
                                  parent_task_id=task.id)

        self.serv.add_subtask(user=TEST_USER,
                              task_id=subtask.id,
                              parent_task_id=task.id)
        self.assertEqual(subtask.parent_task_id, task.id)

        with self.assertRaises(ex.UpdateError):
            self.serv.add_subtask(user=TEST_USER,
                                  task_id=task.id,
                                  parent_task_id=task.id)

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


class FolderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.serv = AppService(CONNECTIONSTRING)

    def test_create_folder(self):
        folder = self.serv.create_folder(user=TEST_USER,
                                         name='TESTNAME')

        self.assertEqual(folder.user, TEST_USER)
        self.assertEqual(folder.name, 'TESTNAME')

    def test_update_folder(self):
        folder = self.serv.create_folder(user=TEST_USER,
                                         name=TEST_RANDOM_STR)
        self.serv.update_folder(user=TEST_USER,
                                folder_id=folder.id,
                                name=TEST_NAME)

        self.assertEqual(folder.name, TEST_NAME)

        with self.assertRaises(ex.UpdateError):
            self.serv.update_folder(user=TEST_USER,
                                    folder_id=folder.id,
                                    name=TEST_NAME)

    def test_get_folder(self):
        folder = self.serv.create_folder(user=TEST_USER,
                                         name=TEST_NAME)
        folder_copy = self.serv.get_folder_by_id(user=TEST_USER,
                                                 folder_id=folder.id)
        self.assertEqual(folder, folder_copy)

        with self.assertRaises(ex.ObjectNotFound):
            self.serv.get_folder_by_id(user=TEST_USER,
                                       folder_id=TEST_RANDOM_INT)

    def test_delete_folder(self):
        folder = self.serv.create_folder(user=TEST_USER, name='randomstr')
        self.serv.delete_folder(user=TEST_USER,
                                folder_id=folder.id)
        with self.assertRaises(ex.ObjectNotFound):
            self.serv.get_folder_by_id(user=TEST_USER, folder_id=folder.id)
