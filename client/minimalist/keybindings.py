"""Keyboard binding definitions for the application."""


def setup_keybindings(frame, vim_nav):
    """Configure all vim keybindings on the main frame."""
    # Issue operations
    vim_nav.map_key('c', frame.on_create_issue, "Create new issue")
    vim_nav.map_key('e', frame.on_edit_issue, "Edit selected issue")
    vim_nav.map_key('dd', frame.on_delete_issue, "Delete selected issue")
    vim_nav.map_key('x', frame.on_toggle_issue, "Toggle issue completion")
    vim_nav.map_key('r', frame.on_refresh, "Refresh view")
    vim_nav.map_key('?', vim_nav.show_help, "Show keyboard shortcuts")

    # Issue movement (Kanban)
    vim_nav.map_key('[', frame.on_move_status_prev, "Move issue to previous status")
    vim_nav.map_key(']', frame.on_move_status_next, "Move issue to next status")
    vim_nav.map_key('m', frame.on_pick_status, "Pick status for issue")

    # Issue properties
    vim_nav.map_key('p', frame.on_set_priority, "Set issue priority")
    vim_nav.map_key('L', frame.on_set_labels, "Set issue labels")

    # Navigation
    vim_nav.map_key('Enter', frame.on_open_detail, "Open issue detail")
    vim_nav.map_key('Escape', frame.on_close_detail, "Close detail / deselect")

    # View toggles
    vim_nav.map_key('Tab', frame.on_toggle_view, "Toggle board/list view")
