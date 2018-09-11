""" Package that contains simple task library

    Modules:
    models - contains models that are used in library
    services - contains AppService that provide api to work with library
    exceptions - contains library exceptions and warnings
    logging - contains logger, its decorator and setup method
    utils - containts utils that used by library
    validators - contains validate methods that used by library

    Usage:
        1. import library
        2. create session object by calling set_up_connection
        3. create AppService object by passing session object

    Example:

        >>> from todolib.services import AppService
        >>> from todolib.models import set_up_connection
        >>> driver_name = 'sqlite'
        >>> connection_string = '' # existing dir + any file name
        >>> session = set_up_connection(driver_name, connection_string)
        >>> service = AppService(session)
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

    Notes:
        You can use the library to create your own application.


"""
