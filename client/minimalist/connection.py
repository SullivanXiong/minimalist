"""WebSocket connection management."""

import json
import threading
import uuid

import websocket
import wx

from .auth import get_valid_token
from .config import AUTH_REQUIRED, WS_URL


class WebSocketConnection:
    """Manages WebSocket connection to the server."""

    def __init__(self):
        self.ws = None
        self.ws_thread = None
        self.is_connected = False
        self._handlers = {}
        self._status_callback = None

    def connect(self, workspace_slug):
        """Connect to a workspace WebSocket endpoint."""
        self.disconnect()

        url = f"{WS_URL}/ws/workspace/{workspace_slug}/"
        if AUTH_REQUIRED:
            token = get_valid_token()
            if token:
                url = f"{url}?token={token}"

        def on_message(ws, message):
            data = json.loads(message)
            msg_type = data.get('type')
            msg_data = data.get('data')
            wx.CallAfter(self._dispatch, msg_type, msg_data)

        def on_error(ws, error):
            if self._status_callback:
                wx.CallAfter(self._status_callback, False, str(error))

        def on_close(ws, close_status_code, close_msg):
            self.is_connected = False
            if self._status_callback:
                wx.CallAfter(self._status_callback, False, 'Disconnected')

        def on_open(ws):
            self.is_connected = True
            if self._status_callback:
                wx.CallAfter(self._status_callback, True, 'Connected')

        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )

        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def disconnect(self):
        """Close the WebSocket connection."""
        if self.ws:
            self.ws.close()
            self.ws = None
            self.is_connected = False

    def send(self, msg_type, data=None, request_id=None):
        """Send a typed message through the WebSocket."""
        if not self.is_connected or not self.ws:
            return

        message = {
            'type': msg_type,
            'data': data or {},
        }
        if request_id:
            message['request_id'] = request_id

        self.ws.send(json.dumps(message))

    def send_with_id(self, msg_type, data=None):
        """Send a message with an auto-generated request_id."""
        request_id = str(uuid.uuid4())[:8]
        self.send(msg_type, data, request_id)
        return request_id

    def on(self, msg_type, handler):
        """Register a handler for a message type."""
        if msg_type not in self._handlers:
            self._handlers[msg_type] = []
        self._handlers[msg_type].append(handler)

    def on_status(self, callback):
        """Register a connection status callback: callback(connected, message)."""
        self._status_callback = callback

    def _dispatch(self, msg_type, data):
        """Dispatch a message to registered handlers."""
        handlers = self._handlers.get(msg_type, [])
        for handler in handlers:
            handler(data)
