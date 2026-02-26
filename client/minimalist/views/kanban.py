"""Kanban board view with status columns and issue cards."""

import wx

from ..theme import DARK, PRIORITY, hex_to_wx, apply_dark_theme


class IssueCard(wx.Panel):
    """A single issue card in a Kanban column."""

    def __init__(self, parent, issue, state, on_click, on_double_click):
        super().__init__(parent)
        self.issue = issue
        self.state = state
        self.on_click_cb = on_click
        self.on_double_click_cb = on_double_click
        self._selected = False

        self.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        self.SetMinSize((-1, 70))
        self._init_ui()

        self.Bind(wx.EVT_LEFT_DOWN, self._on_click)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_dclick)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_hover_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_hover_leave)

    def _init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Top row: identifier + priority
        top_row = wx.BoxSizer(wx.HORIZONTAL)
        ident = wx.StaticText(self, label=self.issue.identifier)
        ident.SetForegroundColour(hex_to_wx(DARK['text_muted']))
        font = ident.GetFont()
        font.SetPointSize(font.GetPointSize() - 1)
        ident.SetFont(font)
        ident.Bind(wx.EVT_LEFT_DOWN, self._on_click)
        top_row.Add(ident, 1, wx.ALIGN_CENTER_VERTICAL)

        pri_info = PRIORITY.get(self.issue.priority, PRIORITY[0])
        if self.issue.priority > 0:
            pri_label = wx.StaticText(self, label=pri_info['icon'])
            pri_label.SetForegroundColour(hex_to_wx(pri_info['color']))
            pri_label.Bind(wx.EVT_LEFT_DOWN, self._on_click)
            top_row.Add(pri_label, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(top_row, 0, wx.EXPAND | wx.ALL, 8)

        # Title
        title = wx.StaticText(self, label=self.issue.title)
        title.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        title.Wrap(200)
        title.Bind(wx.EVT_LEFT_DOWN, self._on_click)
        sizer.Add(title, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Bottom row: labels + sub-issue indicator
        if self.issue.labels or self.issue.sub_issue_count > 0:
            bottom_row = wx.BoxSizer(wx.HORIZONTAL)
            for label in self.issue.labels[:3]:
                chip = wx.StaticText(self, label=label.name)
                chip.SetForegroundColour(hex_to_wx(label.color))
                chip_font = chip.GetFont()
                chip_font.SetPointSize(chip_font.GetPointSize() - 2)
                chip.SetFont(chip_font)
                chip.Bind(wx.EVT_LEFT_DOWN, self._on_click)
                bottom_row.Add(chip, 0, wx.RIGHT, 6)

            if self.issue.sub_issue_count > 0:
                bottom_row.AddStretchSpacer()
                sub_text = f"{self.issue.sub_issue_completed}/{self.issue.sub_issue_count}"
                sub_label = wx.StaticText(self, label=sub_text)
                sub_label.SetForegroundColour(hex_to_wx(DARK['text_muted']))
                sub_label.Bind(wx.EVT_LEFT_DOWN, self._on_click)
                bottom_row.Add(sub_label, 0, wx.ALIGN_CENTER_VERTICAL)

            sizer.Add(bottom_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.SetSizer(sizer)

    def set_selected(self, selected):
        self._selected = selected
        if selected:
            self.SetBackgroundColour(hex_to_wx(DARK['bg_selected']))
        else:
            self.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
        self.Refresh()

    def _on_click(self, event):
        self.on_click_cb(self.issue.id)

    def _on_dclick(self, event):
        self.on_double_click_cb(self.issue.id)

    def _on_hover_enter(self, event):
        if not self._selected:
            self.SetBackgroundColour(hex_to_wx(DARK['bg_hover']))
            self.Refresh()

    def _on_hover_leave(self, event):
        if not self._selected:
            self.SetBackgroundColour(hex_to_wx(DARK['bg_surface']))
            self.Refresh()


class StatusColumn(wx.Panel):
    """A vertical column representing a single status in the Kanban board."""

    def __init__(self, parent, status, issues, state, on_card_click, on_card_dclick):
        super().__init__(parent)
        self.status = status
        self.state = state
        self.cards = []

        self.SetBackgroundColour(hex_to_wx(DARK['bg_primary']))
        self.SetMinSize((260, -1))

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Column header
        header = wx.BoxSizer(wx.HORIZONTAL)

        # Status color dot
        dot = wx.StaticText(self, label="\u25CF ")
        dot.SetForegroundColour(hex_to_wx(status.color))
        header.Add(dot, 0, wx.ALIGN_CENTER_VERTICAL)

        name_label = wx.StaticText(self, label=status.name)
        name_label.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        header.Add(name_label, 1, wx.ALIGN_CENTER_VERTICAL)

        count_label = wx.StaticText(self, label=str(len(issues)))
        count_label.SetForegroundColour(hex_to_wx(DARK['text_muted']))
        header.Add(count_label, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(header, 0, wx.EXPAND | wx.ALL, 8)

        # Scrollable card area
        self.scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.scroll.SetBackgroundColour(hex_to_wx(DARK['bg_primary']))
        self.scroll.SetScrollRate(0, 10)
        card_sizer = wx.BoxSizer(wx.VERTICAL)

        for issue in issues:
            card = IssueCard(self.scroll, issue, state, on_card_click, on_card_dclick)
            card_sizer.Add(card, 0, wx.EXPAND | wx.BOTTOM, 6)
            self.cards.append(card)

        self.scroll.SetSizer(card_sizer)
        sizer.Add(self.scroll, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        self.SetSizer(sizer)

    def select_issue(self, issue_id):
        for card in self.cards:
            card.set_selected(card.issue.id == issue_id)


class KanbanBoard(wx.ScrolledWindow):
    """Horizontal scrolling Kanban board with status columns."""

    def __init__(self, parent, state, on_card_click, on_card_dclick):
        super().__init__(parent, style=wx.HSCROLL)
        self.state = state
        self.on_card_click = on_card_click
        self.on_card_dclick = on_card_dclick
        self.columns = []

        self.SetBackgroundColour(hex_to_wx(DARK['bg_primary']))
        self.SetScrollRate(10, 0)

        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self._sizer)

    def refresh(self):
        """Rebuild the board from state."""
        # Clear existing columns
        self._sizer.Clear(delete_windows=True)
        self.columns = []

        project = self.state.get_selected_project()
        if not project:
            return

        issues = self.state.get_project_issues()

        for status in project.statuses:
            status_issues = [i for i in issues if i.status_id == status.id]
            col = StatusColumn(
                self, status, status_issues, self.state,
                self.on_card_click, self.on_card_dclick
            )
            self._sizer.Add(col, 0, wx.EXPAND | wx.RIGHT, 4)
            self.columns.append(col)

        self.Layout()
        self.FitInside()

    def select_issue(self, issue_id):
        for col in self.columns:
            col.select_issue(issue_id)
