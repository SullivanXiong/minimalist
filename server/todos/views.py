from django.http import JsonResponse

from .models import Todo


def todo_list(request):
    """REST API endpoint to get all todos."""
    todos = Todo.objects.all()
    return JsonResponse({
        'todos': [todo.to_dict() for todo in todos]
    })




