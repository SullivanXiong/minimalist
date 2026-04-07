"""Display formatting utilities."""

from ..theme import PRIORITY


def format_date(iso_str):
    """Format an ISO date string for display."""
    if not iso_str:
        return ''
    return iso_str[:10]


def format_priority(priority_val):
    """Get priority display info."""
    return PRIORITY.get(priority_val, PRIORITY[0])
