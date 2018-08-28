from django.conf.urls import url, include

from . import views

app_name = 'todoapp'

tasks_patterns =[
    url(r'^$', views.tasks, name='tasks'),
    url(r'^new/$', views.create_task, name='new_task'),
    url(r'^(?P<id>[0-9]+)/$', views.show_task, name='show_task'),
    url(r'^(?P<id>[0-9]+)/$', views.edit_task, name='edit_task'),
    url(r'^(?P<id>[0-9]+)/$', views.delete_task, name='delete_task'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'tasks/', include(tasks_patterns), name='tasks'),
    url(r'folders$', views.folders, name='folders'),
]
