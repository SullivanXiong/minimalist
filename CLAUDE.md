# Minimalist — CLAUDE.md

Linear-inspired project management tool with multi-platform clients and cloud deployment.

## Project Overview

Full-stack app: Django 5.1 + Channels (WebSocket) + DRF backend, wxPython desktop client with vim-like keyboard navigation (via supyx), plus native Android (Kotlin/Compose) and iOS (Swift/SwiftUI) apps. JWT authentication via djangorestframework-simplejwt. Deployed via Docker + Caddy (staging on Raspberry Pi 4, prod on personal server).

## Development Setup

```bash
cd ~/repos/minimalist
direnv allow                # Nix flake activates automatically
make services-up            # Start PostgreSQL + Redis (docker-compose)
make setup-server           # Install server deps, create .env, run migrations
make setup-client           # Install client deps (wxPython, supyx)
```

**Run (two terminals):**
```bash
make dev-server             # Terminal 1: Daphne ASGI server
make dev-client             # Terminal 2: wxPython GUI
```

## Project Structure

```
server/
├── config/
│   ├── settings.py         # Router: imports based on DJANGO_ENV
│   ├── environments/       # base.py, development.py, staging.py, production.py
│   ├── asgi.py             # ASGI with JWT WebSocket middleware
│   └── urls.py             # /api/v1/ (DRF), /api/ (legacy), /api/auth/ (JWT)
├── accounts/               # JWT authentication (login, refresh, me)
│   ├── views.py            # DRF views for /api/auth/me/
│   ├── middleware.py        # JWTAuthMiddleware for WebSocket ?token= param
│   └── urls.py             # simplejwt TokenObtainPair + TokenRefresh
├── projects/               # Core app
│   ├── models.py           # Workspace, Project, Status, Label, Issue (UUID PKs)
│   ├── consumers.py        # WorkspaceConsumer (18 WS message types, auth gating)
│   ├── services.py         # Business logic (create_issue, move_issue, delete_status)
│   ├── views.py            # Legacy REST API (CRUD for all entities)
│   ├── api/                # DRF versioned API at /api/v1/
│   │   ├── serializers.py  # ModelSerializers for all models
│   │   ├── views.py        # DRF ViewSets
│   │   ├── urls.py         # DRF router
│   │   ├── filters.py      # Issue filtering
│   │   └── permissions.py  # Workspace-scoped permissions
│   ├── signals.py          # Auto-create 6 default statuses on new Project
│   └── serializers.py      # to_dict() helpers for WebSocket

client/
├── app.py                  # Thin entry point
├── minimalist.spec         # PyInstaller packaging spec
├── resources/              # App icons (generate with generate_icons.py)
├── minimalist/
│   ├── main.py             # MainFrame (Panel+BoxSizer, NO SplitterWindow)
│   ├── connection.py       # WebSocket client (JWT token in ?token= param)
│   ├── auth.py             # JWT login dialog, token storage/refresh
│   ├── version.py          # Version + auto-update check
│   ├── state.py            # AppState centralized state
│   ├── models.py           # Dataclasses with from_dict()
│   ├── theme.py            # Dark theme (bg=#0D0D0D, accent=#7C3AED)
│   ├── config.py           # Environment-aware server profiles (dev/stage/prod)
│   ├── keybindings.py      # Vim + Linear keyboard shortcuts
│   ├── views/              # sidebar, toolbar, kanban, listview, issue_detail
│   └── dialogs/            # issue, workspace, project, label, status

android/                    # Kotlin + Jetpack Compose (MVVM + Hilt + Retrofit)
ios/                        # Swift + SwiftUI (MVVM + URLSession + Keychain)

deploy/
├── docker-compose.base.yml # Shared: server, postgres, redis, caddy
├── docker-compose.stage.yml # Pi 4 resource limits
├── docker-compose.prod.yml # Production tuning
├── Caddyfile.{stage,prod}  # Auto-TLS reverse proxy
├── .env.{stage,prod}.example
└── scripts/                # backup-db.sh, restore-db.sh, deploy.sh

.github/workflows/
├── ci.yml                  # Lint + test on push/PR
├── docker.yml              # Multi-arch Docker build on tags
└── desktop-release.yml     # PyInstaller builds on tags
```

