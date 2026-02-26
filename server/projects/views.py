import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import services
from .models import Issue, Label, Project, Status, Workspace
from .serializers import (
    serialize_issue,
    serialize_label,
    serialize_project,
    serialize_status,
    serialize_workspace,
)


def _parse_body(request):
    """Parse JSON request body."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


def _get_workspace_or_404(slug):
    try:
        return Workspace.objects.get(slug=slug)
    except Workspace.DoesNotExist:
        return None


# --- Workspace endpoints ---

@csrf_exempt
@require_http_methods(["GET", "POST"])
def workspace_list(request):
    if request.method == 'GET':
        workspaces = Workspace.objects.all()
        return JsonResponse({
            'workspaces': [serialize_workspace(w) for w in workspaces]
        })

    data = _parse_body(request)
    workspace = Workspace.objects.create(
        name=data.get('name', ''),
        slug=data.get('slug', ''),
        identifier_prefix=data.get('identifier_prefix', ''),
        description=data.get('description', ''),
        icon=data.get('icon', ''),
    )
    return JsonResponse(serialize_workspace(workspace), status=201)


@require_http_methods(["GET"])
def workspace_detail(request, slug):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    projects = [
        serialize_project(p, include_statuses=True)
        for p in workspace.projects.prefetch_related('statuses').all()
    ]
    labels = [serialize_label(l) for l in workspace.labels.all()]

    return JsonResponse({
        'workspace': serialize_workspace(workspace),
        'projects': projects,
        'labels': labels,
    })


# --- Project endpoints ---

@csrf_exempt
@require_http_methods(["GET", "POST"])
def project_list(request, slug):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    if request.method == 'GET':
        projects = workspace.projects.prefetch_related('statuses').all()
        return JsonResponse({
            'projects': [serialize_project(p, include_statuses=True) for p in projects]
        })

    data = _parse_body(request)
    project = Project.objects.create(
        workspace=workspace,
        name=data.get('name', ''),
        slug=data.get('slug', data.get('name', '').lower().replace(' ', '-')),
        description=data.get('description', ''),
        icon=data.get('icon', ''),
        color=data.get('color', '#6B7280'),
    )
    project = Project.objects.prefetch_related('statuses').get(pk=project.pk)
    return JsonResponse(serialize_project(project, include_statuses=True), status=201)


# --- Issue endpoints ---

@csrf_exempt
@require_http_methods(["GET", "POST"])
def issue_list(request, slug):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    if request.method == 'GET':
        qs = Issue.objects.filter(
            workspace=workspace
        ).select_related('status').prefetch_related('labels', 'sub_issues')

        project_id = request.GET.get('project_id')
        if project_id:
            qs = qs.filter(project_id=project_id)

        status_id = request.GET.get('status_id')
        if status_id:
            qs = qs.filter(status_id=status_id)

        priority = request.GET.get('priority')
        if priority is not None:
            qs = qs.filter(priority=priority)

        label_id = request.GET.get('label_id')
        if label_id:
            qs = qs.filter(labels__id=label_id)

        # Pagination
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        total = qs.count()
        issues = qs[offset:offset + limit]

        return JsonResponse({
            'issues': [serialize_issue(i) for i in issues],
            'total': total,
            'limit': limit,
            'offset': offset,
        })

    data = _parse_body(request)
    project = Project.objects.get(pk=data['project_id'])

    kwargs = {}
    if 'description' in data:
        kwargs['description'] = data['description']
    if 'priority' in data:
        kwargs['priority'] = data['priority']
    if 'estimate' in data:
        kwargs['estimate'] = data['estimate']
    if 'parent_id' in data and data['parent_id']:
        kwargs['parent_id'] = data['parent_id']
    if 'status_id' in data:
        kwargs['status'] = Status.objects.get(pk=data['status_id'])

    issue = services.create_issue(
        workspace=workspace,
        project=project,
        title=data.get('title', ''),
        **kwargs,
    )

    if 'label_ids' in data:
        issue.labels.set(data['label_ids'])

    issue = Issue.objects.select_related('status').prefetch_related(
        'labels', 'sub_issues'
    ).get(pk=issue.pk)
    return JsonResponse(serialize_issue(issue), status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def issue_detail(request, slug, issue_id):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    try:
        issue = Issue.objects.select_related('status').prefetch_related(
            'labels', 'sub_issues'
        ).get(pk=issue_id, workspace=workspace)
    except Issue.DoesNotExist:
        return JsonResponse({'error': 'Issue not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse(serialize_issue(issue))

    if request.method == 'DELETE':
        issue.delete()
        return JsonResponse({'id': str(issue_id)})

    # PATCH
    data = _parse_body(request)
    for field in ('title', 'description', 'priority', 'estimate', 'sort_order'):
        if field in data:
            setattr(issue, field, data[field])

    if 'status_id' in data:
        new_status = Status.objects.get(pk=data['status_id'])
        services.move_issue(issue, new_status)
    else:
        issue.save()

    if 'label_ids' in data:
        issue.labels.set(data['label_ids'])

    issue.refresh_from_db()
    issue = Issue.objects.select_related('status').prefetch_related(
        'labels', 'sub_issues'
    ).get(pk=issue.pk)
    return JsonResponse(serialize_issue(issue))


# --- Label endpoints ---

@csrf_exempt
@require_http_methods(["GET", "POST"])
def label_list(request, slug):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    if request.method == 'GET':
        labels = workspace.labels.all()
        return JsonResponse({
            'labels': [serialize_label(l) for l in labels]
        })

    data = _parse_body(request)
    label = Label.objects.create(
        workspace=workspace,
        name=data.get('name', ''),
        color=data.get('color', '#6B7280'),
        description=data.get('description', ''),
    )
    return JsonResponse(serialize_label(label), status=201)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def label_detail(request, slug, label_id):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    try:
        label = Label.objects.get(pk=label_id, workspace=workspace)
    except Label.DoesNotExist:
        return JsonResponse({'error': 'Label not found'}, status=404)

    if request.method == 'DELETE':
        label.delete()
        return JsonResponse({'id': str(label_id)})

    data = _parse_body(request)
    for field in ('name', 'color', 'description'):
        if field in data:
            setattr(label, field, data[field])
    label.save()
    return JsonResponse(serialize_label(label))


# --- Status endpoints ---

@csrf_exempt
@require_http_methods(["GET", "POST"])
def status_list(request, slug, project_id):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    try:
        project = Project.objects.get(pk=project_id, workspace=workspace)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

    if request.method == 'GET':
        statuses = project.statuses.all()
        return JsonResponse({
            'statuses': [serialize_status(s) for s in statuses]
        })

    data = _parse_body(request)
    status = Status.objects.create(
        project=project,
        name=data.get('name', ''),
        category=data.get('category', 'unstarted'),
        color=data.get('color', '#6B7280'),
        sort_order=data.get('sort_order', 0),
        is_default=data.get('is_default', False),
    )
    return JsonResponse(serialize_status(status), status=201)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def status_detail(request, slug, project_id, status_id):
    workspace = _get_workspace_or_404(slug)
    if workspace is None:
        return JsonResponse({'error': 'Workspace not found'}, status=404)

    try:
        status = Status.objects.get(
            pk=status_id, project_id=project_id,
            project__workspace=workspace
        )
    except Status.DoesNotExist:
        return JsonResponse({'error': 'Status not found'}, status=404)

    if request.method == 'DELETE':
        data = _parse_body(request)
        move_to_id = data.get('move_to_id')
        if not move_to_id:
            return JsonResponse(
                {'error': 'move_to_id required when deleting status'}, status=400
            )
        move_to = Status.objects.get(pk=move_to_id)
        services.delete_status(status, move_to)
        return JsonResponse({'id': str(status_id)})

    data = _parse_body(request)
    for field in ('name', 'category', 'color', 'sort_order', 'is_default'):
        if field in data:
            setattr(status, field, data[field])
    status.save()
    return JsonResponse(serialize_status(status))
