from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, Status

DEFAULT_STATUSES = [
    {'name': 'Backlog', 'category': 'backlog', 'color': '#6B7280', 'sort_order': 0},
    {'name': 'Todo', 'category': 'unstarted', 'color': '#6B7280', 'sort_order': 1, 'is_default': True},
    {'name': 'In Progress', 'category': 'started', 'color': '#F59E0B', 'sort_order': 2},
    {'name': 'In Review', 'category': 'started', 'color': '#3B82F6', 'sort_order': 3},
    {'name': 'Done', 'category': 'completed', 'color': '#10B981', 'sort_order': 4},
    {'name': 'Cancelled', 'category': 'cancelled', 'color': '#EF4444', 'sort_order': 5},
]


@receiver(post_save, sender=Project)
def create_default_statuses(sender, instance, created, **kwargs):
    """Auto-create default statuses when a new project is created."""
    if not created:
        return

    for status_data in DEFAULT_STATUSES:
        Status.objects.create(project=instance, **status_data)
