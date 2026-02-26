"""Project creation/editing dialog."""

import wx

from ..theme import DARK, hex_to_wx, apply_dark_theme


class ProjectDialog(wx.Dialog):
    """Dialog for creating or editing a project."""

    def __init__(self, parent, project=None):
        title = "Edit Project" if project else "Create Project"
        super().__init__(parent, title=title, size=(400, 250))
        self.project = project
        self.result = None

        apply_dark_theme(self, 'bg_secondary')
        self._init_ui()
        self.CenterOnParent()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Name
        sizer.Add(self._make_label("Name"), 0, wx.LEFT | wx.TOP, 16)
        self.name_ctrl = wx.TextCtrl(self)
        self.name_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.name_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        if self.project:
            self.name_ctrl.SetValue(self.project.name)
        sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Icon
        sizer.Add(self._make_label("Icon (emoji)"), 0, wx.LEFT, 16)
        self.icon_ctrl = wx.TextCtrl(self)
        self.icon_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.icon_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        if self.project:
            self.icon_ctrl.SetValue(self.project.icon)
        sizer.Add(self.icon_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Color
        sizer.Add(self._make_label("Color (hex)"), 0, wx.LEFT, 16)
        self.color_ctrl = wx.TextCtrl(self)
        self.color_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.color_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        self.color_ctrl.SetValue(self.project.color if self.project else '#6B7280')
        sizer.Add(self.color_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddStretchSpacer()

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()

        cancel_btn = wx.Button(self, wx.ID_CANCEL, label="Cancel")
        cancel_btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        cancel_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        btn_sizer.Add(cancel_btn, 0, wx.RIGHT, 8)

        ok_label = "Save" if self.project else "Create"
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

        self.result = {
            'name': name,
            'slug': name.lower().replace(' ', '-'),
            'icon': self.icon_ctrl.GetValue().strip(),
            'color': self.color_ctrl.GetValue().strip() or '#6B7280',
        }
        self.EndModal(wx.ID_OK)
