from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import logging

from todolib.models import (TaskPriority,
                            TaskStatus)
from todolib.exceptions import ObjectNotFound
from todoapp import get_service
from .forms import TaskForm, FolderForm


logger = logging.getLogger(__name__)

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
def add_folder(request):

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            service = get_service()
            name = form.cleaned_data['name']
            user = request.user.username
            folder = service.get_folder_by_name(user=user, name=name)

            if folder:
                form.add_error('name', f'You already have folder {name}')
                return render(request, 'tasks/add.html', {'form': form})

            folder = service.create_folder(user=user, name=name)
            return redirect('todoapp:folder_tasks', folder.id)

    else:
        form = FolderForm()

    return render(request, 'folders/add.html', {'form': form})

@login_required
def edit_folder(request, id):

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            service = get_service()
            user = request.user.username
            name = form.cleaned_data['name']
            folder = service.get_folder_by_name(user=user, name=name)
            logger.info('id type',type(id))
            if folder and folder.id is not id:
                form.add_error('name', f'You already have folder {name}')
                return render(request, 'tasks/edit.html', {'form':form})

            service.update_folder(user=user, folder_id=id, name=name)
            return redirect('todoapp:folder_tasks', id)

    else:
        form = FolderForm()

    return render(request, 'folders/edit.html', {'form': form})

@login_required
def delete_folder(request, id):
    if request.method == 'POST':
        service = get_service()
        user = request.user.username
        service.delete_folder(user=user,
                              folder_id=id)
    return redirect('todoapp:tasks')


@login_required
def create_task(request):

    user = request.user.username

    if request.method == 'POST':
        form = TaskForm(user, request.POST)
        if form.is_valid():
            try:
                service = get_service()
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

            for folder_id in folders_ids:
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

            current_folders = service.get_task_folders(task_id=task.id,
                                                       user=user)

            old_folders = set(map(lambda x: x.id, current_folders))
            new_folders = set(form.cleaned_data['folders'])

            add = new_folders.difference(old_folders)
            remove = old_folders.difference(new_folders)

            for folder_id in add:
                service.populate_folder(user=user,
                                        folder_id=folder_id,
                                        task_id=task.id)
            for folder_id in remove:
                service.unpopulate_folder(user=user,
                                          folder_id=folder_id,
                                          task_id=task.id)

            return redirect('todoapp:show_task', task.id)

    else:
        assigned = None
        if task.assigned:
            assigned = User.objects.filter(username=task.assigned).get()

        initial_folders = [folder.id for folder
                           in service.get_task_folders(task.id, user=user)]

        if not initial_folders:
            initial_folders = 0
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
        user = request.user.username
        task = get_service().get_task(user=user,
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
    user = request.user.username
    tasks = service.get_own_tasks(user)
    folders = service.get_all_folders(user)
    args = {'tasks':tasks, 'header': 'My tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)

@login_required
def available_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = service.get_available_tasks(user)
    folders = service.get_all_folders(user)
    args = {'tasks':tasks, 'header': 'Available tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)


@login_required
def assigned_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = service.get_user_assigned_tasks(user)
    folders = service.get_all_folders(user)
    args = {'tasks':tasks, 'header': 'Assigned tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)

@login_required
def archived_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = service.get_filtered_tasks(user=user,
                                       status=TaskStatus.ARCHIVED)
    folders = service.get_all_folders(user)
    args = {'tasks':tasks, 'header': 'Archived tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)


@login_required
def done_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = service.get_filtered_tasks(user=user,
                                       status=TaskStatus.DONE)
    folders = service.get_all_folders(user)
    args = {'tasks':tasks, 'header': 'Done tasks',
            'folders': folders}
    return render(request, 'tasks/list.html', args)

@login_required
def folder_tasks(request, id):
    service = get_service()
    user = request.user.username
    try:
        folder =service.get_folder(user=user,
                                   folder_id=id)
    except:
        return redirect('todoapp:tasks')
    folders = service.get_all_folders(user=user)
    args = {'tasks':folder.tasks, 'header': f'{folder.name} tasks',
            'folders':folders}
    return render(request, 'tasks/list.html', args)


def dashboard_test(request):
    return render(request, 'Dashboard Template for Bootstrap.html')
