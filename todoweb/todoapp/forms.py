from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.models import User
from todolib.models import TaskStatus, TaskPriority
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
    start_date = forms.DateTimeField(required=False, initial=datetime.now())
    end_date = forms.DateTimeField(required=False,
                                   initial=datetime.now() + timedelta(days=1))

    assigned = forms.ModelChoiceField(User.objects.all(), required=False)
    folders = forms.MultipleChoiceField(required=False)

    def clean_folders(self):
        data = [*map(int, self.cleaned_data['folders'])]
        if 0 in data:
            data.remove(0)
        return data


class FolderForm(forms.Form):
    name = forms.CharField(max_length=20,
                           widget=forms.TextInput(
                            attrs={'placeholder': 'folder name'}))

    
class SubTaskForm(forms.Form):

    task_id = forms.ChoiceField()

    def __init__(self, user, *args, **kwargs):
        super(SubTaskForm, self).__init__(*args, **kwargs)
        tasks = get_service().get_filtered_tasks(
            user=user,
            parentless=True,
            planless=True,
        )

        choices = ((task.id, f'ID: {task.id} Name: {task.name}') for task in tasks
                   if task.status != TaskStatus.ARCHIVED)
        self.fields['task_id'] = forms.ChoiceField(choices=choices)


    def clean_task_id(self):
        return int(self.cleaned_data['task_id'])
    
    
class MemberForm(forms.Form):
    member = forms.ModelChoiceField(User.objects.all(), required=True)
    