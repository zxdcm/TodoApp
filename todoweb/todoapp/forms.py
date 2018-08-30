from datetime import datetime, timedelta
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from todolib.models import TaskStatus, TaskPriority
from todoapp import get_service

class TaskForm(forms.Form):
    def __init__(self, user, task_id, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

    name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'placeholder': 'Task name'}))
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Task description'}))
    priority = forms.ChoiceField(
        choices=[(priority.value, priority.value) for priority in TaskPriority]
    )
    status = forms.ChoiceField(
        choices=[(status.value, status.value) for status in TaskStatus]
    )
    event = forms.BooleanField(initial=False, required=False)
    start_date = forms.DateTimeField(required=False, initial=datetime.now())
    end_date = forms.DateTimeField(required=False,
                                   initial=datetime.now() + timedelta(days=1))
    assigned = forms.ModelChoiceField(queryset=User.objects.all(),
                                      required=False)
    folders = forms.ModelMultipleChoiceField(User.objects.all())

