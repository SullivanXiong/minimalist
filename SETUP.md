# Setup Guide

This guide will walk you through setting up the Minimalist Todo App from scratch.

## System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL
- **Python**: 3.11 or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7 or higher

## Step-by-Step Setup

### 1. Install Prerequisites

#### Install uv Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal or source your shell profile:

```bash
source ~/.bashrc  # or ~/.zshrc
```

#### Install System Dependencies (Linux)

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    postgresql \
    redis-server \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    build-essential
```

**Fedora:**

```bash
sudo dnf install -y \
    python3-devel \
    postgresql-server \
    redis \
    gtk3-devel \
    webkit2gtk3-devel \
    gcc
```

**macOS:**

```bash
brew install postgresql redis
```

### 2. Start Database Services

#### Option A: Using Docker (Recommended)

```bash
# Install Docker and Docker Compose if not already installed
# Then start services:
make services-up

# Or manually:
docker-compose up -d
```

#### Option B: Native Installation

**Start PostgreSQL:**

```bash
# Linux
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

**Create Database and User:**

```bash
sudo -u postgres psql
```

In PostgreSQL shell:

```sql
CREATE DATABASE todoapp;
CREATE USER todouser WITH PASSWORD 'todopass';
GRANT ALL PRIVILEGES ON DATABASE todoapp TO todouser;
\q
```

**Start Redis:**

```bash
# Linux
sudo systemctl start redis
sudo systemctl enable redis

# macOS
brew services start redis
```

### 3. Setup Quasarpy Library

The Quasarpy library should be in a sibling directory to minimalist:

```bash
cd /path/to/repos
ls
# Should show:
# minimalist/
# supyx/
```

If supyx doesn't exist yet, the setup will still work but vim navigation won't be available.

### 4. Setup Server

```bash
cd minimalist
make setup-server
```

This will:

- Install Python dependencies
- Create `.env` file from `.env.example`
- Run database migrations

**Edit Configuration:**

Open `server/.env` and update if needed:

```env
SECRET_KEY=change-this-to-a-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_NAME=todoapp
DATABASE_USER=todouser
DATABASE_PASSWORD=todopass
DATABASE_HOST=localhost
DATABASE_PORT=5432

REDIS_URL=redis://localhost:6379/0
```

**Create Admin User (Optional):**

```bash
make createsuperuser
```

### 5. Setup Client

```bash
make setup-client
```

This will install wxPython and other client dependencies.

**Note**: wxPython installation can take a few minutes as it needs to compile native components.

### 6. Run the Application

**Terminal 1 - Start Server:**

```bash
make dev-server
```

You should see:

```
2025-10-20 12:00:00 [INFO] Starting server at tcp:port=8000
```

**Terminal 2 - Start Client:**

```bash
make dev-client
```

The wxPython application window should open.

### 7. Verify Setup

1. **Check Server**: Open browser to `http://localhost:8000/admin/` and login
2. **Check WebSocket**: In client app, status bar should show "Connected"
3. **Test CRUD**:
   - Add a todo by typing in the input and clicking "Add"
   - Toggle completion by double-clicking a todo
   - Delete by selecting and clicking "Delete"

## Testing Vim Navigation

Once the client is running:

1. Press `Esc` to enter Normal mode (status bar shows "-- NORMAL --")
2. Press `f` to show hints on all clickable elements
3. Type hint letters to click that element
4. Press `/` to search within the app
5. Press `i` to focus the input field
6. Press `?` to see all keyboard shortcuts

## Troubleshooting

### "uv: command not found"

Make sure uv is installed and in your PATH:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### "Connection refused" when starting client

- Ensure Django server is running: `make dev-server`
- Check PostgreSQL is running: `pg_isready` or `docker ps`
- Check Redis is running: `redis-cli ping` (should return "PONG")

### wxPython installation fails

**Linux**: Install system dependencies first:

```bash
sudo apt-get install libgtk-3-dev libwebkit2gtk-4.0-dev
```

**macOS**: Install Xcode Command Line Tools:

```bash
xcode-select --install
```

### Database migrations fail

```bash
# Reset migrations (development only!)
cd server
rm -rf todos/migrations
uv run python manage.py makemigrations todos
uv run python manage.py migrate
```

### Vim navigation not working

Check if supyx is installed:

```bash
cd client
uv run python -c "import supyx; print('OK')"
```

If it fails, make sure the supyx directory exists at `../supyx/` relative to the project root.

### "Module not found: channels"

```bash
cd server
uv sync
```

## Next Steps

- **Add more todos**: Test the real-time synchronization
- **Customize keybindings**: Edit `client/app.py` to add your own vim commands
- **Deploy**: See README.md for production deployment instructions
- **Extend**: Add features like categories, tags, or due dates

## Development Tips

### Django Admin

Access at `http://localhost:8000/admin/` to manage todos directly.

### Database Shell

```bash
make shell
```

### View Logs

Server logs appear in the terminal where you ran `make dev-server`.

### Hot Reload

Django auto-reloads on code changes. For client changes, restart the client application.

## Clean Up

To stop and remove everything:

```bash
# Stop services
make services-down

# Clean generated files
make clean

# Remove virtual environments
rm -rf server/.venv client/.venv
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review error messages in terminal output
- Check Django logs for backend issues
- For supyx issues, see [supyx/README.md](../supyx/README.md)



