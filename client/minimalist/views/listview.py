"""Multi-column list view for issues."""

import wx

from ..theme import DARK, PRIORITY, hex_to_wx, apply_dark_theme
from ..utils.formatting import format_date


class IssueListView(wx.ListCtrl):
    """Multi-column issue list with dark theme."""

    def __init__(self, parent, state, on_issue_selected, on_issue_activated):
        super().__init__(
            parent,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_NONE
        )
        self.state = state
        self.on_issue_selected = on_issue_selected
        self.on_issue_activated = on_issue_activated
        self._issue_ids = []

        apply_dark_theme(self, 'bg_primary')

        self.InsertColumn(0, "ID", width=80)
        self.InsertColumn(1, "Title", width=350)
        self.InsertColumn(2, "Status", width=100)
        self.InsertColumn(3, "Priority", width=80)
        self.InsertColumn(4, "Labels", width=120)
        self.InsertColumn(5, "Est", width=50)
        self.InsertColumn(6, "Created", width=90)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_activated)

    def refresh(self):
        """Refresh the list from current state."""
        self.DeleteAllItems()
        self._issue_ids = []

        issues = self.state.get_project_issues()
        for issue in issues:
            idx = self.InsertItem(self.GetItemCount(), issue.identifier)
            self._issue_ids.append(issue.id)

            self.SetItem(idx, 1, issue.title)

            status = self.state.get_status(issue.status_id)
            self.SetItem(idx, 2, status.name if status else '')

            pri_info = PRIORITY.get(issue.priority, PRIORITY[0])
            self.SetItem(idx, 3, pri_info['icon'])

            label_names = ', '.join(l.name for l in issue.labels)
            self.SetItem(idx, 4, label_names)

            self.SetItem(idx, 5, str(issue.estimate) if issue.estimate else '')
            self.SetItem(idx, 6, format_date(issue.created_at))

            # Color rows for completed/cancelled
            if status and status.category == 'completed':
                self.SetItemTextColour(idx, hex_to_wx(DARK['text_muted']))
            elif status and status.category == 'cancelled':
                self.SetItemTextColour(idx, hex_to_wx(DARK['text_muted']))

        # Restore selection
        if self.state.selected_issue_id:
            for i, iid in enumerate(self._issue_ids):
                if iid == self.state.selected_issue_id:
                    self.Select(i)
                    break

    def get_selected_issue_id(self):
        idx = self.GetFirstSelected()
        if idx == -1 or idx >= len(self._issue_ids):
            return None
        return self._issue_ids[idx]

    def _on_selected(self, event):
        issue_id = self.get_selected_issue_id()
        if issue_id:
            self.state.selected_issue_id = issue_id
            self.on_issue_selected(issue_id)

    def _on_activated(self, event):
        issue_id = self.get_selected_issue_id()
        if issue_id:
            self.on_issue_activated(issue_id)
