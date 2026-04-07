"""Status management dialog."""

import wx

from ..theme import DARK, STATUS_COLORS, hex_to_wx, apply_dark_theme


CATEGORIES = ['backlog', 'unstarted', 'started', 'completed', 'cancelled']


class StatusManagerDialog(wx.Dialog):
    """Dialog for managing statuses of a project."""

    def __init__(self, parent, project, connection):
        super().__init__(parent, title=f"Manage Statuses - {project.name}", size=(500, 400))
        self.project = project
        self.connection = connection

        apply_dark_theme(self, 'bg_secondary')
        self._init_ui()
        self.CenterOnParent()

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Status list
        self.status_list = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_NONE
        )
        apply_dark_theme(self.status_list, 'bg_secondary')
        self.status_list.InsertColumn(0, "Name", width=150)
        self.status_list.InsertColumn(1, "Category", width=100)
        self.status_list.InsertColumn(2, "Color", width=80)
        self.status_list.InsertColumn(3, "Default", width=60)

        self._refresh_list()
        sizer.Add(self.status_list, 1, wx.EXPAND | wx.ALL, 12)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_btn = wx.Button(self, label="Add")
        add_btn.SetBackgroundColour(hex_to_wx(DARK['accent_blue']))
        add_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        add_btn.Bind(wx.EVT_BUTTON, self._on_add)
        btn_sizer.Add(add_btn, 0, wx.RIGHT, 8)

        close_btn = wx.Button(self, wx.ID_CANCEL, label="Close")
        close_btn.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        close_btn.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        btn_sizer.Add(close_btn, 0)

        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 12)
        self.SetSizer(sizer)

    def _refresh_list(self):
        self.status_list.DeleteAllItems()
        for status in self.project.statuses:
            idx = self.status_list.InsertItem(self.status_list.GetItemCount(), status.name)
            self.status_list.SetItem(idx, 1, status.category)
            self.status_list.SetItem(idx, 2, status.color)
            self.status_list.SetItem(idx, 3, "Yes" if status.is_default else "")

    def _on_add(self, event):
        dlg = wx.TextEntryDialog(self, "Status name:", "Add Status")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue().strip()
            if name:
                # Choose category
                cat_dlg = wx.SingleChoiceDialog(
                    self, "Category:", "Status Category", CATEGORIES
                )
                if cat_dlg.ShowModal() == wx.ID_OK:
                    category = CATEGORIES[cat_dlg.GetSelection()]
                    self.connection.send('status.create', {
                        'project_id': self.project.id,
                        'name': name,
                        'category': category,
                        'color': STATUS_COLORS.get(category, '#6B7280'),
                        'sort_order': len(self.project.statuses),
                    })
                cat_dlg.Destroy()
        dlg.Destroy()
