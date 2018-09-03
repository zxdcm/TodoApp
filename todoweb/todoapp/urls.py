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
    url(r'^(?P<task_id>[0-9]+)/$', views.show_task, name='show_task'),
    url(r'^add/$', views.add_task, name='add_task'),
    url(r'^edit/(?P<task_id>[0-9]+)/$', views.edit_task, name='edit_task'),
    url(r'^delete/(?P<task_id>[0-9]+)/$', views.delete_task, name='delete_task'),
    url(r'^archive/(?P<task_id>[0-9]+)/$', views.archive_task, name='archive_task'),
    url(r'^done/(?P<task_id>[0-9]+)/$', views.done_task, name='done_task'),
    url(r'^add_subtask/(?P<parent_task_id>[0-9]+)/$', views.add_subtask, name='add_subtask'),
    url(r'^detach/(?P<task_id>[0-9]+)/$', views.detach_task, name='detach_task'),
    url(r'^share_task/(?P<task_id>[0-9]+)/', views.share_task, name='share_task'),
    url(r'^unshare_task/(?P<task_id>[0-9]+)/(?P<member>[\w\-]+)/$', views.unshare_task, name='unshare_task'),
    url(r'^own_tasks/$', views.own_tasks, name='own_tasks'),
    url(r'^assigned_tasks/$', views.assigned_tasks, name='assigned_tasks'),
    url(r'^archived_tasks/$', views.archived_tasks, name='archived_tasks'),
    url(r'^done_tasks/$', views.done_tasks, name='done_tasks'),
    url(r'^available_tasks/$', views.available_tasks, name='available_tasks'),
    url(r'^folder_tasks/(?P<folder_id>[0-9]+)$', views.folder_tasks, name='folder_tasks'),
]

folder_patterns = [
    url(r'^add/$', views.add_folder, name='add_folder'),
    url(r'^edit/(?P<folder_id>[0-9]+)/$', views.edit_folder, name='edit_folder'),
    url(r'^delete/(?P<folder_id>[0-9]+)/$', views.delete_folder, name='delete_folder'),
]

plan_patterns =[
    url(r'^$', views.plans, name='plans'),
    url(r'^(?P<plan_id>[0-9]+)/$', views.show_plan, name='show_plan'),
    url(r'^add/$', views.add_plan, name='add_plan'),
    url(r'^edit/(?P<plan_id>[0-9]+)/$', views.edit_plan, name='edit_plan'),
    url(r'^delete/(?P<plan_id>[0-9]+)/$', views.delete_plan, name='delete_plan'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'tasks/', include(tasks_patterns), name='tasks'),
    url(r'users/', include(users_patterns), name='users'),
    url(r'folders/', include(folder_patterns), name='folders'),
    url(r'plans/', include(plan_patterns), name='plans')
]
