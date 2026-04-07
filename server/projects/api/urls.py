"""DRF router for versioned API endpoints."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'workspaces', views.WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'workspaces/<slug:workspace_slug>/projects/',
        views.ProjectViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='project-list',
    ),
    path(
        'workspaces/<slug:workspace_slug>/projects/<uuid:pk>/',
        views.ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='project-detail',
    ),
    path(
        'workspaces/<slug:workspace_slug>/projects/<uuid:project_pk>/statuses/',
        views.StatusViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='status-list',
    ),
    path(
        'workspaces/<slug:workspace_slug>/projects/<uuid:project_pk>/statuses/<uuid:pk>/',
        views.StatusViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='status-detail',
    ),
    path(
        'workspaces/<slug:workspace_slug>/labels/',
        views.LabelViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='label-list',
    ),
    path(
        'workspaces/<slug:workspace_slug>/labels/<uuid:pk>/',
        views.LabelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='label-detail',
    ),
    path(
        'workspaces/<slug:workspace_slug>/issues/',
        views.IssueViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='issue-list',
    ),
    path(
        'workspaces/<slug:workspace_slug>/issues/<uuid:pk>/',
        views.IssueViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='issue-detail',
    ),
    path(
        'workspaces/<slug:workspace_slug>/issues/<uuid:pk>/move/',
        views.IssueViewSet.as_view({'post': 'move'}),
        name='issue-move',
    ),
]
