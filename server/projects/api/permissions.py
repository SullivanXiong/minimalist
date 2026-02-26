"""Workspace-scoped permissions for the projects API."""

from rest_framework.permissions import BasePermission

from projects.models import Workspace


class WorkspaceScoped(BasePermission):
    """Ensure the request targets a valid workspace."""

    def has_permission(self, request, view):
        workspace_slug = view.kwargs.get('workspace_slug')
        if not workspace_slug:
            return False
        return Workspace.objects.filter(slug=workspace_slug).exists()
