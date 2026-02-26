.PHONY: setup setup-server setup-client dev-server dev-client migrate test clean format set-ports reset-ports show-ports rename-db services-up services-down deploy-stage deploy-prod

# Configuration - reads from .devenv.local if it exists, otherwise uses defaults
SERVER_PORT := $(shell if [ -f .devenv.local ]; then python3 -c "import json; print(json.load(open('.devenv.local')).get('server_port', 8000))"; else echo 8000; fi)
POSTGRES_PORT := $(shell if [ -f .devenv.local ]; then python3 -c "import json; print(json.load(open('.devenv.local')).get('postgres_port', 5432))"; else echo 5432; fi)

# Initial project setup
setup: setup-server setup-client
	@echo "Setup complete! Run 'make dev-server' and 'make dev-client' in separate terminals."

# Server setup
setup-server:
	@echo "Setting up Django server..."
	cd server && uv sync
	@if [ ! -f server/.env ]; then \
		cp server/.env.example server/.env; \
		echo "Created server/.env from .env.example - please update with your settings"; \
	fi
	@echo "Running migrations..."
	cd server && uv run python manage.py migrate
	@echo "Server setup complete!"

# Client setup
setup-client:
	@echo "Setting up wxPython client..."
	cd client && uv sync
	@echo "Client setup complete!"

# Run Django development server (uses ports from .devenv.local or defaults)
dev-server:
	@echo "Starting server on port $(SERVER_PORT) (PostgreSQL: $(POSTGRES_PORT))..."
	cd server && DATABASE_PORT=$(POSTGRES_PORT) uv run daphne -b 0.0.0.0 -p $(SERVER_PORT) config.asgi:application

# Run wxPython client
dev-client:
	cd client && SERVER_PORT=$(SERVER_PORT) uv run python app.py

# Run database migrations
migrate:
	cd server && uv run python manage.py makemigrations
	cd server && uv run python manage.py migrate

# Create Django superuser
createsuperuser:
	cd server && uv run python manage.py createsuperuser

# Run tests
test:
	cd server && uv run python manage.py test
	cd client && uv run python -m pytest

# Format code with ruff
format:
	./format_code.sh

# Clean generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

# Django shell
shell:
	cd server && uv run python manage.py shell

# Configure local ports (writes to .devenv.local)
# Usage: make set-ports POSTGRES_PORT=5433 SERVER_PORT=8080
set-ports:
	@echo '{"postgres_port":$(POSTGRES_PORT),"server_port":$(SERVER_PORT)}' > .devenv.local
	@echo "Updated .devenv.local: postgres=$(POSTGRES_PORT), server=$(SERVER_PORT)"
	@echo "Run 'direnv reload' in each terminal to apply"

# Reset to default ports
reset-ports:
	@rm -f .devenv.local
	@echo "Removed .devenv.local (using defaults: postgres=5432, server=8000)"
	@echo "Run 'direnv reload' in each terminal to apply"

# Show current port configuration
show-ports:
	@if [ -f .devenv.local ]; then \
		echo "Custom ports (.devenv.local):"; \
		cat .devenv.local | python3 -c "import sys,json; c=json.load(sys.stdin); print(f'  PostgreSQL: {c.get(\"postgres_port\", 5432)}'); print(f'  Server: {c.get(\"server_port\", 8000)}')"; \
	else \
		echo "Using defaults:"; \
		echo "  PostgreSQL: 5432"; \
		echo "  Server: 8000"; \
	fi

# Rename database from legacy 'todoapp' to 'minimalist'
rename-db:
	@echo "Renaming database todoapp -> minimalist..."
	cd server && DATABASE_PORT=$(POSTGRES_PORT) uv run python -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT 1')" 2>/dev/null && echo "Already connected to minimalist" || \
	psql -h localhost -p $(POSTGRES_PORT) -c "ALTER DATABASE todoapp RENAME TO minimalist;" 2>/dev/null && echo "Renamed successfully" || echo "Database already named minimalist (or todoapp does not exist)"

# Docker compose services (local dev)
services-up:
	docker compose up -d postgres redis
	@echo "Waiting for services..."
	@sleep 3
	@echo "Services ready."

services-down:
	docker compose down

# Deployment
deploy-stage:
	cd deploy && ./scripts/deploy.sh stage

deploy-prod:
	cd deploy && ./scripts/deploy.sh prod

# Note: PostgreSQL and Redis are managed by devenv
# Start services with: devenv up