## Key Commands

```bash
make dev-server             # Run Django with Daphne on SERVER_PORT
make dev-client             # Run wxPython client (reads SERVER_PORT)
make migrate                # Run Django migrations
make shell                  # Django shell
make test                   # Run server + client tests
make format                 # Ruff format + check
make set-ports POSTGRES_PORT=X SERVER_PORT=Y  # Configure custom ports
make show-ports             # Display current port config
make rename-db              # Rename database from todoapp to minimalist
make services-up            # Start PostgreSQL + Redis via docker-compose
make services-down          # Stop docker-compose services
make deploy-stage           # Deploy to staging (Pi 4)
make deploy-prod            # Deploy to production
```

## Environment Configuration

**Server** (`DJANGO_ENV`): `development` (default), `staging`, `production`
- `settings.py` routes to `config/environments/{env}.py`
- Development: `DEBUG=True`, `AUTH_REQUIRED=False`
- Staging/Production: `DEBUG=False`, `AUTH_REQUIRED=True`, HSTS, secure cookies

**Client** (`MINIMALIST_ENV`): `development` (default), `staging`, `production`
- `config.py` selects server profile (URL, ws/wss scheme, auth requirement)

## Port Configuration (IMPORTANT)

Custom ports live in `.devenv.local` (JSON format):
```json
{"postgres_port":5433,"server_port":8003}
```

- Makefile reads this JSON and exports `DATABASE_PORT` and `SERVER_PORT` env vars
- Django `settings.py` reads `DATABASE_PORT` for PostgreSQL connection
- Client reads `SERVER_PORT` for WebSocket URL
- After changing ports: `direnv reload` in each terminal

## Authentication

- JWT via `djangorestframework-simplejwt` (1h access, 30d refresh, rotation enabled)
- REST: `Authorization: Bearer <token>` header
- WebSocket: `?token=<jwt>` query parameter
- `AUTH_REQUIRED=False` in development (no login needed locally)
- Client stores tokens in `~/.config/minimalist/auth.json`
- Login dialog appears automatically when auth is required and no valid token exists

## API

- **REST v1** (DRF): `/api/v1/workspaces/`, `/api/v1/workspaces/<slug>/issues/`, etc.
- **Legacy REST**: `/api/workspaces/` (backward compat)
- **WebSocket**: `ws(s)://<host>/ws/workspace/<slug>/` — see `docs/WEBSOCKET_PROTOCOL.md`
- **OpenAPI** (dev only): `GET /api/schema/` (YAML), `GET /api/docs/` (Swagger UI)

## Architecture Gotchas

1. **NO SplitterWindow** — macOS wxPython renders a red sash artifact. Use Panel+BoxSizer for all layouts.
2. **Signals don't fire in Django data migrations** — Must manually create default statuses in migration code, not rely on post_save signals.
3. **supyx dependency** — Client depends on `../../supyx/` (sibling directory). If missing, install fails. Will be published to PyPI for CI.
4. **Issue numbering** — Uses atomic F() expression increment on `workspace.issue_counter`. Don't set `issue_number` manually.
5. **WebSocket scoping** — Per-workspace at `ws/workspace/<slug>/`.
6. **Thread safety** — All WebSocket callbacks must use `wx.CallAfter()` to touch GUI from daemon thread.
7. **Detail panel parent navigation** — Use `wx.GetTopLevelParent(self)` not `self.GetParent().GetParent()`.
8. **Database name** — Changed from `todoapp` to `minimalist`. Run `make rename-db` if upgrading.
9. **Pi 4 resource limits** — Staging deployment on 4GB Pi needs tuned Postgres/Redis (see `docker-compose.stage.yml`).

## Conventions

- Python 3.11 (pinned via Nix). Use `python`, never `python3`.
- uv for package management (separate venvs for server/ and client/)
- Ruff for linting/formatting
- UUID primary keys on all new models, human-readable `identifier` field
- Commit style: `type: description` (lowercase, imperative) — e.g., `feat: add kanban board view`
- Dark theme colors consistent across all platforms (bg=#0D0D0D, accent=#7C5CFC)
