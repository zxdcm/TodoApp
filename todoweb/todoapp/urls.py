from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'todoapp'

users_patterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'todoapp:index'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup')
]

tasks_patterns =[
    url(r'^$', views.tasks, name='tasks'),
    url(r'^(?P<id>[0-9]+)/$', views.show_task, name='show_task'),
    url(r'^add/$', views.create_task, name='add_task'),
    url(r'^edit/(?P<id>[0-9]+)/$', views.edit_task, name='edit_task'),
    url(r'^delete/^(?P<id>[0-9]+)/$', views.delete_task, name='delete_task'),
    url(r'^own/$', views.own_tasks, name='own_tasks'),
    url(r'^assigned/$', views.assigned_tasks, name='assigned_tasks'),
    url(r'^archived/$', views.archived_tasks, name='archived_tasks'),
    url(r'^done/$', views.done_tasks, name='done_tasks'),
    url(r'^available/$', views.available_tasks, name='available_tasks'),
    url(r'^folder_tasks/(?P<id>[0-9]+)$', views.folder_tasks, name='folder_tasks'),
]

folder_patterns = [
    url(r'^add/$', views.add_folder, name='add_folder'),
    url(r'^edit/$', views.add_folder, name='edit_folder')
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'tasks/', include(tasks_patterns), name='tasks'),
    url(r'users/', include(users_patterns), name='users'),
    url(r'folder/', include(folder_patterns), name='folders')
]
