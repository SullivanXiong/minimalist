"""Client-side dataclasses matching server models."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Workspace:
    id: str = ''
    name: str = ''
    slug: str = ''
    identifier_prefix: str = ''
    issue_counter: int = 0
    description: str = ''
    icon: str = ''
    created_at: str = ''
    updated_at: str = ''

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            slug=data.get('slug', ''),
            identifier_prefix=data.get('identifier_prefix', ''),
            issue_counter=data.get('issue_counter', 0),
            description=data.get('description', ''),
            icon=data.get('icon', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
        )


@dataclass
class Status:
    id: str = ''
    project_id: str = ''
    name: str = ''
    category: str = ''
    color: str = '#6B7280'
    sort_order: float = 0
    is_default: bool = False
    created_at: str = ''

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', ''),
            project_id=data.get('project_id', ''),
            name=data.get('name', ''),
            category=data.get('category', ''),
            color=data.get('color', '#6B7280'),
            sort_order=data.get('sort_order', 0),
            is_default=data.get('is_default', False),
            created_at=data.get('created_at', ''),
        )


@dataclass
class Project:
    id: str = ''
    workspace_id: str = ''
    name: str = ''
    slug: str = ''
    description: str = ''
    icon: str = ''
    color: str = '#6B7280'
    sort_order: float = 0
    statuses: list = field(default_factory=list)
    created_at: str = ''
    updated_at: str = ''

    @classmethod
    def from_dict(cls, data):
        statuses = [
            Status.from_dict(s) for s in data.get('statuses', [])
        ]
        return cls(
            id=data.get('id', ''),
            workspace_id=data.get('workspace_id', ''),
            name=data.get('name', ''),
            slug=data.get('slug', ''),
            description=data.get('description', ''),
            icon=data.get('icon', ''),
            color=data.get('color', '#6B7280'),
            sort_order=data.get('sort_order', 0),
            statuses=statuses,
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
        )

    def get_default_status(self):
        for s in self.statuses:
            if s.is_default:
                return s
        return self.statuses[0] if self.statuses else None


@dataclass
class Label:
    id: str = ''
    workspace_id: str = ''
    name: str = ''
    color: str = '#6B7280'
    description: str = ''
    created_at: str = ''

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', ''),
            workspace_id=data.get('workspace_id', ''),
            name=data.get('name', ''),
            color=data.get('color', '#6B7280'),
            description=data.get('description', ''),
            created_at=data.get('created_at', ''),
        )


@dataclass
class Issue:
    id: str = ''
    identifier: str = ''
    number: int = 0
    workspace_id: str = ''
    project_id: str = ''
    status_id: str = ''
    parent_id: Optional[str] = None
    assignee_id: Optional[int] = None
    title: str = ''
    description: str = ''
    priority: int = 0
    estimate: Optional[int] = None
    labels: list = field(default_factory=list)
    sort_order: float = 0
    created_at: str = ''
    updated_at: str = ''
    completed_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    sub_issue_count: int = 0
    sub_issue_completed: int = 0

    @classmethod
    def from_dict(cls, data):
        labels = [
            Label.from_dict(l) for l in data.get('labels', [])
        ]
        return cls(
            id=data.get('id', ''),
            identifier=data.get('identifier', ''),
            number=data.get('number', 0),
            workspace_id=data.get('workspace_id', ''),
            project_id=data.get('project_id', ''),
            status_id=data.get('status_id', ''),
            parent_id=data.get('parent_id'),
            assignee_id=data.get('assignee_id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            priority=data.get('priority', 0),
            estimate=data.get('estimate'),
            labels=labels,
            sort_order=data.get('sort_order', 0),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            completed_at=data.get('completed_at'),
            cancelled_at=data.get('cancelled_at'),
            sub_issue_count=data.get('sub_issue_count', 0),
            sub_issue_completed=data.get('sub_issue_completed', 0),
        )
