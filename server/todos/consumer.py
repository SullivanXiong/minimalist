import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Todo


class TodoConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time todo CRUD operations."""

    async def connect(self):
        """Handle websocket connection."""
        await self.accept()
        # Send initial todo list
        todos = await self.get_all_todos()
        await self.send(text_data=json.dumps({
            'type': 'list',
            'data': todos
        }))

    async def disconnect(self, close_code):
        """Handle websocket disconnection."""
        pass

    async def receive(self, text_data):
        """Handle incoming websocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            message_data = data.get('data', {})

            if message_type == 'create':
                todo = await self.create_todo(message_data)
                await self.send(text_data=json.dumps({
                    'type': 'created',
                    'data': todo
                }))

            elif message_type == 'update':
                todo = await self.update_todo(message_data)
                await self.send(text_data=json.dumps({
                    'type': 'updated',
                    'data': todo
                }))

            elif message_type == 'delete':
                todo_id = message_data.get('id')
                await self.delete_todo(todo_id)
                await self.send(text_data=json.dumps({
                    'type': 'deleted',
                    'data': {'id': todo_id}
                }))

            elif message_type == 'list':
                todos = await self.get_all_todos()
                await self.send(text_data=json.dumps({
                    'type': 'list',
                    'data': todos
                }))

        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'data': {'message': str(e)}
            }))

    @database_sync_to_async
    def get_all_todos(self):
        """Get all todos from database."""
        todos = Todo.objects.all()
        return [todo.to_dict() for todo in todos]

    @database_sync_to_async
    def create_todo(self, data):
        """Create a new todo."""
        todo = Todo.objects.create(
            title=data.get('title', ''),
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )
        return todo.to_dict()

    @database_sync_to_async
    def update_todo(self, data):
        """Update an existing todo."""
        todo_id = data.get('id')
        todo = Todo.objects.get(id=todo_id)
        
        if 'title' in data:
            todo.title = data['title']
        if 'description' in data:
            todo.description = data['description']
        if 'completed' in data:
            todo.completed = data['completed']
        
        todo.save()
        return todo.to_dict()

    @database_sync_to_async
    def delete_todo(self, todo_id):
        """Delete a todo."""
        todo = Todo.objects.get(id=todo_id)
        todo.delete()




