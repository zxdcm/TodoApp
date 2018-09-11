from datetime import datetime, timedelta

from django import forms
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from todolib.models import TaskStatus, TaskPriority, Period
from todoapp import get_service



class TaskForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        folders = get_service().get_all_folders(user=user)
        folders_tuples = [(folder.id, folder.name)
                         for folder in folders]
        folders_tuples.insert(0, (0, '--------'))
        self.fields['folders'].choices = folders_tuples


    name = forms.CharField(max_length=200)

    description = forms.CharField(
        required=False,
        empty_value=None)
    priority = forms.ChoiceField(
        choices=[(priority.value, priority.value) for priority in TaskPriority]
    )
    status = forms.ChoiceField(
        choices=[(status.value, status.value) for status in TaskStatus][:-1],
        required=False)
    event = forms.BooleanField(initial=False, required=False)
    start_date = forms.DateTimeField(initial=datetime.now())
    end_date = forms.DateTimeField(initial=datetime.now() + timedelta(days=1))

    assigned = forms.ModelChoiceField(User.objects.all(), required=False)
    folders = forms.TypedMultipleChoiceField(required=True,
                                             coerce=int,
                                             empty_value=0)

    def clean_folders(self):
        data = self.cleaned_data['folders']
        if 0 in data:
            data.remove(0)
        return data

    def clean_assigned(self):
        if self.cleaned_data['assigned']:
            return self.cleaned_data['assigned'].username

    def clean_start_date(self):
        if self.cleaned_data['start_date']:
            return self.cleaned_data['start_date'].replace(tzinfo=None)

    def clean_end_date(self):
        if self.cleaned_data['end_date']:
            return self.cleaned_data['end_date'].replace(tzinfo=None)



class FolderForm(forms.Form):
    name = forms.CharField(max_length=20)

    
class SubTaskForm(forms.Form):

    task_id = forms.TypedChoiceField(coerce=int)

    def __init__(self, user, *args, **kwargs):
        super(SubTaskForm, self).__init__(*args, **kwargs)
        tasks = get_service().get_filtered_tasks(
            user=user,
            parentless=True)

        choices = ((task.id, f'ID: {task.id} Name: {task.name}') for task in tasks
                   if task.status != TaskStatus.ARCHIVED)
        self.fields['task_id'].choices = choices


class MemberForm(forms.Form):

    member = forms.ModelChoiceField(User.objects.all(), required=True)


class PlanForm(forms.Form):

    def __init__(self, user, plan_id, *args, **kwargs):
        super(PlanForm, self).__init__(*args, **kwargs)
        if plan_id is None:
            service = get_service()
            tasks = service.get_filtered_tasks(
                user=user,
                planless=True)
            choices = ((task.id, f'ID: {task.id} Name: {task.name}') for task in tasks
                       if task.status != TaskStatus.ARCHIVED and not task.subtasks)
            self.fields['task_id'].choices = choices
            self.fields['task_id'].label = 'Task'
        else:
            self.fields['task_id'].widget = forms.HiddenInput()
            self.fields['task_id'].required = False
            self.fields['start_date'].widget.attrs['readonly'] = True
            self.fields['start_date'].required = False


    task_id = forms.TypedChoiceField(coerce=int, required=True)

    period_amount = forms.IntegerField(
        validators=[MinValueValidator(1)])
    period = forms.ChoiceField(
        choices=[(period.value, period.value) for period in Period])

    repetitions_amount = forms.IntegerField(
        validators=[MinValueValidator(0)],
        required=False)

    start_date = forms.DateTimeField(initial=datetime.now()+timedelta(days=1))
    end_date = forms.DateTimeField(required=False)


    def clean_end_date(self):
        if self.cleaned_data['end_date']:
            date = self.cleaned_data['end_date'].replace(tzinfo=None)
            if date < datetime.now():
                msg = 'End date should be in future.'
                self.add_error('end_date', msg)
            return date

    def clean_start_date(self):
        if self.cleaned_data['start_date']:
            date = self.cleaned_data['start_date'].replace(tzinfo=None)
            if date < datetime.now():
                # dont show errors if use form for edit existing plan.
                readonly = self.fields['start_date'].widget.attrs.get('readonly', None)
                if readonly is not True:
                    msg = 'Start date should be in future.'
                    self.add_error('start_date', msg)
            return date

    def clean(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data.get('end_date', None)
        if (start_date and end_date) and (end_date < start_date):
            msg = 'End date should be greater than start date.'
            self.add_error('start_date', msg)


class ReminderForm(forms.Form):

    task_id = forms.TypedChoiceField(coerce=int)
    date = forms.DateTimeField(initial=datetime.now() + timedelta(days=1))

    def __init__(self, user, *args, **kwargs):
        super(ReminderForm, self).__init__(*args, **kwargs)
        tasks = get_service().get_filtered_tasks(user=user)

        choices = ((task.id, f'ID: {task.id} Name: {task.name}') for task in tasks)
        self.fields['task_id'].choices = choices

    def clean_date(self):
        if self.cleaned_data['date']:
            return self.cleaned_data['date'].replace(tzinfo=None)


class TaskSearchForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(TaskSearchForm, self).__init__(*args, **kwargs)

        service = get_service()

        priority_choices = [(priority.value, priority.value) for priority in TaskPriority]
        priority_choices.insert(0, (None, '---------'))

        status_choices = [(status.value, status.value) for status in TaskStatus]
        status_choices.insert(0, (None, '---------'))

        parent_tasks = service.get_available_tasks(user=user)

        parent_tasks_choices = [(task.id, f'ID: {task.id} Name: {task.name}') for task in parent_tasks]

        parent_tasks_choices.insert(0, (None, '---------'))

        self.fields['status'].choices = status_choices
        self.fields['priority'].choices = priority_choices
        self.fields['parent_task_id'].choices = parent_tasks_choices


    name = forms.CharField(max_length=200,
                           widget=forms.TextInput(),
                           required=False,
                           empty_value=None)

    owner = forms.ModelChoiceField(User.objects.all(),
                                   required=False)

    description = forms.CharField(required=False, empty_value=None)

    priority = forms.TypedChoiceField(required=False,
                                      empty_value=None)

    status = forms.TypedChoiceField(required=False,
                                    empty_value=None)

    parent_task_id = forms.TypedChoiceField(label='Parent task',
                                            required=False,
                                            coerce=int,
                                            empty_value=None)

    event = forms.NullBooleanField(required=False)

    start_date = forms.DateTimeField(required=False,
                                     help_text='From start date')
    end_date = forms.DateTimeField(required=False,
                                   help_text='Till end date')

    assigned = forms.ModelChoiceField(User.objects.all(),
                                      required=False)

    def clean_owner(self):
        if self.cleaned_data['owner']:
            return self.cleaned_data['owner'].username

    def clean_start_date(self):
        if self.cleaned_data['start_date']:
            return self.cleaned_data['start_date'].replace(tzinfo=None)

    def clean_end_date(self):
        if self.cleaned_data['end_date']:
            return self.cleaned_data['end_date'].replace(tzinfo=None)

    def clean_assigned(self):
        if self.cleaned_data['assigned']:
            return self.cleaned_data['assigned'].username


    def clean(self):
        if not any(self.cleaned_data.values()):
            self.add_error(0, 'You have forgotten to specify params')
