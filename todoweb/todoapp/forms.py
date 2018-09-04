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


    name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'placeholder': 'Task name'}))
    description = forms.CharField(
        required=False)
    priority = forms.ChoiceField(
        choices=[(priority.value, priority.value) for priority in TaskPriority]
    )
    status = forms.ChoiceField(
        choices=[(status.value, status.value) for status in TaskStatus][:-1])
    event = forms.BooleanField(initial=False, required=False)
    start_date = forms.DateTimeField(required=True, initial=datetime.now())
    end_date = forms.DateTimeField(required=True,
                                   initial=datetime.now() + timedelta(days=1))

    assigned = forms.ModelChoiceField(User.objects.all(), required=False)
    folders = forms.MultipleChoiceField(required=False)

    def clean_folders(self):
        data = [*map(int, self.cleaned_data['folders'])]
        if 0 in data:
            data.remove(0)
        return data


    def clean_start_date(self):
        if self.cleaned_data['start_date']:
            self.cleaned_data['start_date'].replace(tzinfo=None)

    def clean_end_date(self):
        if self.cleaned_data['end_date']:
            self.cleaned_data['end_date'].replace(tzinfo=None)



class FolderForm(forms.Form):
    name = forms.CharField(max_length=20,
                           widget=forms.TextInput(
                            attrs={'placeholder': 'folder name'}))

    
class SubTaskForm(forms.Form):

    task_id = forms.ChoiceField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(SubTaskForm, self).__init__(*args, **kwargs)
        tasks = get_service().get_filtered_tasks(
            user=user,
            parentless=True)

        choices = ((task.id, f'ID: {task.id} Name: {task.name}') for task in tasks
                   if task.status != TaskStatus.ARCHIVED)
        self.fields['task_id'] = forms.ChoiceField(choices=choices)


    def clean_task_id(self):
        return int(self.cleaned_data['task_id'])
    
    
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
            self.fields['task_id'] = forms.ChoiceField(choices=choices, required=True)
            self.fields['task_id'].label = 'Task'
        else:
            self.fields['task_id'].widget = forms.HiddenInput()
            self.fields['task_id'].required = False
            self.fields['start_date'].widget.attrs['readonly'] = True
            self.fields['start_date'].required = False


    task_id = forms.ChoiceField()

    period_amount = forms.IntegerField(
        validators=[MinValueValidator(1)],
        required=True)
    period = forms.ChoiceField(
        choices=[(period.value, period.value) for period in Period],
        required=True)

    repetitions_amount = forms.IntegerField(
        validators=[MinValueValidator(1)],
        required=False,
        help_text='You may leave this field empty.')

    start_date = forms.DateTimeField(required=True, initial=datetime.now())
    end_date = forms.DateTimeField(required=False,
                                   help_text='You may leave this field empty')


    def clean_task_id(self):
        if self.cleaned_data['task_id']:
            return int(self.cleaned_data['task_id'])

    def clean_end_date(self):
        if self.cleaned_data['end_date']:
            date = self.cleaned_data['end_date'].replace(tzinfo=None)
            if date < datetime.now():
                msg = 'End date should be in future.'
                self._errors['end_date'] = [msg]
            return date

    def clean_start_date(self):
        if self.cleaned_data['start_date']:
            date = self.cleaned_data['start_date'].replace(tzinfo=None)
            if date < datetime.now():
                msg = 'Start date should be in future.'
                self._errors['start_date'] = [msg]
            return date

    def clean(self):
        # start_date = self.cleaned_data.get('start_date', None)
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']
        if start_date and end_date:
            if end_date < start_date:
                msg = 'End date should be greater than start date.'
                self._errors['end_date'] = [msg]
