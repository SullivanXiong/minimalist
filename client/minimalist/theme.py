"""Dark theme color definitions inspired by Linear's design language."""

import wx

# Dark theme color palette
DARK = {
    # Backgrounds
    'bg_primary': '#0D0D0D',
    'bg_secondary': '#141414',
    'bg_surface': '#1A1A1A',
    'bg_hover': '#222222',
    'bg_selected': '#2A2A2A',
    'bg_input': '#1E1E1E',

    # Text
    'text_primary': '#EBEBEB',
    'text_secondary': '#8A8A8A',
    'text_muted': '#5C5C5C',
    'text_accent': '#7C8AFF',

    # Borders
    'border_primary': '#2A2A2A',
    'border_hover': '#3A3A3A',

    # Accents
    'accent_blue': '#5E6AD2',
    'accent_purple': '#7C5CFC',
    'accent_green': '#10B981',
    'accent_yellow': '#F59E0B',
    'accent_red': '#EF4444',
    'accent_orange': '#F97316',
}

# Status category colors
STATUS_COLORS = {
    'backlog': '#6B7280',
    'unstarted': '#6B7280',
    'started': '#F59E0B',
    'completed': '#10B981',
    'cancelled': '#EF4444',
}

# Priority colors and labels
PRIORITY = {
    0: {'label': 'No Priority', 'color': '#6B7280', 'icon': '---'},
    1: {'label': 'Urgent', 'color': '#EF4444', 'icon': '!!!'},
    2: {'label': 'High', 'color': '#F97316', 'icon': '!! '},
    3: {'label': 'Medium', 'color': '#F59E0B', 'icon': '!  '},
    4: {'label': 'Low', 'color': '#6B7280', 'icon': '.  '},
}

# Estimate options (Fibonacci scale)
ESTIMATES = [1, 2, 3, 5, 8, 13, 21]


def hex_to_wx(hex_str):
    """Convert hex color string to wx.Colour."""
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return wx.Colour(r, g, b)


def apply_dark_theme(widget, bg_key='bg_primary', fg_key='text_primary'):
    """Apply dark theme colors to a widget."""
    widget.SetBackgroundColour(hex_to_wx(DARK[bg_key]))
    widget.SetForegroundColour(hex_to_wx(DARK[fg_key]))
