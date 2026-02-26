"""Toolbar panel above the main content area."""

import wx

from ..theme import DARK, hex_to_wx, apply_dark_theme


class ToolbarPanel(wx.Panel):
    """Horizontal toolbar with project name, view toggle, and action buttons."""

    def __init__(self, parent, state, on_view_toggle, on_create_issue, on_filter):
        super().__init__(parent)
        self.state = state
        self.on_view_toggle = on_view_toggle
        self.on_create_issue = on_create_issue
        self.on_filter = on_filter

        apply_dark_theme(self, 'bg_primary')
        self._init_ui()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Project name
        self.project_label = wx.StaticText(self, label="")
        self.project_label.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        font = self.project_label.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.project_label.SetFont(font)
        sizer.Add(self.project_label, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 16)

        # View toggle buttons
        self.board_btn = wx.Button(self, label="Board", size=(60, 28))
        self.list_btn = wx.Button(self, label="List", size=(60, 28))
        for btn in (self.board_btn, self.list_btn):
            btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
            btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        self.board_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_view_toggle('board'))
        self.list_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_view_toggle('list'))
        sizer.Add(self.board_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        sizer.Add(self.list_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

        # New issue button
        self.new_btn = wx.Button(self, label="+ New", size=(70, 28))
        self.new_btn.SetBackgroundColour(hex_to_wx(DARK['accent_blue']))
        self.new_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        self.new_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_create_issue())
        sizer.Add(self.new_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 16)

        self.SetSizer(sizer)
        self.SetMinSize((-1, 48))

    def refresh(self):
        """Update toolbar display from state."""
        project = self.state.get_selected_project()
        if project:
            self.project_label.SetLabel(project.name)
        else:
            self.project_label.SetLabel("")

        # Highlight active view mode
        if self.state.view_mode == 'board':
            self.board_btn.SetBackgroundColour(hex_to_wx(DARK['bg_selected']))
            self.list_btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        else:
            self.list_btn.SetBackgroundColour(hex_to_wx(DARK['bg_selected']))
            self.board_btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
