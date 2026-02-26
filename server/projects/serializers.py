"""Serialization helpers that add computed fields on top of model.to_dict()."""

from .models import Issue, Label, Project, Status, Workspace


def serialize_workspace(workspace):
    return workspace.to_dict()


def serialize_project(project, include_statuses=False):
    data = project.to_dict()
    if include_statuses:
        data['statuses'] = [
            serialize_status(s) for s in project.statuses.all()
        ]
    return data


def serialize_status(status):
    return status.to_dict()


def serialize_label(label):
    return label.to_dict()


def serialize_issue(issue):
    data = issue.to_dict()
    return data


def serialize_workspace_state(workspace):
    """Full workspace context sent on connection."""
    projects = []
    for project in workspace.projects.prefetch_related('statuses').all():
        projects.append(serialize_project(project, include_statuses=True))

    labels = [serialize_label(l) for l in workspace.labels.all()]

    return {
        'workspace': serialize_workspace(workspace),
        'projects': projects,
        'labels': labels,
    }
