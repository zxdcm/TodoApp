from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from functools import wraps
import logging

from todolib.models import (TaskPriority,
                            TaskStatus)
from todolib.exceptions import ObjectNotFound
from todoapp import get_service
from .forms import (TaskForm,
                    FolderForm,
                    SubTaskForm,
                    MemberForm,
                    PlanForm,
                    ReminderForm)


logger = logging.getLogger(__name__)


def execute_plans(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        logger.info('username' ,request.user.username)
        get_service().execute_plans(request.user.username)
        return func(request, *args, **kwargs)

    return wrapper


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
@execute_plans
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
@execute_plans
def edit_folder(request, folder_id):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            service = get_service()
            user = request.user.username
            name = form.cleaned_data['name']
            folder_id = int(folder_id)
            folder = service.get_folder_by_name(user=user, name=name)
            if folder and folder.id != folder_id:
                form.add_error('name', f'You already have folder {name}')
                return render(request, 'tasks/edit.html', {'form':form})
            service.update_folder(user=user, folder_id=folder_id, name=name)
            return redirect('todoapp:folder_tasks', folder_id)

    else:
        form = FolderForm()

    return render(request, 'folders/edit.html', {'form': form})

@login_required
@execute_plans
def delete_folder(request, folder_id):
    if request.method == 'POST':
        service = get_service()
        user = request.user.username
        folder_id = int(folder_id)
        service.delete_folder(user=user,
                              folder_id=folder_id)
    return redirect('todoapp:tasks')


@login_required
@execute_plans
def add_task(request):

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
@execute_plans
def edit_task(request, task_id):

    service = get_service()
    user = request.user.username
    task_id = int(task_id)
    try:
        task = service.get_task(user=user, task_id=task_id)
    except ObjectNotFound:
        return redirect('todoapp:index')

    # button to edit task would be disabled. but link to edit task
    # still will be available. due to forms requests of get type on init form
    if task.status == TaskStatus.ARCHIVED:
        return redirect('todoapp:index')

    if request.method == 'POST':
        form = TaskForm(user, request.POST)
        if form.is_valid():
            try:
                task = service.update_task(user=user,
                                           task_id=task_id,
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

            old_folders = set(map(lambda folder: folder.id, current_folders))
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

    return render(request,
                  'tasks/edit.html',
                  {'form': form})

@login_required
@execute_plans
def show_task(request, task_id):
    try:
        user = request.user.username
        service = get_service()
        task_id = int(task_id)
        task = service.get_task(user=user,
                                      task_id=task_id)
        subtasks = service.get_subtasks(user=user,
                                        task_id=task_id)
    except ObjectNotFound:
        return redirect('todoapp:tasks')
    return render(request, 'tasks/show.html',
                  {'task': task, 'subtasks': subtasks})

@login_required
def tasks(request):
    return available_tasks(request)

@login_required
@execute_plans
def add_subtask(request, parent_task_id):
    user = request.user.username

    if request.method == 'POST':
        form = SubTaskForm(user, request.POST)
        if form.is_valid():
            service = get_service()
            task_id = form.cleaned_data['task_id']
            parent_task_id = int(parent_task_id)
            try:
                service.add_subtask(user=user,
                                    task_id=task_id,
                                    parent_task_id=parent_task_id)
            except ValueError as e:
                form.add_error('task_id', e)
                return render(request,
                              'tasks/add_subtask.html',
                              {'form': form})

            return redirect('todoapp:show_task', parent_task_id)

    else:
        form = SubTaskForm(user)

    return render(request,
                  'tasks/add_subtask.html',
                  {'form': form})

@login_required
@execute_plans
def detach_task(request, task_id):
    if request.method == 'POST':
        user = request.user.username
        service = get_service()
        task_id = int(task_id)
        service.detach_task(user=user,
                            task_id=task_id)
        return redirect('todoapp:show_task', task_id)

    return redirect('todoapp:index')

@login_required
@execute_plans
def share_task(request, task_id):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            service = get_service()
            user= request.user.username
            task_id = int(task_id)
            member = form.cleaned_data['member'].username
            service.share_task(user=user,
                               task_id=task_id,
                               user_receiver=member)
            return redirect('todoapp:show_task', task_id)

    else:
        form = MemberForm()

    return render(request,
                  'tasks/add_member.html',
                  {'form': form})

@login_required
@execute_plans
def unshare_task(request, task_id, member):
    user = request.user.username
    service = get_service()
    task_id = int(task_id)
    service.unshare_task(user=user,
                         task_id=task_id,
                         user_receiver=member)

    return redirect('todoapp:show_task', task_id)


def done_task(request, task_id):
    user = request.user.username
    service = get_service()
    task_id = int(task_id)
    service.change_task_status(user=user,
                               task_id=task_id,
                               status=TaskStatus.DONE.value)
    return redirect('todoapp:show_task', task_id)

@login_required
@execute_plans
def archive_task(request, task_id):
    if request.method == 'POST':
        user = request.user.username
        service = get_service()
        task_id = int(task_id)
        service.change_task_status(user=user,
                                   task_id=task_id,
                                   status=TaskStatus.ARCHIVED.value,
                                   apply_on_subtasks=True)
        return redirect('todoapp:show_task', task_id)

    return redirect('todoapp:index')


@login_required
@execute_plans
def delete_task(request, task_id):
    if request.method == 'POST':
        user = request.user.username
        service = get_service()
        task_id = int(task_id)
        service.delete_task(user=user,
                            task_id=task_id)
    return redirect('todoapp:tasks')

@login_required
@execute_plans
def own_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = [task for task in service.get_filtered_tasks(user=user, owner=user)
             if task.status != TaskStatus.ARCHIVED]
    folders = service.get_all_folders(user)

    return render(request, 'tasks/list.html',
                  {'tasks': tasks, 'header': 'My tasks',
                   'folders': folders})

@login_required
@execute_plans
def available_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = [task for task in service.get_available_tasks(user=user)
             if task.status != TaskStatus.ARCHIVED]
    folders = service.get_all_folders(user)

    return render(request, 'tasks/list.html',
                  {'tasks': tasks, 'header': 'Available tasks',
                   'folders': folders})


@login_required
@execute_plans
def assigned_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = [task for task in service.get_user_assigned_tasks(user)
            if task.status != TaskStatus.ARCHIVED]
    folders = service.get_all_folders(user)

    return render(request, 'tasks/list.html',
                  {'tasks': tasks, 'header': 'Assigned tasks',
                   'folders': folders})

@login_required
@execute_plans
def archived_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = service.get_filtered_tasks(user=user,
                                       status=TaskStatus.ARCHIVED)
    folders = service.get_all_folders(user)

    return render(request, 'tasks/list.html',
                  {'tasks': tasks, 'header': 'Archived tasks',
                   'folders': folders})


@login_required
@execute_plans
def done_tasks(request):
    service = get_service()
    user = request.user.username
    tasks = service.get_filtered_tasks(user=user,
                                       status=TaskStatus.DONE)
    folders = service.get_all_folders(user)

    return render(request, 'tasks/list.html',
                  {'tasks': tasks,
                   'header': 'Done tasks',
                   'folders': folders})

@login_required
@execute_plans
def folder_tasks(request, folder_id):
    service = get_service()
    user = request.user.username
    try:
        folder = service.get_folder(user=user,
                                   folder_id=folder_id)
    except:
        return redirect('todoapp:tasks')
    folders = service.get_all_folders(user=user)
    tasks = [task for task in folder.tasks
             if task.status != TaskStatus.ARCHIVED]

    return render(request, 'tasks/list.html',
                  {'tasks': tasks,
                   'header': f'{folder.name} tasks',
                   'folders': folders})

@login_required
@execute_plans
def plans(request):
    service = get_service()
    user = request.user.username
    plans = service.get_all_plans(user=user)

    return render(request, 'plans/list.html',
                  {'plans': plans,
                   'header': 'Available plans'})

@login_required
@execute_plans
def add_plan(request):

    user = request.user.username

    if request.method == 'POST':
        form = PlanForm(user, None, request.POST)
        if form.is_valid():
            try:
                service = get_service()
                task = service.create_plan(
                    user=user,
                    task_id=int(form.cleaned_data['task_id']),
                    period_amount=form.cleaned_data['period_amount'],
                    period=form.cleaned_data['period'],
                    start_date=form.cleaned_data['start_date'],
                    repetitions_amount=form.cleaned_data['repetitions_amount'],
                    end_date=form.cleaned_data['end_date'])

            except ValueError as e:
                form.add_error('end_date', e)
                return render(request, 'plans/add.html', {'form': form})

            return redirect('todoapp:show_plan', task.id)

    else:
        form = PlanForm(user, None, None)

    return render(request, 'plans/add.html', {'form': form})


@login_required
@execute_plans
def edit_plan(request, plan_id):

    service = get_service()
    user = request.user.username
    plan_id = int(plan_id)
    try:
        plan = service.get_plan(user=user, plan_id=plan_id)
    except ObjectNotFound:
        return redirect('todoapp:index')

    if request.method == 'POST':
        form = PlanForm(user, plan_id, request.POST)
        if form.is_valid():
            plan = service.update_plan(
                user=user,
                plan_id=plan_id,
                period=form.cleaned_data['period'],
                period_amount=form.cleaned_data['period_amount'],
                repetitions_amount=form.cleaned_data['repetitions_amount'],
                end_date=form.cleaned_data['end_date'],
            )
            return redirect('todoapp:show_plan', plan.id)

    else:
        form = PlanForm(
            user,
            plan_id,
            initial={
                'period': plan.period,
                'period_amount': plan.period_amount,
                'repetitions_amount': plan.repetitions_amount,
                'start_date': plan.start_date,
                'end_date': plan.end_date,
            })

    return render(request,
                  'plans/edit.html',
                  {'form': form})


@login_required
@execute_plans
def show_plan(request, plan_id):
    try:
        user = request.user.username
        service = get_service()
        plan_id = int(plan_id)
        plan = service.get_plan(user=user,
                                plan_id=plan_id)

    except ObjectNotFound:
        return redirect('todoapp:plans')

    return render(request, 'plans/show.html',
                  {'plan': plan})


@login_required
@execute_plans
def delete_plan(request, plan_id):
    if request.method == 'POST':
        user = request.user.username
        service = get_service()
        plan_id = int(plan_id)
        service.delete_plan(user=user,
                            plan_id=plan_id)
    return redirect('todoapp:plans')

@login_required
@execute_plans
def add_reminder(request):

    user = request.user.username

    if request.method == 'POST':
        form = ReminderForm(user, request.POST)
        if form.is_valid():
            try:
                service = get_service()
                service.create_reminder(
                    user=user,
                    task_id=int(form.cleaned_data['task_id']),
                    date=form.cleaned_data['date'])

            except ValueError as e:
                form.add_error('date', e)
                return render(request, 'reminders/add.html', {'form': form})

            return redirect('todoapp:reminders')

    else:
        form = ReminderForm(user, None)

    return render(request, 'reminders/add.html', {'form': form})

@login_required
@execute_plans
def edit_reminder(request, reminder_id):

    service = get_service()
    user = request.user.username
    reminder_id = int(reminder_id)

    try:
        reminder = service.get_reminder(user=user, reminder_id=reminder_id)
    except ObjectNotFound:
        return redirect('todoapp:index')

    if request.method == 'POST':
        form = ReminderForm(user, request.POST)
        if form.is_valid():
            try:
                service.update_reminder(user=user,
                                        reminder_id=reminder_id,
                                        date=form.cleaned_data['date'])
            except ValueError as e:
                form.add_error('start_date', e)
                return render(request, 'reminders/edit.html', {'form': form})

            return redirect('todoapp:reminders')

    else:

        form = ReminderForm(
            user,
            initial={
                'date': reminder.date
            })

    return render(request,
                  'reminders/edit.html',
                  {'form': form})


@login_required
@execute_plans
def delete_reminder(request, reminder_id):
    if request.method == 'POST':
        user = request.user.username
        service = get_service()
        reminder_id = int(reminder_id)
        service.delete_reminder(user=user,
                                reminder_id=reminder_id)

    return redirect('todoapp:reminders')



@login_required
@execute_plans
def reminders(request):
    service = get_service()
    user = request.user.username
    reminders = service.get_all_reminders(user=user)

    return render(request, 'reminders/list.html',
                  {'reminders': reminders,
                   'header': 'Available reminders'})

