"""DRF ViewSets for the projects API."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from projects import services
from projects.models import Issue, Label, Project, Status, Workspace

from .filters import IssueFilter
from .serializers import (
    IssueCreateSerializer,
    IssueSerializer,
    LabelSerializer,
    ProjectCreateSerializer,
    ProjectSerializer,
    StatusSerializer,
    WorkspaceSerializer,
)


class WorkspaceViewSet(viewsets.ModelViewSet):
    """CRUD for workspaces."""
    serializer_class = WorkspaceSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Workspace.objects.all()


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD for projects within a workspace."""

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_queryset(self):
        workspace_slug = self.kwargs['workspace_slug']
        return Project.objects.filter(
            workspace__slug=workspace_slug
        ).prefetch_related('statuses')

    def perform_create(self, serializer):
        workspace = Workspace.objects.get(slug=self.kwargs['workspace_slug'])
        serializer.save(workspace=workspace)


class StatusViewSet(viewsets.ModelViewSet):
    """CRUD for statuses within a project."""
    serializer_class = StatusSerializer

    def get_queryset(self):
        return Status.objects.filter(
            project_id=self.kwargs['project_pk'],
            project__workspace__slug=self.kwargs['workspace_slug'],
        )

    def perform_create(self, serializer):
        project = Project.objects.get(
            pk=self.kwargs['project_pk'],
            workspace__slug=self.kwargs['workspace_slug'],
        )
        serializer.save(project=project)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        move_to_id = request.data.get('move_to_id')
        if not move_to_id:
            return Response(
                {'error': 'move_to_id required when deleting status'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            move_to = Status.objects.get(
                pk=move_to_id,
                project__workspace__slug=self.kwargs['workspace_slug'],
            )
        except Status.DoesNotExist:
            return Response(
                {'error': 'Target status not found in this workspace'},
                status=status.HTTP_404_NOT_FOUND,
            )
        services.delete_status(instance, move_to)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LabelViewSet(viewsets.ModelViewSet):
    """CRUD for labels within a workspace."""
    serializer_class = LabelSerializer

    def get_queryset(self):
        return Label.objects.filter(
            workspace__slug=self.kwargs['workspace_slug']
        )

    def perform_create(self, serializer):
        workspace = Workspace.objects.get(slug=self.kwargs['workspace_slug'])
        serializer.save(workspace=workspace)


class IssueViewSet(viewsets.ModelViewSet):
    """CRUD for issues within a workspace."""
    serializer_class = IssueSerializer
    filter_backends = [IssueFilter]

    def get_queryset(self):
        return Issue.objects.filter(
            workspace__slug=self.kwargs['workspace_slug']
        ).select_related('status').prefetch_related('labels', 'sub_issues')

    def create(self, request, *args, **kwargs):
        serializer = IssueCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        workspace_slug = self.kwargs['workspace_slug']
        try:
            workspace = Workspace.objects.get(slug=workspace_slug)
        except Workspace.DoesNotExist:
            return Response(
                {'error': 'Workspace not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            project = Project.objects.get(
                pk=data['project_id'], workspace=workspace,
            )
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found in this workspace'},
                status=status.HTTP_404_NOT_FOUND,
            )

        kwargs_create = {
            'description': data.get('description', ''),
            'priority': data.get('priority', 0),
            'sort_order': data.get('sort_order', 0),
        }
        if data.get('estimate') is not None:
            kwargs_create['estimate'] = data['estimate']
        if data.get('parent_id'):
            kwargs_create['parent_id'] = str(data['parent_id'])
        if data.get('status_id'):
            try:
                kwargs_create['status'] = Status.objects.get(
                    pk=data['status_id'],
                    project__workspace=workspace,
                )
            except Status.DoesNotExist:
                return Response(
                    {'error': 'Status not found in this workspace'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        issue = services.create_issue(
            workspace=workspace,
            project=project,
            title=data['title'],
            **kwargs_create,
        )

        if data.get('label_ids'):
            issue.labels.set(data['label_ids'])

        issue = Issue.objects.select_related('status').prefetch_related(
            'labels', 'sub_issues'
        ).get(pk=issue.pk)

        return Response(
            IssueSerializer(issue).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def move(self, request, *args, **kwargs):
        """Move an issue to a new status."""
        issue = self.get_object()
        status_id = request.data.get('status_id')
        sort_order = request.data.get('sort_order')

        if not status_id:
            return Response(
                {'error': 'status_id required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_status = Status.objects.get(
                pk=status_id,
                project__workspace__slug=self.kwargs['workspace_slug'],
            )
        except Status.DoesNotExist:
            return Response(
                {'error': 'Status not found in this workspace'},
                status=status.HTTP_404_NOT_FOUND,
            )

        issue = services.move_issue(issue, new_status, sort_order)

        issue = Issue.objects.select_related('status').prefetch_related(
            'labels', 'sub_issues'
        ).get(pk=issue.pk)

        return Response(IssueSerializer(issue).data)
