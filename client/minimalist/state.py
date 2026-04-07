"""Centralized application state management."""

from .models import Issue, Label, Project, Workspace


class AppState:
    """Holds all application state — workspace, projects, issues, etc."""

    def __init__(self):
        self.workspace = None
        self.projects = []
        self.labels = []
        self.issues = []
        self.selected_project_id = None
        self.selected_issue_id = None
        self.view_mode = 'board'

    def set_workspace(self, data):
        """Set workspace from server workspace.state message."""
        self.workspace = Workspace.from_dict(data['workspace'])
        self.projects = [Project.from_dict(p) for p in data.get('projects', [])]
        self.labels = [Label.from_dict(l) for l in data.get('labels', [])]

        # Auto-select first project if none selected
        if not self.selected_project_id and self.projects:
            self.selected_project_id = self.projects[0].id

    def set_issues(self, issues_data):
        """Set issues from server issue.list message."""
        self.issues = [Issue.from_dict(i) for i in issues_data]

    def add_issue(self, issue_data):
        """Add a newly created issue."""
        issue = Issue.from_dict(issue_data)
        self.issues.insert(0, issue)
        return issue

    def update_issue(self, issue_data):
        """Update an existing issue in place."""
        issue = Issue.from_dict(issue_data)
        for i, existing in enumerate(self.issues):
            if existing.id == issue.id:
                self.issues[i] = issue
                return issue
        # Not found locally, add it
        self.issues.insert(0, issue)
        return issue

    def remove_issue(self, issue_id):
        """Remove an issue by ID."""
        self.issues = [i for i in self.issues if i.id != issue_id]

    def add_project(self, project_data):
        project = Project.from_dict(project_data)
        self.projects.append(project)
        return project

    def update_project(self, project_data):
        project = Project.from_dict(project_data)
        for i, existing in enumerate(self.projects):
            if existing.id == project.id:
                self.projects[i] = project
                return project
        self.projects.append(project)
        return project

    def remove_project(self, project_id):
        self.projects = [p for p in self.projects if p.id != project_id]
        if self.selected_project_id == project_id:
            self.selected_project_id = self.projects[0].id if self.projects else None

    def add_label(self, label_data):
        label = Label.from_dict(label_data)
        self.labels.append(label)
        return label

    def update_label(self, label_data):
        label = Label.from_dict(label_data)
        for i, existing in enumerate(self.labels):
            if existing.id == label.id:
                self.labels[i] = label
                return label
        self.labels.append(label)
        return label

    def remove_label(self, label_id):
        self.labels = [l for l in self.labels if l.id != label_id]

    def get_selected_project(self):
        if not self.selected_project_id:
            return None
        for p in self.projects:
            if p.id == self.selected_project_id:
                return p
        return None

    def get_selected_issue(self):
        if not self.selected_issue_id:
            return None
        for i in self.issues:
            if i.id == self.selected_issue_id:
                return i
        return None

    def get_project_issues(self, project_id=None):
        """Get issues for a specific project (or selected project)."""
        pid = project_id or self.selected_project_id
        if not pid:
            return self.issues
        return [i for i in self.issues if i.project_id == pid]

    def get_status(self, status_id):
        """Find a status by ID across all projects."""
        for project in self.projects:
            for status in project.statuses:
                if status.id == status_id:
                    return status
        return None

    def get_label(self, label_id):
        for label in self.labels:
            if label.id == label_id:
                return label
        return None
