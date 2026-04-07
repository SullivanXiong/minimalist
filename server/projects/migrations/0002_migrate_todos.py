"""Data migration: create default workspace, project, and statuses."""

from django.db import migrations


def create_defaults(apps, schema_editor):
    Workspace = apps.get_model('projects', 'Workspace')
    Project = apps.get_model('projects', 'Project')
    Status = apps.get_model('projects', 'Status')

    # Create default workspace
    workspace = Workspace.objects.create(
        name='Default',
        slug='default',
        identifier_prefix='MIN',
        issue_counter=0,
    )

    # Create default project (signals don't run in data migrations,
    # so we create statuses manually below)
    project = Project.objects.create(
        name='General',
        slug='general',
        workspace=workspace,
    )

    # Create default statuses manually (signals don't fire in migrations)
    default_statuses = [
        {'name': 'Backlog', 'category': 'backlog', 'color': '#6B7280', 'sort_order': 0},
        {'name': 'Todo', 'category': 'unstarted', 'color': '#6B7280', 'sort_order': 1, 'is_default': True},
        {'name': 'In Progress', 'category': 'started', 'color': '#F59E0B', 'sort_order': 2},
        {'name': 'In Review', 'category': 'started', 'color': '#3B82F6', 'sort_order': 3},
        {'name': 'Done', 'category': 'completed', 'color': '#10B981', 'sort_order': 4},
        {'name': 'Cancelled', 'category': 'cancelled', 'color': '#EF4444', 'sort_order': 5},
    ]

    for s in default_statuses:
        Status.objects.create(project=project, **s)


def reverse_migration(apps, schema_editor):
    """Remove default data."""
    Issue = apps.get_model('projects', 'Issue')
    Status = apps.get_model('projects', 'Status')
    Project = apps.get_model('projects', 'Project')
    Workspace = apps.get_model('projects', 'Workspace')

    Issue.objects.filter(workspace__slug='default').delete()
    Status.objects.filter(project__slug='general', project__workspace__slug='default').delete()
    Project.objects.filter(slug='general', workspace__slug='default').delete()
    Workspace.objects.filter(slug='default').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_defaults, reverse_migration),
    ]
