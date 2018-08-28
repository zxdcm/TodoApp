from django.shortcuts import render, redirect
from django.conf import settings
from todolib.services import  AppService
from todolib.models import set_up_connection
from todolib.exceptions import ObjectNotFound

def index(request):
    session = set_up_connection('sqlite',settings.DATABASES['default']['NAME'])
    service = AppService(session)
    task = service.create_task(user='user', name='test')

    return render(request, 'base.html',{'task': task})


def folders(request):
    return render(request, 'base.html')


def tasks(request):
    session = set_up_connection('sqlite',settings.DATABASES['default']['NAME'])
    service = AppService(session)
    tasks = service.get_available_tasks('test')
    args = {'tasks':tasks, 'header': 'Tasks'}
    return render(request, 'tasks/list.html', args)

def create_task(request):
    return render(request, 'base.html')

def edit_task(request):
    return render(request, 'base.html')

def show_task(request, id):
    session = set_up_connection('sqlite',settings.DATABASES['default']['NAME'])
    service = AppService(session)
    try:
       task =service.get_task(user='test', task_id=id)
    except ObjectNotFound:
        return redirect('todoapp:tasks')

    return render(request, 'tasks/show.html', {'task': task})

def delete_task(request):
    return render(request, 'base.html')
