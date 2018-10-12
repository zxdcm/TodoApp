# TodoApp

Todoapp is a simple task tracker and plan manager.
It allows you to create and edit tasks, track their progress, share them with other users.
Assign executors, set end dates and priorities, group tasks in personal folders. Set reminders for significant tasks

You can use todoapp in different ways:

todolib library for embedding capabilities in your own app;
todocli manage your tasks using command-line interface;
todoweb manage your tasks via web interface.

## Built with 
- **Python 3.6.5**  
- **Django 1.11.15&ast;**
- **SQLAlchemy** – SQL Toolkit and Object Relational Mapper
- **dateutil** – powerful extensions to the standard datetime module
-  **django-bootstrap4&ast;** - https://pypi.org/project/django-bootstrap4/ 

**&ast; - web requirements**

## Install

Make sure you have installed setuptools

``$ pip install setuptools``

Clone the repository

``
$ git clone https://zxdcm@bitbucket.org/zxdcm/isppythonlabs.git
``

Install the application

`` $ cd isppythonlabs``

``$ python setup.py install``

Now call the cli-app by typing following command

``$ todoapp``

## Console application usage

#### First usage

Register youself in the app

``$ todoapp user create <username> ``

Now you can use the application.
Just follow the help messages.


#### Working with users

`` $ todoapp user ``

#### Working with tasks

Lets create your first task:

``$ todoapp task create "My first task" ``

That command will create and print your first task

#### Working with folders

`` $ todoapp folder ``

#### Working with plans

`` $ todoapp plan ``

#### Working with reminders

`` $ todoapp reminder ``

#### Configure application settings

You can configure application by editing config.py file. Which location is ``todocli/config.py``

## Library usage


You are free to use the library to create your own application.

Library contains build-in types and logic validation.
It raises exceptions and warnings when errors occurred.


### Quickstart

1. Import set_up_connection and AppService

```
>>> from todolib.models import set_up_connection
>>> from todolib.services import AppService
```

2. Set up connection to database

```
>>> driver_name = 'sqlite'
>>> connection_string = '' # existing dir + any file name
>>> session = set_up_connection(driver_name, connection_string)
```

3. Create AppService object

```
>>> service = AppService(session)
```

4. Work with library objects like this one:

```
>>> user = 'manager'
>>> task = service.create_task(user, 'Make a report', priority='High')
>>> second_task = service.create_task(user, 'Shout at bad employees', priority='Low')

>>> folder = service.create_folder(user, 'Work')

>>> service.populate_folder(user, folder.id, task.id)
>>> service.populate_folder(user, folder.id, second_task.id)

>>> for task in folder.tasks:
...    print(f'Name: {task.name}, priority: {task.priority.value})
...
Name: Make a report, priority:  High
Name: Shout at bad employees, priority: Low

```

### Whats next?

Retrive and read library docs

``from todolib import services``

``help(services)``
