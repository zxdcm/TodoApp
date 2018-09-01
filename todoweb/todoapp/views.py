from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from todolib.services import  AppService
from todolib.models import (set_up_connection,
                            TaskPriority,
                            TaskStatus)
from todolib.exceptions import ObjectNotFound
from todoapp import get_service
from .forms import TaskForm


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('todoapp:index')
    else:
        form = UserCreationForm()
    return render(request,
                  'registration/signup.html',
                  {'form': form})

def index(request):
    return render(request, 'base.html')

@login_required
def create_task(request):

    service = get_service()
    user = request.user.username

    if request.method == 'POST':
        form = TaskForm(user, request.POST)
        if form.is_valid():
            try:
                assigned = form.cleaned_data['assigned']
                if assigned:
                    assigned = assigned.username

                task = service.create_task(user=user,
                                       name=form.cleaned_data['name'],
                                       description=form.cleaned_data['description'],
                                       priority=form.cleaned_data['priority'],
                                       status=form.cleaned_data['status'],
                                       event = form.cleaned_data['event'],
                                       start_date=form.cleaned_data['start_date'],
                                       end_date=form.cleaned_data['end_date'],
                                       assigned=assigned)
            except ValueError as e:
                form.add_error('start_date', e)
                return render(request, 'tasks/add.html', {'form': form})

            folders_ids = form.cleaned_data['folders']
            if '0' in folders_ids:
                folders_ids.remove('0')
            for folder_id in form.cleaned_data['folders']:
                service.populate_folder(user=user,
                                        folder_id=folder_id,
                                        task_id=task.id)
            return redirect('todoapp:show_task', task.id)

    else:
        form = TaskForm(user, None)
    return render(request, 'tasks/add.html', {'form': form})

@login_required
def edit_task(request, id):
    service = get_service()
    user = request.user.username

    try:
        task = service.get_task(user=user, task_id=id)
    except ObjectNotFound:
        return redirect('todoapp:index')

    if request.method == 'POST':
        form = TaskForm(user, request.POST)
        if form.is_valid():
            try:
                task = service.update_task(user=user,
                                           task_id=id,
                                           name=form.cleaned_data['name'],
                                           description=form.cleaned_data['description'],
                                           priority=form.cleaned_data['priority'],
                                           status=form.cleaned_data['status'],
                                           event=form.cleaned_data['event'],
                                           start_date=form.cleaned_data['start_date'],
                                           end_date=form.cleaned_data['end_date'])
            except ValueError as e:
                form.add_error('start_date', e)
                return render(request, 'tasks/edit.html', {'form': form})

            assigned = form.cleaned_data['assigned']

            if assigned:
                service.assign_user(user=user,
                                    task_id=task.id,
                                    user_receiver=assigned.username)
            else:
                task.assigned = None

            folders = service.get_task_folders(task.id)
            for folder in folders:
                folder.tasks.remove(task)

            folders_ids = form.cleaned_data['folders']
            if '0' in folders_ids:
                folders_ids.remove('0')
            for folder_id in folders_ids:
                folder = service.get_folder(user=user,
                                            folder_id=folder_id)
                folder.tasks.append(task)

            service.save_updates()
            return redirect('todoapp:tasks')

    else:
        assigned = None
        if task.assigned:
            assigned = User.objects.filter(username=task.assigned).get()

        initial_folders = [folder.id for folder in service.get_task_folders(task.id)
                           if task.id in map(lambda x: x.id, folder.tasks)]

        form = TaskForm(
            user,
            initial={
                'name': task.name,
                'description': task.description,
                'status': task.status.value,
                'priority': task.priority.value,
                'event': task.event,
                'start_date': task.start_date,
                'end_date': task.end_date,
                'assigned': assigned,
                'folders': initial_folders
            })

    return render(request, 'tasks/edit.html', {'form': form})

@login_required()
def show_task(request, id):
    try:
       task =get_service().get_task(user=request.user.username,
                                    task_id=id)
    except ObjectNotFound:
        return redirect('todoapp:tasks')
    return render(request, 'tasks/show.html', {'task': task})

@login_required
def tasks(request):
    return available_tasks(request)

@login_required
def delete_task(request):
    return render(request, 'base.html')


@login_required
def own_tasks(request):
    service = get_service()
    tasks = service.get_own_tasks(request.user.username)
    folders = service.get_all_folders(user=request.user.username)
    args = {'tasks':tasks, 'header': 'My tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)

@login_required
def available_tasks(request):
    service = get_service()
    tasks = service.get_available_tasks(request.user.username)
    folders = service.get_all_folders(user=request.user.username)
    args = {'tasks':tasks, 'header': 'Available tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)


@login_required
def assigned_tasks(request):
    service = get_service()
    tasks = service.get_user_assigned_tasks(request.user.username)
    folders = service.get_all_folders(user=request.user.username)
    args = {'tasks':tasks, 'header': 'Assigned tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)

@login_required
def archived_tasks(request):
    service = get_service()
    tasks = service.get_filtered_tasks(request.user.username,
                                       status=TaskStatus.ARCHIVED)
    folders = service.get_all_folders(user=request.user.username)
    args = {'tasks':tasks, 'header': 'Archived tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)


@login_required
def done_tasks(request):
    service = get_service()
    tasks = service.get_filtered_tasks(request.user.username,
                                       status=TaskStatus.DONE)
    folders = service.get_all_folders(user=request.user.username)
    args = {'tasks':tasks, 'header': 'Done tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)

@login_required
def folder_tasks(request, id):
    service = get_service()
    try:
        folder =service.get_folder(user=request.user.username,
                                   folder_id=id)
    except:
        return redirect('todoapp:tasks')
    folders = service.get_all_folders(user=request.user.username)
    args = {'tasks':folder.tasks, 'header': f'{folder.name} tasks',
            'folders':folders}
    return render(request, 'tasks/list.html', args)


@login_required
def add_folder(request):
    return render(request, 'tasks/list.html')

def dashboard_test(request):
    return render(request, 'Dashboard Template for Bootstrap.html')
