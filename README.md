# Minimalist Todo App

A modern todo list application with wxPython client and Django backend, featuring vim-like keyboard navigation inspired by Surfingkeys.

## Features

- 📝 **Clean Todo Interface**: Simple and focused todo management
- ⚡ **Real-time Sync**: WebSocket-based live updates
- ⌨️ **Vim Navigation**: Keyboard-first interface with vim-like shortcuts
- 🐍 **Python Stack**: Django backend + wxPython client
- 🔧 **Developer Friendly**: Make, Nix, and Docker support

## Vim Navigation

The client features vim-like navigation powered by the custom `supyx.wxnavimgation` library:

### Modes

- **Normal Mode** (default): Navigate and execute commands
- **Insert Mode** (`i`): Edit text fields
- **Hint Mode** (`f`): Show hints to click elements with keyboard
- **Search Mode** (`/`): Search within the application

### Key Bindings

| Key   | Action                                |
| ----- | ------------------------------------- |
| `i`   | Enter insert mode / Focus first input |
| `Esc` | Return to normal mode                 |
| `f`   | Show hints for clickable elements     |
| `/`   | Open search                           |
| `gi`  | Cycle through input fields            |
| `dd`  | Delete selected todo                  |
| `x`   | Toggle todo completion                |
| `e`   | Edit selected todo                    |
| `r`   | Refresh todo list                     |
| `?`   | Show keyboard shortcuts help          |

## Project Structure

```
minimalist/
├── client/              # wxPython application
│   ├── app.py          # Main client application
│   └── pyproject.toml  # Client dependencies
├── server/              # Django backend
│   ├── config/         # Django configuration
│   ├── todos/          # Todos app with WebSocket support
│   ├── manage.py       # Django management script
│   └── pyproject.toml  # Server dependencies
├── Makefile            # Build and dev commands
├── flake.nix          # Nix flake for reproducible environment
├── devenv.nix         # devenv configuration
├── Dockerfile         # Production containerization
└── docker-compose.yml # Local services (PostgreSQL, Redis)
```

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (for Django Channels)
- [uv](https://github.com/astral-sh/uv) package manager
- Make

Optional:

- Nix with flakes (for reproducible environment)
- Docker & Docker Compose

## Quick Start

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Start Services

Start PostgreSQL and Redis using Docker Compose:

```bash
make services-up
```

### 3. Setup Server

```bash
cd server
uv sync
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
uv run python manage.py migrate

# (Optional) Create superuser for admin panel
uv run python manage.py createsuperuser
```

### 4. Setup Client

```bash
cd client
uv sync
```

### 5. Run the Application

In one terminal, start the Django server:

```bash
make dev-server
# Or: cd server && uv run daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

In another terminal, start the wxPython client:

```bash
make dev-client
# Or: cd client && uv run python app.py
```

## Makefile Commands

```bash
make setup           # Initial project setup (both server and client)
make setup-server    # Setup Django server only
make setup-client    # Setup wxPython client only
make dev-server      # Run Django development server
make dev-client      # Run wxPython client
make migrate         # Run database migrations
make createsuperuser # Create Django admin user
make services-up     # Start PostgreSQL and Redis with Docker
make services-down   # Stop services
make test            # Run tests
make clean           # Clean generated files
make shell           # Open Django shell
```

## WebSocket Protocol

The client and server communicate via WebSocket using JSON messages:

### Client → Server

```json
{
  "type": "create|update|delete|list",
  "data": {
    "id": 1,
    "title": "Task title",
    "description": "Details",
    "completed": false
  }
}
```

### Server → Client

```json
{
  "type": "list|created|updated|deleted|error",
  "data": { ... }
}
```

## Database Schema

PostgreSQL `todos_todo` table:

| Column      | Type         | Description           |
| ----------- | ------------ | --------------------- |
| id          | integer      | Primary key           |
| title       | varchar(200) | Todo title            |
| description | text         | Optional description  |
| completed   | boolean      | Completion status     |
| created_at  | timestamp    | Creation timestamp    |
| updated_at  | timestamp    | Last update timestamp |

## Environment Variables

Server configuration (`.env`):

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_NAME=todoapp
DATABASE_USER=todouser
DATABASE_PASSWORD=todopass
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis (for Channels)
REDIS_URL=redis://localhost:6379/0
```

## Quasarpy Library

The vim navigation is powered by the separate `supyx` library located at `../supyx/`.

This library provides the `wxnavimgation` package for adding vim-like navigation to any wxPython application.

### Using in Your Own Projects

```python
import wx
from supyx.wxnavimgation import VimNavigationMixin

class MyFrame(VimNavigationMixin, wx.Frame):
    def __init__(self):
        super().__init__(None, title="My App")
        self.init_vim_navigation()

        # Add custom keybindings
        self.vim_nav.map_key('dd', self.delete_item, "Delete selected item")
```

See the [Quasarpy README](../supyx/README.md) for more information.

## Production Deployment

### Docker

Build and run with Docker:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`.

### Manual Deployment

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` appropriately
3. Set up a production-grade PostgreSQL and Redis
4. Run with a production ASGI server (Daphne is included)
5. Set up reverse proxy (nginx/traefik) for HTTPS

## Development

### Running Tests

```bash
make test
```

### Code Style

The project uses standard Python formatting. Consider using:

- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## Troubleshooting

### Can't connect to server

- Ensure PostgreSQL and Redis are running: `make services-up`
- Check Django server is running: `make dev-server`
- Verify WebSocket URL in `client/app.py` (default: `ws://localhost:8000/ws/todos/`)

### Database connection errors

- Check `.env` file exists in `server/` directory
- Verify PostgreSQL credentials match those in docker-compose.yml
- Ensure PostgreSQL is running: `docker ps`

### wxPython not installing

- On Linux, you may need system dependencies:

  ```bash
  # Ubuntu/Debian
  sudo apt-get install libgtk-3-dev libwebkit2gtk-4.0-dev

  # Fedora
  sudo dnf install gtk3-devel webkit2gtk3-devel
  ```

## License

MIT License - See LICENSE file for details

## Credits

- Vim navigation inspired by [Surfingkeys](https://github.com/brookhong/Surfingkeys)
- Built with Django, Django Channels, wxPython, and uv



