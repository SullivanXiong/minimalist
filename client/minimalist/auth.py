"""Authentication: token storage, refresh, and login dialog."""

import json
import os

import requests
import wx

from .config import SERVER_URL
from .theme import DARK, apply_dark_theme, hex_to_wx

TOKEN_FILE = os.path.join(
    os.path.expanduser('~/.config/minimalist'), 'auth.json'
)


def load_tokens():
    """Load stored JWT tokens from disk."""
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_tokens(tokens):
    """Save JWT tokens to disk with restricted permissions."""
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(tokens, f)


def clear_tokens():
    """Remove stored tokens."""
    try:
        os.remove(TOKEN_FILE)
    except FileNotFoundError:
        pass


def refresh_access_token(refresh_token):
    """Exchange a refresh token for a new access token."""
    try:
        resp = requests.post(
            f"{SERVER_URL}/api/auth/refresh/",
            json={'refresh': refresh_token},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            tokens = load_tokens()
            tokens['access'] = data['access']
            if 'refresh' in data:
                tokens['refresh'] = data['refresh']
            save_tokens(tokens)
            return data['access']
    except requests.RequestException:
        pass
    return None


def validate_token(access_token):
    """Check if the access token is still valid by calling /api/auth/me/."""
    try:
        resp = requests.get(
            f"{SERVER_URL}/api/auth/me/",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=3,
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False


def get_valid_token():
    """Return a valid access token, refreshing if needed. Returns None if login required."""
    tokens = load_tokens()
    access = tokens.get('access')
    refresh = tokens.get('refresh')

    if access and validate_token(access):
        return access

    if refresh:
        new_access = refresh_access_token(refresh)
        if new_access:
            return new_access

    return None


def login(username, password):
    """Authenticate and store tokens. Returns (success, error_message)."""
    try:
        resp = requests.post(
            f"{SERVER_URL}/api/auth/login/",
            json={'username': username, 'password': password},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            save_tokens({
                'access': data['access'],
                'refresh': data['refresh'],
            })
            return True, None
        else:
            return False, 'Invalid username or password'
    except requests.RequestException as e:
        return False, f'Connection error: {e}'


class LoginDialog(wx.Dialog):
    """Login dialog for authentication."""

    def __init__(self, parent):
        super().__init__(parent, title="Login — Minimalist", size=(360, 260))
        apply_dark_theme(self, 'bg_primary')

        panel = wx.Panel(self)
        apply_dark_theme(panel, 'bg_primary')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)

        # Title
        title = wx.StaticText(panel, label="Sign in to Minimalist")
        title.SetForegroundColour(hex_to_wx(DARK['text_primary']))
        title.SetFont(title.GetFont().Bold().Scaled(1.3))
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        # Username
        lbl = wx.StaticText(panel, label="Username")
        lbl.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        sizer.Add(lbl, 0, wx.LEFT | wx.RIGHT, 30)
        self.username_ctrl = wx.TextCtrl(panel)
        sizer.Add(self.username_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 30)

        # Password
        lbl2 = wx.StaticText(panel, label="Password")
        lbl2.SetForegroundColour(hex_to_wx(DARK['text_secondary']))
        sizer.Add(lbl2, 0, wx.LEFT | wx.RIGHT, 30)
        self.password_ctrl = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(self.password_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 30)

        # Error label
        self.error_label = wx.StaticText(panel, label="")
        self.error_label.SetForegroundColour(hex_to_wx(DARK['accent_red']))
        sizer.Add(self.error_label, 0, wx.LEFT | wx.RIGHT, 30)

        # Login button
        btn = wx.Button(panel, wx.ID_OK, "Sign In")
        sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        btn.Bind(wx.EVT_BUTTON, self._on_login)

        panel.SetSizer(sizer)
        self.username_ctrl.SetFocus()

        # Allow Enter key to submit
        self.password_ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_login)

        self.result = None

    def _on_login(self, event):
        username = self.username_ctrl.GetValue().strip()
        password = self.password_ctrl.GetValue()

        if not username or not password:
            self.error_label.SetLabel("Username and password required")
            return

        success, error = login(username, password)
        if success:
            self.result = True
            self.EndModal(wx.ID_OK)
        else:
            self.error_label.SetLabel(error or "Login failed")
