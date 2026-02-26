"""Slide-in issue detail panel."""

import wx

from ..theme import DARK, PRIORITY, ESTIMATES, hex_to_wx, apply_dark_theme
from ..utils.formatting import format_date


class IssueDetailPanel(wx.Panel):
    """Right-side panel for viewing and editing issue details."""

    def __init__(self, parent, state, connection):
        super().__init__(parent)
        self.state = state
        self.connection = connection
        self._current_issue_id = None

        apply_dark_theme(self, 'bg_secondary')
        self._init_ui()

    def _init_ui(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Header: identifier + close button
        header = wx.BoxSizer(wx.HORIZONTAL)
        self.identifier_label = wx.StaticText(self, label="")
        self.identifier_label.SetForegroundColour(hex_to_wx(DARK['text_muted']))
        header.Add(self.identifier_label, 1, wx.ALIGN_CENTER_VERTICAL)

        close_btn = wx.Button(self, label="X", size=(24, 24))
        close_btn.SetBackgroundColour(hex_to_wx(DARK['bg_secondary']))
        close_btn.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        close_btn.Bind(wx.EVT_BUTTON, lambda e: wx.GetTopLevelParent(self).on_close_detail())
        header.Add(close_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(header, 0, wx.EXPAND | wx.ALL, 12)

        # Title (editable)
        self.title_ctrl = wx.TextCtrl(
            self, style=wx.TE_PROCESS_ENTER | wx.BORDER_NONE
        )
        self.title_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_secondary']))
        self.title_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        font = self.title_ctrl.GetFont()
        font.SetPointSize(font.GetPointSize() + 4)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.title_ctrl.SetFont(font)
        self.title_ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_title_change)
        self.title_ctrl.Bind(wx.EVT_KILL_FOCUS, self._on_title_change)
        self.sizer.Add(self.title_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.sizer.AddSpacer(12)

        # Properties grid
        grid = wx.FlexGridSizer(cols=2, hgap=12, vgap=8)
        grid.AddGrowableCol(1, 1)

        # Status
        grid.Add(self._make_label("Status"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.status_choice = wx.Choice(self)
        apply_dark_theme(self.status_choice, 'bg_input')
        self.status_choice.Bind(wx.EVT_CHOICE, self._on_status_change)
        grid.Add(self.status_choice, 0, wx.EXPAND)

        # Priority
        grid.Add(self._make_label("Priority"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.priority_choice = wx.Choice(self)
        apply_dark_theme(self.priority_choice, 'bg_input')
        for val, info in PRIORITY.items():
            self.priority_choice.Append(f"{info['icon']} {info['label']}")
        self.priority_choice.Bind(wx.EVT_CHOICE, self._on_priority_change)
        grid.Add(self.priority_choice, 0, wx.EXPAND)

        # Estimate
        grid.Add(self._make_label("Estimate"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.estimate_choice = wx.Choice(self)
        apply_dark_theme(self.estimate_choice, 'bg_input')
        self.estimate_choice.Append("None")
        for est in ESTIMATES:
            self.estimate_choice.Append(str(est))
        self.estimate_choice.Bind(wx.EVT_CHOICE, self._on_estimate_change)
        grid.Add(self.estimate_choice, 0, wx.EXPAND)

        # Labels display
        grid.Add(self._make_label("Labels"), 0, wx.ALIGN_TOP)
        self.labels_text = wx.StaticText(self, label="")
        self.labels_text.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        grid.Add(self.labels_text, 0, wx.EXPAND)

        self.sizer.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.sizer.AddSpacer(16)

        # Description
        desc_label = self._make_label("Description")
        self.sizer.Add(desc_label, 0, wx.LEFT, 12)
        self.desc_ctrl = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.BORDER_NONE
        )
        self.desc_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.desc_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        self.desc_ctrl.Bind(wx.EVT_KILL_FOCUS, self._on_desc_change)
        self.sizer.Add(self.desc_ctrl, 1, wx.EXPAND | wx.ALL, 12)

        # Timestamps
        self.timestamps_label = wx.StaticText(self, label="")
        self.timestamps_label.SetForegroundColour(hex_to_wx(DARK['text_muted']))
        font_small = self.timestamps_label.GetFont()
        font_small.SetPointSize(font_small.GetPointSize() - 1)
        self.timestamps_label.SetFont(font_small)
        self.sizer.Add(self.timestamps_label, 0, wx.ALL, 12)

        # Delete button
        delete_btn = wx.Button(self, label="Delete Issue")
        delete_btn.SetBackgroundColour(hex_to_wx(DARK['accent_red']))
        delete_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        delete_btn.Bind(wx.EVT_BUTTON, self._on_delete)
        self.sizer.Add(delete_btn, 0, wx.ALL | wx.ALIGN_RIGHT, 12)

        self.SetSizer(self.sizer)

    def _make_label(self, text):
        label = wx.StaticText(self, label=text)
        label.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        return label

    def show_issue(self, issue_id):
        """Populate the panel with issue data."""
        self._current_issue_id = issue_id
        issue = self.state.get_selected_issue()
        if not issue or issue.id != issue_id:
            # Find issue in state
            for i in self.state.issues:
                if i.id == issue_id:
                    issue = i
                    break
        if not issue:
            return

        self.identifier_label.SetLabel(issue.identifier)
        self.title_ctrl.SetValue(issue.title)

        # Populate status choices
        self.status_choice.Clear()
        project = self.state.get_selected_project()
        selected_status_idx = 0
        if project:
            for i, status in enumerate(project.statuses):
                self.status_choice.Append(status.name)
                if status.id == issue.status_id:
                    selected_status_idx = i
        self.status_choice.SetSelection(selected_status_idx)

        # Priority
        self.priority_choice.SetSelection(issue.priority)

        # Estimate
        if issue.estimate is None:
            self.estimate_choice.SetSelection(0)
        else:
            for i, est in enumerate(ESTIMATES):
                if est == issue.estimate:
                    self.estimate_choice.SetSelection(i + 1)
                    break

        # Labels
        label_text = ', '.join(l.name for l in issue.labels) if issue.labels else 'None'
        self.labels_text.SetLabel(label_text)

        # Description
        self.desc_ctrl.SetValue(issue.description)

        # Timestamps
        timestamps = f"Created: {format_date(issue.created_at)}"
        if issue.completed_at:
            timestamps += f"  |  Completed: {format_date(issue.completed_at)}"
        self.timestamps_label.SetLabel(timestamps)

        self.Layout()

    def _on_title_change(self, event):
        if not self._current_issue_id:
            return
        new_title = self.title_ctrl.GetValue().strip()
        if not new_title:
            return
        self.connection.send('issue.update', {
            'id': self._current_issue_id,
            'title': new_title,
        })

    def _on_status_change(self, event):
        if not self._current_issue_id:
            return
        project = self.state.get_selected_project()
        if not project:
            return
        idx = self.status_choice.GetSelection()
        if idx == wx.NOT_FOUND or idx >= len(project.statuses):
            return
        status = project.statuses[idx]
        self.connection.send('issue.move', {
            'id': self._current_issue_id,
            'status_id': status.id,
        })

    def _on_priority_change(self, event):
        if not self._current_issue_id:
            return
        priority = self.priority_choice.GetSelection()
        self.connection.send('issue.update', {
            'id': self._current_issue_id,
            'priority': priority,
        })

    def _on_estimate_change(self, event):
        if not self._current_issue_id:
            return
        idx = self.estimate_choice.GetSelection()
        estimate = None if idx == 0 else ESTIMATES[idx - 1]
        self.connection.send('issue.update', {
            'id': self._current_issue_id,
            'estimate': estimate,
        })

    def _on_desc_change(self, event):
        if not self._current_issue_id:
            return
        self.connection.send('issue.update', {
            'id': self._current_issue_id,
            'description': self.desc_ctrl.GetValue(),
        })

    def _on_delete(self, event):
        dlg = wx.MessageDialog(
            self, "Delete this issue?", "Confirm Delete",
            wx.YES_NO | wx.ICON_QUESTION
        )
        if dlg.ShowModal() == wx.ID_YES:
            self.connection.send('issue.delete', {
                'id': self._current_issue_id,
            })
            # Close the detail panel
            wx.GetTopLevelParent(self).on_close_detail()
        dlg.Destroy()
