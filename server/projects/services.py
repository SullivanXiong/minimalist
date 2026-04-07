from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Issue, Status, Workspace


def create_issue(workspace, project, title, **kwargs):
    """Create a new issue with an atomically assigned identifier."""
    with transaction.atomic():
        Workspace.objects.filter(pk=workspace.pk).update(
            issue_counter=F('issue_counter') + 1
        )
        workspace.refresh_from_db()
        number = workspace.issue_counter
        identifier = f"{workspace.identifier_prefix}-{number}"

        # Default to the project's default status
        status = kwargs.pop('status', None)
        if status is None:
            status = Status.objects.filter(
                project=project, is_default=True
            ).first()
            if status is None:
                status = Status.objects.filter(project=project).first()

        labels = kwargs.pop('labels', None)

        issue = Issue.objects.create(
            workspace=workspace,
            project=project,
            status=status,
            identifier=identifier,
            number=number,
            title=title,
            **kwargs,
        )

        if labels:
            issue.labels.set(labels)

        return issue


def move_issue(issue, new_status, sort_order=None):
    """Move an issue to a new status, updating timestamps accordingly."""
    now = timezone.now()
    issue.status = new_status

    if sort_order is not None:
        issue.sort_order = sort_order

    if new_status.category == 'completed':
        issue.completed_at = now
        issue.cancelled_at = None
    elif new_status.category == 'cancelled':
        issue.cancelled_at = now
        issue.completed_at = None
    else:
        issue.completed_at = None
        issue.cancelled_at = None

    issue.save()
    return issue


def delete_status(status, move_to_status):
    """Reassign all issues from a status before deleting it."""
    with transaction.atomic():
        status.issues.update(status=move_to_status)
        status.delete()
