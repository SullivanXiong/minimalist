"""Label management dialog."""

import wx

from ..theme import DARK, hex_to_wx, apply_dark_theme


class LabelDialog(wx.Dialog):
    """Dialog for creating or editing a label."""

    def __init__(self, parent, label=None):
        title = "Edit Label" if label else "Create Label"
        super().__init__(parent, title=title, size=(400, 250))
        self.label_data = label
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
        if self.label_data:
            self.name_ctrl.SetValue(self.label_data.name)
        sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Color
        sizer.Add(self._make_label("Color (hex)"), 0, wx.LEFT, 16)
        self.color_ctrl = wx.TextCtrl(self)
        self.color_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.color_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        self.color_ctrl.SetValue(self.label_data.color if self.label_data else '#6B7280')
        sizer.Add(self.color_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(8)

        # Description
        sizer.Add(self._make_label("Description"), 0, wx.LEFT, 16)
        self.desc_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.desc_ctrl.SetBackgroundColour(hex_to_wx(DARK['bg_input']))
        self.desc_ctrl.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        if self.label_data:
            self.desc_ctrl.SetValue(self.label_data.description)
        sizer.Add(self.desc_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        sizer.AddSpacer(12)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        cancel_btn = wx.Button(self, wx.ID_CANCEL, label="Cancel")
        cancel_btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        cancel_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        btn_sizer.Add(cancel_btn, 0, wx.RIGHT, 8)

        ok_label = "Save" if self.label_data else "Create"
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
            'color': self.color_ctrl.GetValue().strip() or '#6B7280',
            'description': self.desc_ctrl.GetValue(),
        }
        self.EndModal(wx.ID_OK)
