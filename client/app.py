#!/usr/bin/env python3
"""
Minimalist Todo App - wxPython Client with Vim Navigation
"""

import json
import threading
from typing import Dict, List, Optional

import websocket
import wx

# Import supyx vim navigation
try:
    from supyx.wxnavimgation import VimNavigationMixin
    HAS_VIM_NAV = True
except ImportError:
    print("Warning: supyx not installed. Vim navigation will not be available.")
    HAS_VIM_NAV = False
    VimNavigationMixin = object


class TodoFrame(VimNavigationMixin if HAS_VIM_NAV else object, wx.Frame):
    """Main application frame with todo list and vim navigation."""
    
    def __init__(self):
        super().__init__(None, title="Minimalist Todo", size=(800, 600))
        
        self.todos: List[Dict] = []
        self.ws: Optional[websocket.WebSocketApp] = None
        self.ws_thread: Optional[threading.Thread] = None
        self.is_connected = False
        
        self._init_ui()
        
        # Initialize vim navigation if available
        if HAS_VIM_NAV:
            self.init_vim_navigation()
            self._setup_custom_keybindings()
        
        # Connect to websocket
        self._connect_websocket()
        
        self.Show()
    
    def _init_ui(self):
        """Initialize the user interface."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="📝 Minimalist Todo")
        title_font = title.GetFont()
        title_font.PointSize = 18
        title_font = title_font.Bold()
        title.SetFont(title_font)
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)
        
        # Add todo section
        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.todo_input = wx.TextCtrl(panel, size=(400, 30))
        self.todo_input.SetHint("What needs to be done?")
        add_sizer.Add(self.todo_input, 1, wx.EXPAND | wx.RIGHT, 5)
        
        self.add_btn = wx.Button(panel, label="Add")
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_todo)
        add_sizer.Add(self.add_btn, 0)
        
        main_sizer.Add(add_sizer, 0, wx.ALL | wx.EXPAND, 10)
        
        # Todo list
        self.todo_list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL
        )
        self.todo_list.InsertColumn(0, "✓", width=40)
        self.todo_list.InsertColumn(1, "Task", width=500)
        self.todo_list.InsertColumn(2, "Created", width=150)
        self.todo_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_toggle_todo)
        
        main_sizer.Add(self.todo_list, 1, wx.ALL | wx.EXPAND, 10)
        
        # Action buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.edit_btn = wx.Button(panel, label="Edit")
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit_todo)
        btn_sizer.Add(self.edit_btn, 0, wx.RIGHT, 5)
        
        self.delete_btn = wx.Button(panel, label="Delete")
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_todo)
        btn_sizer.Add(self.delete_btn, 0)
        
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(main_sizer)
        
        # Status bar
        self.CreateStatusBar(2)
        self.SetStatusWidths([-1, 150])
        self.SetStatusText("Disconnected", 0)
    
    def _setup_custom_keybindings(self):
        """Setup custom vim keybindings for todo operations."""
        # Delete selected todo with 'dd'
        self.vim_nav.map_key('dd', self.on_delete_todo, "Delete selected todo")
        
        # Toggle completed with 'x'
        self.vim_nav.map_key('x', self.on_toggle_todo, "Toggle todo completion")
        
        # Edit with 'e'
        self.vim_nav.map_key('e', self.on_edit_todo, "Edit selected todo")
        
        # Refresh list with 'r'
        self.vim_nav.map_key('r', self.refresh_todos, "Refresh todo list")
        
        # Show help with '?'
        self.vim_nav.map_key('?', self.vim_nav.show_help, "Show keyboard shortcuts")
    
    def _connect_websocket(self):
        """Connect to the Django websocket server."""
        def on_message(ws, message):
            data = json.loads(message)
            wx.CallAfter(self._handle_ws_message, data)
        
        def on_error(ws, error):
            wx.CallAfter(self.SetStatusText, f"Error: {error}", 0)
        
        def on_close(ws, close_status_code, close_msg):
            self.is_connected = False
            wx.CallAfter(self.SetStatusText, "Disconnected", 0)
        
        def on_open(ws):
            self.is_connected = True
            wx.CallAfter(self.SetStatusText, "Connected", 0)
        
        # Create websocket connection
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws/todos/",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        # Run websocket in separate thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def _handle_ws_message(self, data):
        """Handle incoming websocket messages."""
        msg_type = data.get('type')
        msg_data = data.get('data')
        
        if msg_type == 'list':
            self.todos = msg_data
            self._refresh_list()
        elif msg_type == 'created':
            self.todos.insert(0, msg_data)
            self._refresh_list()
        elif msg_type == 'updated':
            for i, todo in enumerate(self.todos):
                if todo['id'] == msg_data['id']:
                    self.todos[i] = msg_data
                    break
            self._refresh_list()
        elif msg_type == 'deleted':
            self.todos = [t for t in self.todos if t['id'] != msg_data['id']]
            self._refresh_list()
        elif msg_type == 'error':
            wx.MessageBox(
                msg_data.get('message', 'Unknown error'),
                "Error",
                wx.OK | wx.ICON_ERROR
            )
    
    def _refresh_list(self):
        """Refresh the todo list display."""
        self.todo_list.DeleteAllItems()
        
        for todo in self.todos:
            index = self.todo_list.InsertItem(self.todo_list.GetItemCount(), "")
            
            # Checkbox column
            check = "☑" if todo['completed'] else "☐"
            self.todo_list.SetItem(index, 0, check)
            
            # Title column
            title = todo['title']
            if todo['completed']:
                title = f"~{title}~"
            self.todo_list.SetItem(index, 1, title)
            
            # Created date
            created = todo['created_at'][:10]  # Just the date
            self.todo_list.SetItem(index, 2, created)
            
            # Store todo id as item data
            self.todo_list.SetItemData(index, todo['id'])
    
    def _send_ws_message(self, msg_type, data=None):
        """Send a message through websocket."""
        if not self.is_connected or not self.ws:
            wx.MessageBox(
                "Not connected to server",
                "Connection Error",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        message = {
            'type': msg_type,
            'data': data or {}
        }
        self.ws.send(json.dumps(message))
    
    def on_add_todo(self, event=None):
        """Handle adding a new todo."""
        title = self.todo_input.GetValue().strip()
        if not title:
            return
        
        self._send_ws_message('create', {
            'title': title,
            'description': '',
            'completed': False
        })
        
        self.todo_input.Clear()
    
    def on_toggle_todo(self, event=None):
        """Handle toggling todo completion status."""
        selected = self.todo_list.GetFirstSelected()
        if selected == -1:
            return
        
        todo_id = self.todo_list.GetItemData(selected)
        todo = next((t for t in self.todos if t['id'] == todo_id), None)
        
        if todo:
            self._send_ws_message('update', {
                'id': todo_id,
                'completed': not todo['completed']
            })
    
    def on_edit_todo(self, event=None):
        """Handle editing a todo."""
        selected = self.todo_list.GetFirstSelected()
        if selected == -1:
            return
        
        todo_id = self.todo_list.GetItemData(selected)
        todo = next((t for t in self.todos if t['id'] == todo_id), None)
        
        if not todo:
            return
        
        # Show edit dialog
        dlg = wx.TextEntryDialog(
            self,
            "Edit todo:",
            "Edit Todo",
            todo['title']
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            new_title = dlg.GetValue().strip()
            if new_title:
                self._send_ws_message('update', {
                    'id': todo_id,
                    'title': new_title
                })
        
        dlg.Destroy()
    
    def on_delete_todo(self, event=None):
        """Handle deleting a todo."""
        selected = self.todo_list.GetFirstSelected()
        if selected == -1:
            return
        
        todo_id = self.todo_list.GetItemData(selected)
        
        # Confirm deletion
        dlg = wx.MessageDialog(
            self,
            "Delete this todo?",
            "Confirm Delete",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            self._send_ws_message('delete', {'id': todo_id})
        
        dlg.Destroy()
    
    def refresh_todos(self):
        """Request a refresh of the todo list."""
        self._send_ws_message('list')


def main():
    """Main entry point."""
    app = wx.App()
    frame = TodoFrame()
    app.MainLoop()


if __name__ == '__main__':
    main()

