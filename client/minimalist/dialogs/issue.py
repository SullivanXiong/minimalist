"""Issue creation dialog."""

import wx

from ..theme import DARK, PRIORITY, ESTIMATES, hex_to_wx, apply_dark_theme


class IssueCreateDialog(wx.Dialog):
    """Quick-create dialog for new issues."""

    def __init__(self, parent, state):
        super().__init__(parent, title="Create Issue", size=(450, 350))
        self.state = state
        self.result = None

        apply_dark_theme(self, 'bg_secondary')
        self._init_ui()
        self.CenterOnParent()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        sizer.Add(self._make_label("Title"), 0, wx.LEFT | wx.TOP, 16)
        self.title_ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.title_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.title_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        self.title_ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_submit)
        sizer.Add(self.title_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Project
        sizer.Add(self._make_label("Project"), 0, wx.LEFT, 16)
        self.project_choice = wx.Choice(self)
        apply_dark_theme(self.project_choice, 'bg_input')
        selected_idx = 0
        for i, project in enumerate(self.state.projects):
            self.project_choice.Append(project.name, project.id)
            if project.id == self.state.selected_project_id:
                selected_idx = i
        if self.state.projects:
            self.project_choice.SetSelection(selected_idx)
        sizer.Add(self.project_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Priority
        sizer.Add(self._make_label("Priority"), 0, wx.LEFT, 16)
        self.priority_choice = wx.Choice(self)
        apply_dark_theme(self.priority_choice, 'bg_input')
        for val, info in PRIORITY.items():
            self.priority_choice.Append(f"{info['icon']} {info['label']}")
        self.priority_choice.SetSelection(0)
        sizer.Add(self.priority_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Description
        sizer.Add(self._make_label("Description (optional)"), 0, wx.LEFT, 16)
        self.desc_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.desc_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.desc_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        sizer.Add(self.desc_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(12)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()

        cancel_btn = wx.Button(self, wx.ID_CANCEL, label="Cancel")
        cancel_btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        cancel_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        btn_sizer.Add(cancel_btn, 0, wx.RIGHT, 8)

        create_btn = wx.Button(self, wx.ID_OK, label="Create")
        create_btn.SetBackgroundColour(hex_to_wx(DARK['accent_blue']))
        create_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        create_btn.Bind(wx.EVT_BUTTON, self._on_submit)
        btn_sizer.Add(create_btn, 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 16)

        self.SetSizer(sizer)
        self.title_ctrl.SetFocus()

    def _make_label(self, text):
        label = wx.StaticText(self, label=text)
        label.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        return label

    def _on_submit(self, event):
        title = self.title_ctrl.GetValue().strip()
        if not title:
            return

        proj_idx = self.project_choice.GetSelection()
        if proj_idx == wx.NOT_FOUND:
            return

        self.result = {
            'title': title,
            'project_id': self.project_choice.GetClientData(proj_idx),
            'priority': self.priority_choice.GetSelection(),
            'description': self.desc_ctrl.GetValue(),
        }
        self.EndModal(wx.ID_OK)
