"""Main application frame — orchestrates all views and connections."""

import wx

try:
    from supyx.wxnavimgation import VimNavigationMixin
    HAS_VIM_NAV = True
except ImportError:
    HAS_VIM_NAV = False
    VimNavigationMixin = object

from .config import AUTH_REQUIRED, DEFAULT_WORKSPACE_SLUG
from .connection import WebSocketConnection
from .dialogs.issue import IssueCreateDialog
from .dialogs.project import ProjectDialog
from .dialogs.workspace import WorkspaceDialog
from .state import AppState
from .theme import DARK, PRIORITY, hex_to_wx, apply_dark_theme
from .utils.persistence import load_settings, save_settings
from .views.issue_detail import IssueDetailPanel
from .views.kanban import KanbanBoard
from .views.listview import IssueListView
from .views.sidebar import SidebarPanel
from .views.toolbar import ToolbarPanel


class MainFrame(VimNavigationMixin if HAS_VIM_NAV else object, wx.Frame):
    """Main application window with sidebar, toolbar, and content area."""

    def __init__(self):
        self.settings = load_settings()

        super().__init__(
            None,
            title="Minimalist",
            size=(self.settings['window_width'], self.settings['window_height']),
        )

        self.state = AppState()
        self.state.view_mode = self.settings.get('view_mode', 'board')
        self.connection = WebSocketConnection()
        self._detail_visible = False

        apply_dark_theme(self, 'bg_primary')
        self._init_ui()
        self._setup_connection_handlers()

        if HAS_VIM_NAV:
            self.init_vim_navigation()
            self._setup_keybindings()

        # Authenticate if required
        if AUTH_REQUIRED:
            from .auth import get_valid_token, LoginDialog
            wx.BeginBusyCursor()
            token = get_valid_token()
            wx.EndBusyCursor()
            if not token:
                dlg = LoginDialog(self)
                if dlg.ShowModal() != wx.ID_OK:
                    self.Destroy()
                    return
                dlg.Destroy()

        # Connect to last workspace
        workspace_slug = self.settings.get('last_workspace_slug', DEFAULT_WORKSPACE_SLUG)
        self.connection.connect(workspace_slug)

        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Show()

        # Check for updates (non-blocking)
        from .version import check_for_updates, __version__
        check_for_updates(self._on_update_check)

    def _init_ui(self):
        # Single top-level panel — no SplitterWindows at all
        main_panel = wx.Panel(self)
        apply_dark_theme(main_panel, 'bg_primary')
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Sidebar (fixed width)
        sidebar_width = self.settings.get('sidebar_width', 220)
        self.sidebar = SidebarPanel(
            main_panel, self.state,
            on_project_selected=self._on_project_selected,
            on_workspace_switch=self._on_workspace_switch,
        )
        self.sidebar.add_project_btn.Bind(wx.EVT_BUTTON, self._on_add_project)
        self.sidebar.SetMinSize((sidebar_width, -1))
        main_sizer.Add(self.sidebar, 0, wx.EXPAND)

        # 1px separator between sidebar and content
        sep = wx.Panel(main_panel, size=(1, -1))
        sep.SetBackgroundColour(hex_to_wx(DARK['border_primary']))
        main_sizer.Add(sep, 0, wx.EXPAND)

        # Right side: content + optional detail, managed via nested sizer
        self._right_panel = wx.Panel(main_panel)
        apply_dark_theme(self._right_panel, 'bg_primary')
        self._right_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Content panel holds toolbar + views
        self._content_panel = wx.Panel(self._right_panel)
        apply_dark_theme(self._content_panel, 'bg_primary')
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        # Toolbar
        self.toolbar = ToolbarPanel(
            self._content_panel, self.state,
            on_view_toggle=self._on_view_toggle,
            on_create_issue=self.on_create_issue,
            on_filter=None,
        )
        content_sizer.Add(self.toolbar, 0, wx.EXPAND)

        # View container (holds kanban or list)
        self.view_panel = wx.Panel(self._content_panel)
        apply_dark_theme(self.view_panel, 'bg_primary')
        self.view_sizer = wx.BoxSizer(wx.VERTICAL)

        # Kanban board
        self.kanban = KanbanBoard(
            self.view_panel, self.state,
            on_card_click=self._on_issue_selected,
            on_card_dclick=self._on_issue_activated,
        )
        self.view_sizer.Add(self.kanban, 1, wx.EXPAND)

        # List view
        self.listview = IssueListView(
            self.view_panel, self.state,
            on_issue_selected=self._on_issue_selected,
            on_issue_activated=self._on_issue_activated,
        )
        self.view_sizer.Add(self.listview, 1, wx.EXPAND)

        self.view_panel.SetSizer(self.view_sizer)
        content_sizer.Add(self.view_panel, 1, wx.EXPAND)
        self._content_panel.SetSizer(content_sizer)

        self._right_sizer.Add(self._content_panel, 1, wx.EXPAND)

        # Detail panel (hidden by default)
        self.detail_panel = IssueDetailPanel(
            self._right_panel, self.state, self.connection
        )
        self.detail_panel.Hide()
        # Separator before detail
        self._detail_sep = wx.Panel(self._right_panel, size=(1, -1))
        self._detail_sep.SetBackgroundColour(hex_to_wx(DARK['border_primary']))
        self._detail_sep.Hide()

        self._right_panel.SetSizer(self._right_sizer)

        main_sizer.Add(self._right_panel, 1, wx.EXPAND)
        main_panel.SetSizer(main_sizer)

        # Status bar
        self.CreateStatusBar(3)
        self.SetStatusWidths([-1, 150, 100])
        self.SetStatusText("Disconnected", 0)

        # Show correct view
        self._apply_view_mode()

    def _setup_connection_handlers(self):
        """Register WebSocket message handlers."""
        self.connection.on_status(self._on_connection_status)
        self.connection.on('workspace.state', self._on_workspace_state)
        self.connection.on('issue.list', self._on_issue_list)
        self.connection.on('issue.created', self._on_issue_created)
        self.connection.on('issue.updated', self._on_issue_updated)
        self.connection.on('issue.deleted', self._on_issue_deleted)
        self.connection.on('project.created', self._on_project_created)
        self.connection.on('project.updated', self._on_project_updated)
        self.connection.on('project.deleted', self._on_project_deleted)
        self.connection.on('label.created', self._on_label_created)
        self.connection.on('label.updated', self._on_label_updated)
        self.connection.on('label.deleted', self._on_label_deleted)
        self.connection.on('status.created', self._on_status_created)
        self.connection.on('error', self._on_error)

    def _setup_keybindings(self):
        """Configure vim keybindings."""
        from .keybindings import setup_keybindings
        setup_keybindings(self, self.vim_nav)

    # --- View management ---

    def _apply_view_mode(self):
        """Show the correct view (kanban or list) and hide the other."""
        if self.state.view_mode == 'board':
            self.kanban.Show()
            self.listview.Hide()
        else:
            self.kanban.Hide()
            self.listview.Show()
        self.view_panel.Layout()

    def _refresh_content(self):
        """Refresh all content views."""
        self.toolbar.refresh()
        self.kanban.refresh()
        self.listview.refresh()

        # Update status bar
        project = self.state.get_selected_project()
        issues = self.state.get_project_issues()
        if self.state.workspace:
            self.SetStatusText(f"Workspace: {self.state.workspace.name}", 1)
        if project:
            self.SetStatusText(f"{len(issues)} issues", 2)

    def _show_detail(self, issue_id):
        """Show the issue detail panel."""
        if not self._detail_visible:
            self._right_sizer.Add(self._detail_sep, 0, wx.EXPAND)
            self._right_sizer.Add(self.detail_panel, 0, wx.EXPAND)
            self.detail_panel.SetMinSize((350, -1))
            self._detail_sep.Show()
            self.detail_panel.Show()
            self._right_panel.Layout()
            self._detail_visible = True
        self.detail_panel.show_issue(issue_id)

    def _hide_detail(self):
        """Hide the issue detail panel."""
        if self._detail_visible:
            self._right_sizer.Detach(self.detail_panel)
            self._right_sizer.Detach(self._detail_sep)
            self.detail_panel.Hide()
            self._detail_sep.Hide()
            self._right_panel.Layout()
            self._detail_visible = False

    # --- Connection handlers ---

    def _on_connection_status(self, connected, message):
        self.SetStatusText(message, 0)

    def _on_workspace_state(self, data):
        self.state.set_workspace(data)

        # Restore last project selection
        last_project = self.settings.get('last_project_id')
        if last_project:
            for p in self.state.projects:
                if p.id == last_project:
                    self.state.selected_project_id = last_project
                    break

        self.sidebar.refresh()

        # Request issues for selected project
        if self.state.selected_project_id:
            self.connection.send('issue.list', {
                'project_id': self.state.selected_project_id,
            })
        else:
            self._refresh_content()

    def _on_issue_list(self, data):
        self.state.set_issues(data)
        self._refresh_content()

    def _on_issue_created(self, data):
        self.state.add_issue(data)
        self._refresh_content()

    def _on_issue_updated(self, data):
        self.state.update_issue(data)
        self._refresh_content()
        # Update detail panel if showing this issue
        if self._detail_visible and data.get('id') == self.state.selected_issue_id:
            self.detail_panel.show_issue(data['id'])

    def _on_issue_deleted(self, data):
        deleted_id = data.get('id')
        self.state.remove_issue(deleted_id)
        if self.state.selected_issue_id == deleted_id:
            self.state.selected_issue_id = None
            self._hide_detail()
        self._refresh_content()

    def _on_project_created(self, data):
        self.state.add_project(data)
        self.sidebar.refresh()

    def _on_project_updated(self, data):
        self.state.update_project(data)
        self.sidebar.refresh()
        self._refresh_content()

    def _on_project_deleted(self, data):
        self.state.remove_project(data.get('id'))
        self.sidebar.refresh()
        if self.state.selected_project_id:
            self.connection.send('issue.list', {
                'project_id': self.state.selected_project_id,
            })

    def _on_label_created(self, data):
        self.state.add_label(data)
        self.sidebar.refresh()

    def _on_label_updated(self, data):
        self.state.update_label(data)
        self.sidebar.refresh()

    def _on_label_deleted(self, data):
        self.state.remove_label(data.get('id'))
        self.sidebar.refresh()

    def _on_status_created(self, data):
        # Refresh workspace state to get updated statuses
        self.connection.send('workspace.get', {})

    def _on_error(self, data):
        wx.MessageBox(
            data.get('message', 'Unknown error'),
            "Error", wx.OK | wx.ICON_ERROR
        )

    # --- UI event handlers ---

    def _on_project_selected(self, project_id):
        self.state.selected_project_id = project_id
        self.state.selected_issue_id = None
        self._hide_detail()
        self.connection.send('issue.list', {'project_id': project_id})

    def _on_workspace_switch(self, workspace_slug):
        self.connection.connect(workspace_slug)
        self.settings['last_workspace_slug'] = workspace_slug

    def _on_view_toggle(self, mode):
        self.state.view_mode = mode
        self._apply_view_mode()
        self._refresh_content()

    def _on_issue_selected(self, issue_id):
        self.state.selected_issue_id = issue_id
        self.kanban.select_issue(issue_id)

    def _on_issue_activated(self, issue_id):
        self.state.selected_issue_id = issue_id
        self._show_detail(issue_id)

    def _on_add_project(self, event):
        dlg = ProjectDialog(self)
        if dlg.ShowModal() == wx.ID_OK and dlg.result:
            self.connection.send('project.create', dlg.result)
        dlg.Destroy()

    # --- Keybinding action handlers ---

    def on_create_issue(self, event=None):
        if not self.state.projects:
            return
        dlg = IssueCreateDialog(self, self.state)
        if dlg.ShowModal() == wx.ID_OK and dlg.result:
            self.connection.send('issue.create', dlg.result)
        dlg.Destroy()

    def on_edit_issue(self, event=None):
        issue = self.state.get_selected_issue()
        if not issue:
            return
        dlg = wx.TextEntryDialog(self, "Edit title:", "Edit Issue", issue.title)
        if dlg.ShowModal() == wx.ID_OK:
            new_title = dlg.GetValue().strip()
            if new_title:
                self.connection.send('issue.update', {
                    'id': issue.id,
                    'title': new_title,
                })
        dlg.Destroy()

    def on_delete_issue(self, event=None):
        issue = self.state.get_selected_issue()
        if not issue:
            return
        dlg = wx.MessageDialog(
            self, f"Delete {issue.identifier}?", "Confirm Delete",
            wx.YES_NO | wx.ICON_QUESTION
        )
        if dlg.ShowModal() == wx.ID_YES:
            self.connection.send('issue.delete', {'id': issue.id})
        dlg.Destroy()

    def on_toggle_issue(self, event=None):
        issue = self.state.get_selected_issue()
        if not issue:
            return
        project = self.state.get_selected_project()
        if not project:
            return

        # Toggle between done and default status
        done_status = None
        default_status = None
        for s in project.statuses:
            if s.category == 'completed':
                done_status = s
            if s.is_default:
                default_status = s

        current_status = self.state.get_status(issue.status_id)
        if current_status and current_status.category == 'completed':
            target = default_status
        else:
            target = done_status

        if target:
            self.connection.send('issue.move', {
                'id': issue.id,
                'status_id': target.id,
            })

    def on_move_status_prev(self, event=None):
        self._move_status_by(-1)

    def on_move_status_next(self, event=None):
        self._move_status_by(1)

    def _move_status_by(self, direction):
        issue = self.state.get_selected_issue()
        if not issue:
            return
        project = self.state.get_selected_project()
        if not project or not project.statuses:
            return

        current_idx = None
        for i, s in enumerate(project.statuses):
            if s.id == issue.status_id:
                current_idx = i
                break

        if current_idx is None:
            return

        new_idx = current_idx + direction
        if 0 <= new_idx < len(project.statuses):
            new_status = project.statuses[new_idx]
            self.connection.send('issue.move', {
                'id': issue.id,
                'status_id': new_status.id,
            })

    def on_pick_status(self, event=None):
        issue = self.state.get_selected_issue()
        if not issue:
            return
        project = self.state.get_selected_project()
        if not project:
            return

        choices = [s.name for s in project.statuses]
        dlg = wx.SingleChoiceDialog(self, "Move to status:", "Pick Status", choices)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            new_status = project.statuses[idx]
            self.connection.send('issue.move', {
                'id': issue.id,
                'status_id': new_status.id,
            })
        dlg.Destroy()

    def on_set_priority(self, event=None):
        issue = self.state.get_selected_issue()
        if not issue:
            return
        choices = [f"{info['icon']} {info['label']}" for info in PRIORITY.values()]
        dlg = wx.SingleChoiceDialog(self, "Set priority:", "Priority", choices)
        if dlg.ShowModal() == wx.ID_OK:
            priority = dlg.GetSelection()
            self.connection.send('issue.update', {
                'id': issue.id,
                'priority': priority,
            })
        dlg.Destroy()

    def on_set_labels(self, event=None):
        issue = self.state.get_selected_issue()
        if not issue:
            return
        if not self.state.labels:
            wx.MessageBox("No labels defined in this workspace.", "Labels")
            return

        choices = [l.name for l in self.state.labels]
        current = [l.id for l in issue.labels]
        dlg = wx.MultiChoiceDialog(self, "Select labels:", "Labels", choices)

        # Pre-select current labels
        selections = []
        for i, label in enumerate(self.state.labels):
            if label.id in current:
                selections.append(i)
        dlg.SetSelections(selections)

        if dlg.ShowModal() == wx.ID_OK:
            selected_ids = [self.state.labels[i].id for i in dlg.GetSelections()]
            self.connection.send('issue.update', {
                'id': issue.id,
                'label_ids': selected_ids,
            })
        dlg.Destroy()

    def on_open_detail(self, event=None):
        if self.state.selected_issue_id:
            self._show_detail(self.state.selected_issue_id)

    def on_close_detail(self, event=None):
        self._hide_detail()

    def on_refresh(self, event=None):
        if self.state.selected_project_id:
            self.connection.send('issue.list', {
                'project_id': self.state.selected_project_id,
            })

    def on_toggle_view(self, event=None):
        new_mode = 'list' if self.state.view_mode == 'board' else 'board'
        self._on_view_toggle(new_mode)

    # --- Cleanup ---

    def _on_close(self, event):
        """Save settings and disconnect on close."""
        size = self.GetSize()
        self.settings['window_width'] = size.width
        self.settings['window_height'] = size.height
        self.settings['view_mode'] = self.state.view_mode
        if self.state.selected_project_id:
            self.settings['last_project_id'] = self.state.selected_project_id
        if self.state.workspace:
            self.settings['last_workspace_slug'] = self.state.workspace.slug
        save_settings(self.settings)

        self.connection.disconnect()
        self.Destroy()

    def _on_update_check(self, latest_version, download_url):
        """Handle update check result (called from background thread)."""
        if latest_version:
            import wx
            wx.CallAfter(
                wx.MessageBox,
                f"A new version (v{latest_version}) is available.\n"
                f"Download at: {download_url}",
                "Update Available",
                wx.OK | wx.ICON_INFORMATION,
            )
