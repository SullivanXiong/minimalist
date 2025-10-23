# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

```bash
# Check if uv is installed
uv --version

# If not installed:
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

## Installation (3 steps)

### 1. Start Services

```bash
# Start PostgreSQL and Redis with Docker
make services-up

# Wait 10 seconds for services to start
sleep 10
```

### 2. Setup Backend

```bash
# Install dependencies and run migrations
make setup-server

# This will:
# - Install Django, Channels, etc.
# - Create .env file
# - Run database migrations
```

### 3. Setup Client

```bash
# Install wxPython and dependencies (takes 2-5 minutes)
make setup-client
```

## Running the App

Open **two terminals**:

**Terminal 1 - Backend:**

```bash
make dev-server
# Wait for: "Starting server at tcp:port=8000"
```

**Terminal 2 - Client:**

```bash
make dev-client
# wxPython window will open
```

## Using the App

### Mouse Mode (Beginner)

1. Type a todo in the input box
2. Click "Add" button
3. Double-click a todo to mark as complete
4. Select a todo and click "Delete" to remove it

### Vim Mode (Pro)

1. Press `Esc` to enter Normal mode (see status bar)
2. Press `i` to focus input field → type todo → press `Enter`
3. Press `Esc` to return to Normal mode
4. Press `f` to show hints, type letter to click
5. Press `x` to toggle completion
6. Press `dd` to delete selected todo
7. Press `/` to search
8. Press `?` for help

## Keyboard Shortcuts

| Key   | Action            |
| ----- | ----------------- |
| `i`   | Enter insert mode |
| `Esc` | Normal mode       |
| `f`   | Show hints        |
| `/`   | Search            |
| `gi`  | Next input        |
| `dd`  | Delete            |
| `x`   | Toggle            |
| `e`   | Edit              |
| `r`   | Refresh           |
| `?`   | Help              |

## Troubleshooting

### "Connection refused"

```bash
# Check if services are running
docker ps

# Should show postgres and redis containers
# If not:
make services-up
```

### "uv: command not found"

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version
```

### wxPython installation fails (Linux)

```bash
sudo apt-get install libgtk-3-dev libwebkit2gtk-4.0-dev
make setup-client
```

### Client can't connect to server

1. Make sure server is running: `make dev-server`
2. Check http://localhost:8000/health/ in browser
3. If 404, server is not running
4. If connection refused, check firewall

## What's Next?

- **Customize**: Edit `client/app.py` to add your own keybindings
- **Deploy**: See README.md for production setup
- **Learn**: Check SETUP.md for detailed documentation

## Stop Everything

```bash
# Stop services
make services-down

# Clean up
make clean
```

---

**Need Help?** See [SETUP.md](SETUP.md) for detailed troubleshooting.



