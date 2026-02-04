.PHONY: setup setup-server setup-client dev-server dev-client migrate test clean format

# Configuration (override with: make dev-server SERVER_PORT=8080)
SERVER_PORT ?= 8000

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

# Run Django development server (override port: make dev-server SERVER_PORT=8080)
dev-server:
	cd server && uv run daphne -b 0.0.0.0 -p $(SERVER_PORT) config.asgi:application

# Run wxPython client
dev-client:
	cd client && uv run python app.py

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

# Note: PostgreSQL and Redis are managed by devenv
# Start services with: devenv up
# Change PostgreSQL port: POSTGRES_PORT=5433 direnv reload
