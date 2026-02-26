"""Left sidebar with workspace switcher and project list."""

import wx

from ..theme import DARK, hex_to_wx, apply_dark_theme


class SidebarPanel(wx.Panel):
    """Dark-themed sidebar with workspace and project navigation."""

    def __init__(self, parent, state, on_project_selected, on_workspace_switch):
        super().__init__(parent)
        self.state = state
        self.on_project_selected = on_project_selected
        self.on_workspace_switch = on_workspace_switch

        apply_dark_theme(self, 'bg_secondary')
        self._init_ui()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Workspace header
        self.workspace_label = wx.StaticText(self, label="Workspace")
        self.workspace_label.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        font = self.workspace_label.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(font.GetPointSize() + 1)
        self.workspace_label.SetFont(font)
        sizer.Add(self.workspace_label, 0, wx.ALL | wx.EXPAND, 12)

        # Separator
        sep = wx.StaticLine(self)
        sep.SetBackgroundColour(hex_to_wx(DARK['border_primary']))
        sizer.Add(sep, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # Projects header
        projects_header = wx.BoxSizer(wx.HORIZONTAL)
        proj_label = wx.StaticText(self, label="Projects")
        proj_label.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        font_small = proj_label.GetFont()
        font_small.SetPointSize(font_small.GetPointSize() - 1)
        proj_label.SetFont(font_small)
        projects_header.Add(proj_label, 1, wx.ALIGN_CENTER_VERTICAL)

        self.add_project_btn = wx.Button(self, label="+", size=(24, 24))
        self.add_project_btn.SetBackgroundColour(hex_to_wx(DARK['bg_secondary']))
        self.add_project_btn.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        projects_header.Add(self.add_project_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(projects_header, 0, wx.ALL | wx.EXPAND, 12)

        # Project list
        self.project_list = wx.ListBox(self, style=wx.LB_SINGLE | wx.BORDER_NONE)
        apply_dark_theme(self.project_list, 'bg_secondary')
        self.project_list.Bind(wx.EVT_LISTBOX, self._on_project_click)
        sizer.Add(self.project_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # Labels section
        sizer.AddSpacer(16)
        labels_label = wx.StaticText(self, label="Labels")
        labels_label.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        labels_label.SetFont(font_small)
        sizer.Add(labels_label, 0, wx.LEFT | wx.RIGHT, 12)

        self.labels_list = wx.ListBox(self, style=wx.LB_SINGLE | wx.BORDER_NONE)
        apply_dark_theme(self.labels_list, 'bg_secondary')
        sizer.Add(self.labels_list, 0, wx.EXPAND | wx.ALL, 8)

        self.SetSizer(sizer)

    def refresh(self):
        """Refresh sidebar contents from state."""
        # Workspace name
        if self.state.workspace:
            self.workspace_label.SetLabel(self.state.workspace.name)

        # Projects
        self.project_list.Clear()
        for project in self.state.projects:
            self.project_list.Append(project.name, project.id)

        # Select the current project
        if self.state.selected_project_id:
            for i in range(self.project_list.GetCount()):
                if self.project_list.GetClientData(i) == self.state.selected_project_id:
                    self.project_list.SetSelection(i)
                    break

        # Labels
        self.labels_list.Clear()
        for label in self.state.labels:
            self.labels_list.Append(label.name, label.id)

    def _on_project_click(self, event):
        idx = self.project_list.GetSelection()
        if idx == wx.NOT_FOUND:
            return
        project_id = self.project_list.GetClientData(idx)
        self.state.selected_project_id = project_id
        self.on_project_selected(project_id)
