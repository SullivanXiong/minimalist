"""Workspace creation/editing dialog."""

import wx

from ..theme import DARK, hex_to_wx, apply_dark_theme


class WorkspaceDialog(wx.Dialog):
    """Dialog for creating or editing a workspace."""

    def __init__(self, parent, workspace=None):
        title = "Edit Workspace" if workspace else "Create Workspace"
        super().__init__(parent, title=title, size=(400, 280))
        self.workspace = workspace
        self.result = None

        apply_dark_theme(self, 'bg_secondary')
        self._init_ui()
        self.CenterOnParent()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Name
        sizer.Add(self._make_label("Name"), 0, wx.LEFT | wx.TOP, 16)
        self.name_ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.name_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.name_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        if self.workspace:
            self.name_ctrl.SetValue(self.workspace.name)
        sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Identifier prefix
        sizer.Add(self._make_label("Identifier Prefix (e.g., WORK, PERS)"), 0, wx.LEFT, 16)
        self.prefix_ctrl = wx.TextCtrl(self)
        self.prefix_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.prefix_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        if self.workspace:
            self.prefix_ctrl.SetValue(self.workspace.identifier_prefix)
        sizer.Add(self.prefix_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Icon
        sizer.Add(self._make_label("Icon (emoji)"), 0, wx.LEFT, 16)
        self.icon_ctrl = wx.TextCtrl(self)
        self.icon_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.icon_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        if self.workspace:
            self.icon_ctrl.SetValue(self.workspace.icon)
        sizer.Add(self.icon_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddStretchSpacer()

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()

        cancel_btn = wx.Button(self, wx.ID_CANCEL, label="Cancel")
        cancel_btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        cancel_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        btn_sizer.Add(cancel_btn, 0, wx.RIGHT, 8)

        ok_label = "Save" if self.workspace else "Create"
        ok_btn = wx.Button(self, wx.ID_OK, label=ok_label)
        ok_btn.SetBackgroundColour(hex_to_wx(DARK['accent_blue']))
        ok_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        ok_btn.Bind(wx.EVT_BUTTON, self._on_submit)
        btn_sizer.Add(ok_btn, 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 16)
        self.SetSizer(sizer)
        self.name_ctrl.SetFocus()

    def _make_label(self, text):
        label = wx.StaticText(self, label=text)
        label.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        return label

    def _on_submit(self, event):
        name = self.name_ctrl.GetValue().strip()
        if not name:
            return
        prefix = self.prefix_ctrl.GetValue().strip().upper()
        if not prefix:
            return

        self.result = {
            'name': name,
            'slug': name.lower().replace(' ', '-'),
            'identifier_prefix': prefix,
            'icon': self.icon_ctrl.GetValue().strip(),
        }
        self.EndModal(wx.ID_OK)
