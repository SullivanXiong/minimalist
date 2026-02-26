import uuid

from django.conf import settings
from django.db import models


class Workspace(models.Model):
    """Top-level organizational unit (e.g., Work, Personal)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)
    identifier_prefix = models.CharField(max_length=10, unique=True)
    issue_counter = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=10, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'slug': self.slug,
            'identifier_prefix': self.identifier_prefix,
            'issue_counter': self.issue_counter,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Project(models.Model):
    """A project within a workspace, grouping related issues."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='projects'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=10, blank=True, default='')
    color = models.CharField(max_length=7, default='#6B7280')
    sort_order = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = [('workspace', 'slug')]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': str(self.id),
            'workspace_id': str(self.workspace_id),
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Status(models.Model):
    """Issue status within a project (e.g., Backlog, In Progress, Done)."""

    CATEGORY_CHOICES = [
        ('backlog', 'Backlog'),
        ('unstarted', 'Unstarted'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='statuses'
    )
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    color = models.CharField(max_length=7, default='#6B7280')
    sort_order = models.FloatField(default=0)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order']
        unique_together = [('project', 'name')]
        verbose_name_plural = 'statuses'

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'name': self.name,
            'category': self.category,
            'color': self.color,
            'sort_order': self.sort_order,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
        }


class Label(models.Model):
    """Workspace-scoped label for categorizing issues."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='labels'
    )
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#6B7280')
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = [('workspace', 'name')]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': str(self.id),
            'workspace_id': str(self.workspace_id),
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }


class Issue(models.Model):
    """An issue (task/ticket) within a project."""

    PRIORITY_CHOICES = [
        (0, 'No Priority'),
        (1, 'Urgent'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifier = models.CharField(max_length=20, unique=True)
    number = models.PositiveIntegerField()
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name='issues'
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='issues'
    )
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT, related_name='issues'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='sub_issues'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_issues'
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default='')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=0)
    estimate = models.PositiveIntegerField(null=True, blank=True)
    labels = models.ManyToManyField(Label, blank=True, related_name='issues')
    sort_order = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f"{self.identifier}: {self.title}"

    def to_dict(self):
        return {
            'id': str(self.id),
            'identifier': self.identifier,
            'number': self.number,
            'workspace_id': str(self.workspace_id),
            'project_id': str(self.project_id),
            'status_id': str(self.status_id),
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'assignee_id': self.assignee_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'estimate': self.estimate,
            'labels': [label.to_dict() for label in self.labels.all()],
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'sub_issue_count': self.sub_issues.count(),
            'sub_issue_completed': self.sub_issues.filter(
                status__category='completed'
            ).count(),
        }
