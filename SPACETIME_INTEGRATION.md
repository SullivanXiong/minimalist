# spacetime Integration for minimalist

This project integrates with [spacetime](https://github.com/SullivanXiong/spacetime), a lightweight personal development environment tool.

## What is spacetime?

spacetime provides:
- Consistent shell configuration across machines
- Project-aware environment variables
- Custom aliases and functions
- Quick project navigation
- Cross-platform support (Windows, macOS, Linux)

## Files Added

### `.cursor/` - Cursor IDE Configuration
- **Dockerfile**: Container setup with Nix and spacetime
- **environments.json**: Pre-configured terminal commands
- **hooks/**: MCP execution hooks
- **setup-cursor-env.sh**: Automated environment setup

### `.envrc` - direnv Configuration
Automatically loads when entering the project directory:
- Activates Nix devenv
- Loads spacetime configuration
- Sets project-specific environment variables

### `env-shell` - Command Wrapper
Run commands in the Nix development environment:
```bash
./env-shell make dev-server
./env-shell python --version
```

### `.spacetime` - Project Configuration
Project-specific spacetime configuration loaded automatically.

## Quick Start

### 1. Install spacetime (First Time)

**On Windows (PowerShell):**
```powershell
cd $env:USERPROFILE
git clone https://github.com/SullivanXiong/spacetime.git
cd spacetime
.\setup.ps1
```

**On macOS/Linux/WSL:**
```bash
cd ~
git clone https://github.com/SullivanXiong/spacetime.git
cd spacetime
chmod +x setup.sh
./setup.sh
```

### 2. Setup Cursor Environment (if using Cursor)

```bash
cd minimalist
./.cursor/setup-cursor-env.sh
```

### 3. Allow direnv

```bash
direnv allow
```

## Usage

### Project-Specific Commands

When you `cd` into the minimalist directory, you get access to:

**Quick Navigation:**
```bash
server    # Go to server/ directory
client    # Go to client/ directory
supyx     # Go to ../supyx directory
ws        # Go to your workspace
```

**Development Functions:**
```bash
start-dev  # Start all services (PostgreSQL, Redis)
stop-dev   # Stop all services
reset-db   # Reset database completely
```

### Environment Variables

Available in the project:
- `$PROJECT_ROOT` - Project root directory
- `$PROJECT_NAME` - "minimalist"
- `$SERVER_DIR` - server/ path
- `$CLIENT_DIR` - client/ path
- `$DATABASE_URL` - PostgreSQL connection string
- `$DJANGO_DEV_URL` - Django server URL
- `$WEBSOCKET_URL` - WebSocket endpoint

### Cursor Terminal Commands

Pre-configured in `.cursor/environments.json`:

1. **Start Services** - Launch PostgreSQL and Redis
2. **Setup DB** - Run Django migrations
3. **Dev Server** - Start Django/Daphne server
4. **Dev Client** - Launch wxPython client

## Benefits

### 1. Consistent Environment
Same configuration across:
- Local development
- Cursor containers
- CI/CD pipelines
- Team members' machines

### 2. Auto-Loading
Environment automatically configured when entering project:
```bash
cd ~/minimalist
# spacetime and project config automatically loaded
```

### 3. Project Context
Commands know about your project structure:
```bash
# These work from anywhere in the project
server          # Jump to server/
make dev-server # Start Django
reset-db        # Reset database
```

### 4. No Conflicts
- Works alongside Nix/devenv
- Doesn't interfere with virtual environments
- Compatible with Docker

## Workflow Example

### Starting Development

```bash
# Navigate to project
cd ~/minimalist

# Environment auto-loads via direnv
# Output shows project info

# Start all services
start-dev

# In another terminal, start server
make dev-server

# In another terminal, start client
make dev-client
```

### Daily Development

```bash
# Jump to server code
server

# Make changes...
code .

# Run tests
make test

# Jump to client
client

# Test supyx changes
supyx
```

### Cleanup

```bash
# Stop services
stop-dev

# Or reset everything
reset-db
```

## Customization

### Add Project Aliases

Edit `.spacetime` in project root:

```bash
# Custom alias
alias test-api='curl http://localhost:8000/api/todos/'

# Custom function
deploy() {
    echo "Deploying $PROJECT_NAME..."
    docker-compose up --build
}
```

### Add Personal Aliases

Edit `~/.config/spacetime/aliases.sh` (or `.ps1` on Windows):

```bash
# Available in all projects
alias mycommand='echo "Hello"'
```

## Troubleshooting

### Commands not available

```bash
# Reload environment
direnv allow

# Or restart shell
exec $SHELL
```

### spacetime not installed

```bash
cd ~
git clone https://github.com/SullivanXiong/spacetime.git
cd spacetime
./setup.sh  # or setup.ps1 on Windows
```

### Environment not loading

Check if direnv is installed:
```bash
which direnv

# Install if needed (Nix)
nix-env -iA nixpkgs.direnv
```

### Project functions not working

Source the .spacetime file:
```bash
source .spacetime
```

## Integration with Other Tools

### Nix/devenv
- spacetime loads before Nix devenv
- Environment variables available to Nix
- No conflicts with nix packages

### uv (Python)
- spacetime PATH settings respected
- Works with uv virtual environments
- Python paths properly configured

### Docker
- spacetime variables available in Makefile
- Environment passed to containers
- Doesn't interfere with Docker commands

### Git
- Git aliases from spacetime available
- Project-aware git commands
- Doesn't modify .git/config

## See Also

- [spacetime Repository](https://github.com/SullivanXiong/spacetime)
- [spacetime Documentation](https://github.com/SullivanXiong/spacetime/blob/master/README.md)
- [minimalist README](README.md)

