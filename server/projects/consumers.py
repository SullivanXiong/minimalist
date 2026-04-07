import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from . import services
from .models import Issue, Label, Project, Status, Workspace
from .serializers import (
    serialize_issue,
    serialize_label,
    serialize_project,
    serialize_status,
    serialize_workspace_state,
)


class WorkspaceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for workspace-scoped real-time operations."""

    async def connect(self):
        self.workspace_slug = self.scope['url_route']['kwargs']['workspace_slug']
        self.group_name = f"workspace_{self.workspace_slug}"

        # Reject unauthenticated connections before accepting
        if getattr(settings, 'AUTH_REQUIRED', False):
            user = self.scope.get('user')
            if not user or not user.is_authenticated:
                await self.close(code=4001)
                return

        workspace = await self.get_workspace()
        if workspace is None:
            await self.close()
            return

        self.workspace_id = workspace.id

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        state = await self.get_workspace_state()
        await self.send(text_data=json.dumps({
            'type': 'workspace.state',
            'data': state,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            msg_type = message.get('type')
            msg_data = message.get('data', {})
            request_id = message.get('request_id')

            handler = {
                'workspace.get': self.handle_workspace_get,
                'issue.list': self.handle_issue_list,
                'issue.create': self.handle_issue_create,
                'issue.update': self.handle_issue_update,
                'issue.move': self.handle_issue_move,
                'issue.delete': self.handle_issue_delete,
                'project.list': self.handle_project_list,
                'project.create': self.handle_project_create,
                'project.update': self.handle_project_update,
                'project.delete': self.handle_project_delete,
                'label.list': self.handle_label_list,
                'label.create': self.handle_label_create,
                'label.update': self.handle_label_update,
                'label.delete': self.handle_label_delete,
                'status.list': self.handle_status_list,
                'status.create': self.handle_status_create,
                'status.update': self.handle_status_update,
                'status.delete': self.handle_status_delete,
            }.get(msg_type)

            if handler is None:
                await self.send_error(f"Unknown message type: {msg_type}", request_id)
                return

            await handler(msg_data, request_id)

        except Exception as e:
            request_id = message.get('request_id') if 'message' in locals() else None
            await self.send_error(str(e), request_id)

    # --- Helpers ---

    async def send_message(self, msg_type, data, request_id=None):
        response = {'type': msg_type, 'data': data}
        if request_id:
            response['request_id'] = request_id
        await self.send(text_data=json.dumps(response))

    async def send_error(self, message, request_id=None):
        await self.send_message('error', {'message': message}, request_id)

    async def broadcast(self, msg_type, data):
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'workspace_broadcast', 'msg_type': msg_type, 'data': data}
        )

    async def workspace_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': event['msg_type'],
            'data': event['data'],
        }))

    # --- Workspace handlers ---

    async def handle_workspace_get(self, data, request_id):
        state = await self.get_workspace_state()
        await self.send_message('workspace.state', state, request_id)

    # --- Issue handlers ---

    async def handle_issue_list(self, data, request_id):
        issues = await self.get_issues(
            project_id=data.get('project_id'),
            status_id=data.get('status_id'),
            priority=data.get('priority'),
        )
        await self.send_message('issue.list', issues, request_id)

    async def handle_issue_create(self, data, request_id):
        issue = await self.create_issue(data)
        await self.broadcast('issue.created', issue)

    async def handle_issue_update(self, data, request_id):
        issue = await self.update_issue(data)
        await self.broadcast('issue.updated', issue)

    async def handle_issue_move(self, data, request_id):
        issue = await self.move_issue(data)
        await self.broadcast('issue.updated', issue)

    async def handle_issue_delete(self, data, request_id):
        issue_id = data.get('id')
        await self.delete_issue(issue_id)
        await self.broadcast('issue.deleted', {'id': issue_id})

    # --- Project handlers ---

    async def handle_project_list(self, data, request_id):
        projects = await self.get_projects()
        await self.send_message('project.list', projects, request_id)

    async def handle_project_create(self, data, request_id):
        project = await self.create_project(data)
        await self.broadcast('project.created', project)

    async def handle_project_update(self, data, request_id):
        project = await self.update_project(data)
        await self.broadcast('project.updated', project)

    async def handle_project_delete(self, data, request_id):
        project_id = data.get('id')
        await self.delete_project(project_id)
        await self.broadcast('project.deleted', {'id': project_id})

    # --- Label handlers ---

    async def handle_label_list(self, data, request_id):
        labels = await self.get_labels()
        await self.send_message('label.list', labels, request_id)

    async def handle_label_create(self, data, request_id):
        label = await self.create_label(data)
        await self.broadcast('label.created', label)

    async def handle_label_update(self, data, request_id):
        label = await self.update_label(data)
        await self.broadcast('label.updated', label)

    async def handle_label_delete(self, data, request_id):
        label_id = data.get('id')
        await self.delete_label(label_id)
        await self.broadcast('label.deleted', {'id': label_id})

    # --- Status handlers ---

    async def handle_status_list(self, data, request_id):
        project_id = data.get('project_id')
        statuses = await self.get_statuses(project_id)
        await self.send_message('status.list', statuses, request_id)

    async def handle_status_create(self, data, request_id):
        status = await self.create_status(data)
        await self.broadcast('status.created', status)

    async def handle_status_update(self, data, request_id):
        status = await self.update_status(data)
        await self.broadcast('status.updated', status)

    async def handle_status_delete(self, data, request_id):
        status_id = data.get('id')
        move_to_id = data.get('move_to_id')
        await self.delete_status_db(status_id, move_to_id)
        await self.broadcast('status.deleted', {'id': status_id, 'move_to_id': move_to_id})

    # --- Database operations ---

    @database_sync_to_async
    def get_workspace(self):
        try:
            return Workspace.objects.get(slug=self.workspace_slug)
        except Workspace.DoesNotExist:
            return None

    @database_sync_to_async
    def get_workspace_state(self):
        workspace = Workspace.objects.get(pk=self.workspace_id)
        return serialize_workspace_state(workspace)

    @database_sync_to_async
    def get_issues(self, project_id=None, status_id=None, priority=None):
        qs = Issue.objects.filter(
            workspace_id=self.workspace_id
        ).select_related('status').prefetch_related('labels')

        if project_id:
            qs = qs.filter(project_id=project_id)
        if status_id:
            qs = qs.filter(status_id=status_id)
        if priority is not None:
            qs = qs.filter(priority=priority)

        return [serialize_issue(issue) for issue in qs]

    @database_sync_to_async
    def create_issue(self, data):
        workspace = Workspace.objects.get(pk=self.workspace_id)
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
        if 'sort_order' in data:
            kwargs['sort_order'] = data['sort_order']

        issue = services.create_issue(
            workspace=workspace,
            project=project,
            title=data['title'],
            **kwargs,
        )

        if 'label_ids' in data:
            issue.labels.set(data['label_ids'])

        # Re-fetch for full serialization
        issue = Issue.objects.select_related('status').prefetch_related(
            'labels', 'sub_issues'
        ).get(pk=issue.pk)
        return serialize_issue(issue)

    @database_sync_to_async
    def update_issue(self, data):
        issue = Issue.objects.get(pk=data['id'], workspace_id=self.workspace_id)

        for field in ('title', 'description', 'priority', 'estimate', 'sort_order'):
            if field in data:
                setattr(issue, field, data[field])

        if 'status_id' in data:
            issue.status_id = data['status_id']
        if 'parent_id' in data:
            issue.parent_id = data['parent_id'] or None
        if 'project_id' in data:
            issue.project_id = data['project_id']

        issue.save()

        if 'label_ids' in data:
            issue.labels.set(data['label_ids'])

        issue = Issue.objects.select_related('status').prefetch_related(
            'labels', 'sub_issues'
        ).get(pk=issue.pk)
        return serialize_issue(issue)

    @database_sync_to_async
    def move_issue(self, data):
        issue = Issue.objects.select_related('status').get(
            pk=data['id'], workspace_id=self.workspace_id
        )
        new_status = Status.objects.get(pk=data['status_id'])
        sort_order = data.get('sort_order')
        issue = services.move_issue(issue, new_status, sort_order)

        issue = Issue.objects.select_related('status').prefetch_related(
            'labels', 'sub_issues'
        ).get(pk=issue.pk)
        return serialize_issue(issue)

    @database_sync_to_async
    def delete_issue(self, issue_id):
        Issue.objects.filter(pk=issue_id, workspace_id=self.workspace_id).delete()

    @database_sync_to_async
    def get_projects(self):
        projects = Project.objects.filter(
            workspace_id=self.workspace_id
        ).prefetch_related('statuses')
        return [serialize_project(p, include_statuses=True) for p in projects]

    @database_sync_to_async
    def create_project(self, data):
        workspace = Workspace.objects.get(pk=self.workspace_id)
        project = Project.objects.create(
            workspace=workspace,
            name=data['name'],
            slug=data.get('slug', data['name'].lower().replace(' ', '-')),
            description=data.get('description', ''),
            icon=data.get('icon', ''),
            color=data.get('color', '#6B7280'),
        )
        project = Project.objects.prefetch_related('statuses').get(pk=project.pk)
        return serialize_project(project, include_statuses=True)

    @database_sync_to_async
    def update_project(self, data):
        project = Project.objects.get(
            pk=data['id'], workspace_id=self.workspace_id
        )
        for field in ('name', 'slug', 'description', 'icon', 'color', 'sort_order'):
            if field in data:
                setattr(project, field, data[field])
        project.save()
        project = Project.objects.prefetch_related('statuses').get(pk=project.pk)
        return serialize_project(project, include_statuses=True)

    @database_sync_to_async
    def delete_project(self, project_id):
        Project.objects.filter(
            pk=project_id, workspace_id=self.workspace_id
        ).delete()

    @database_sync_to_async
    def get_labels(self):
        labels = Label.objects.filter(workspace_id=self.workspace_id)
        return [serialize_label(l) for l in labels]

    @database_sync_to_async
    def create_label(self, data):
        workspace = Workspace.objects.get(pk=self.workspace_id)
        label = Label.objects.create(
            workspace=workspace,
            name=data['name'],
            color=data.get('color', '#6B7280'),
            description=data.get('description', ''),
        )
        return serialize_label(label)

    @database_sync_to_async
    def update_label(self, data):
        label = Label.objects.get(pk=data['id'], workspace_id=self.workspace_id)
        for field in ('name', 'color', 'description'):
            if field in data:
                setattr(label, field, data[field])
        label.save()
        return serialize_label(label)

    @database_sync_to_async
    def delete_label(self, label_id):
        Label.objects.filter(pk=label_id, workspace_id=self.workspace_id).delete()

    @database_sync_to_async
    def get_statuses(self, project_id):
        qs = Status.objects.filter(project__workspace_id=self.workspace_id)
        if project_id:
            qs = qs.filter(project_id=project_id)
        return [serialize_status(s) for s in qs]

    @database_sync_to_async
    def create_status(self, data):
        project = Project.objects.get(
            pk=data['project_id'], workspace_id=self.workspace_id
        )
        status = Status.objects.create(
            project=project,
            name=data['name'],
            category=data.get('category', 'unstarted'),
            color=data.get('color', '#6B7280'),
            sort_order=data.get('sort_order', 0),
            is_default=data.get('is_default', False),
        )
        return serialize_status(status)

    @database_sync_to_async
    def update_status(self, data):
        status = Status.objects.get(
            pk=data['id'], project__workspace_id=self.workspace_id
        )
        for field in ('name', 'category', 'color', 'sort_order', 'is_default'):
            if field in data:
                setattr(status, field, data[field])
        status.save()
        return serialize_status(status)

    @database_sync_to_async
    def delete_status_db(self, status_id, move_to_id):
        status = Status.objects.get(
            pk=status_id, project__workspace_id=self.workspace_id
        )
        move_to = Status.objects.get(
            pk=move_to_id, project__workspace_id=self.workspace_id
        )
        services.delete_status(status, move_to)
