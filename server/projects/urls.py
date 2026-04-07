from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('workspaces/', views.workspace_list, name='workspace_list'),
    path('workspaces/<slug:slug>/', views.workspace_detail, name='workspace_detail'),
    path('workspaces/<slug:slug>/projects/', views.project_list, name='project_list'),
    path('workspaces/<slug:slug>/issues/', views.issue_list, name='issue_list'),
    path('workspaces/<slug:slug>/issues/<uuid:issue_id>/', views.issue_detail, name='issue_detail'),
    path('workspaces/<slug:slug>/labels/', views.label_list, name='label_list'),
    path('workspaces/<slug:slug>/labels/<uuid:label_id>/', views.label_detail, name='label_detail'),
    path('workspaces/<slug:slug>/projects/<uuid:project_id>/statuses/', views.status_list, name='status_list'),
    path('workspaces/<slug:slug>/projects/<uuid:project_id>/statuses/<uuid:status_id>/', views.status_detail, name='status_detail'),
]
