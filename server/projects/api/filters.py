"""Filter backends for the projects API."""

from rest_framework.filters import BaseFilterBackend


class IssueFilter(BaseFilterBackend):
    """Filter issues by project, status, priority, and label."""

    def filter_queryset(self, request, queryset, view):
        project_id = request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        status_id = request.query_params.get('status_id')
        if status_id:
            queryset = queryset.filter(status_id=status_id)

        priority = request.query_params.get('priority')
        if priority is not None:
            queryset = queryset.filter(priority=priority)

        label_id = request.query_params.get('label_id')
        if label_id:
            queryset = queryset.filter(labels__id=label_id)

        return queryset
