# Spec: Transform Minimalist Todo into Linear-like Project Management Tool

## Context

The Minimalist Todo App is currently a simple checklist — a single `Todo` model with title, description, and completed flag, displayed in a flat `wx.ListCtrl`. The goal is to transform it into a Linear-like project management tool with multi-column Kanban boards, workspaces, projects, and a keyboard-driven dark UI.

This spec documents the target architecture, data model, UI design, and phased implementation plan. It is delivered as a **Spec PR** (docs only) for approval before any implementation begins.

---

## Problem Statement

The current app is a flat todo checklist with no organizational hierarchy, no status workflow, and a basic light-themed UI. The target is a Linear-inspired issue tracker with:

- **Workspaces** for context separation (Work, Personal, Side Projects)
- **Projects** within workspaces for grouping related work
- **Issues** (replacing todos) with status, priority, and labels
- **Multi-column Kanban board** grouped by status
- **Dark-themed, keyboard-first UI** matching Linear's design language

### Success Criteria

1. Users can create multiple workspaces and switch between them
2. Each workspace has projects with configurable status workflows
3. Issues display in both Kanban board and list views
4. UI uses a dark theme with Linear-inspired visual design
5. All core actions are keyboard-accessible
6. Existing todos migrate cleanly to the new data model

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Organizational hierarchy | Workspace > Project > Issue (no Teams) | Linear uses Workspace > Team > Issue, but Teams add complexity unnecessary for a personal tool. Workspaces serve the "Work vs Personal" separation. |
| Issue identifiers | Workspace-scoped (`WORK-123`) | Linear scopes to teams; we scope to workspaces since we skip teams. |
| Primary keys | UUIDs for new models | Avoids sequential enumeration, simplifies future sync. Human-readable IDs via `identifier` field. |
| Status system | 5 categories with custom statuses per project | Matches Linear exactly: Backlog, Unstarted, Started, Completed, Cancelled. Custom status names map to a category. |
| Priority levels | 4 levels + None | Matches Linear: Urgent, High, Medium, Low, No Priority. |
| UI framework | Keep wxPython | Already in use. Dark theming is possible via custom panel painting. Native widgets accept color overrides. |
| Issue detail | Slide-in panel from right | Matches Linear's pattern. Uses `wx.SplitterWindow` with show/hide. |
| WebSocket scoping | Per-workspace connection | Client connects to `ws/workspace/<slug>/`, receives full workspace context. Reconnects on workspace switch. |
| Client architecture | Split `app.py` into package | Current 315-line monolith won't scale. New `minimalist/` package with views, dialogs, state management. |
| Color system | Dark mode default, monochrome + accent | Matches Linear's 2025 redesign: monochrome black/white with minimal bold colors. |
| Sub-issues | Include in v1 | Parent/child issue hierarchy. Issues can have sub-issues with inherited project/status context. |
| Estimate points | Include in v1 | Story point estimation on issues. Numeric values (1, 2, 3, 5, 8, 13, 21) matching Linear's Fibonacci scale. |
| Cycles/Sprints | Deferred to v2 | Time-boxed work periods add significant complexity. Not in initial scope. |
| Assignee field | Include in model, not in UI | Future-proofs for multi-user. FK to Django User, nullable, not surfaced in v1 UI. |
| Local persistence | JSON config file | `~/.config/minimalist/settings.json` stores last workspace, project, window size, view preference. |
| Default window size | 1200x800 | Comfortable fit for sidebar + 4-5 Kanban columns. |

---

## Current State

**Data model:** Single `Todo` model (id, title, description, completed, created_at, updated_at). No relationships.

**Server:** Django 5.1 + Channels + Daphne. One `TodoConsumer` at `ws/todos/` with 4 message types (create, update, delete, list). One REST endpoint (`GET /api/todos/`).

**Client:** Single `TodoFrame` class in `client/app.py`. Flat `wx.ListCtrl` with checkbox/title/date columns. 800x600 window with light theme.

**Infrastructure:** PostgreSQL 15, Redis, devenv/Nix, uv for deps.

---

## Target State

### Data Model

```
Workspace (1) ──< (many) Project
Workspace (1) ──< (many) Label
Workspace (1) ──< (many) Issue
Project   (1) ──< (many) Status
Project   (1) ──< (many) Issue
Status    (1) ──< (many) Issue
Issue    (many) >──< (many) Label
Issue     (1) ──< (many) Issue  (parent/sub-issue)
User      (1) ──< (many) Issue  (assignee, optional)
```

#### Workspace

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| name | CharField(100) | e.g., "Work", "Personal" |
| slug | SlugField(50) | Unique, URL-safe |
| identifier_prefix | CharField(10) | Unique, e.g., "WORK", "PERS" |
| issue_counter | PositiveIntegerField | Atomic counter for issue numbering |
| description | TextField | Optional |
| icon | CharField(10) | Emoji or icon name |
| created_at | DateTimeField | Auto |
| updated_at | DateTimeField | Auto |

#### Project

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| workspace | FK(Workspace) | CASCADE |
| name | CharField(200) | |
| slug | SlugField(100) | Unique within workspace |
| description | TextField | Optional |
| icon | CharField(10) | Emoji |
| color | CharField(7) | Hex color, default #6B7280 |
| sort_order | IntegerField | For sidebar ordering |
| created_at | DateTimeField | Auto |
| updated_at | DateTimeField | Auto |

#### Status

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project | FK(Project) | CASCADE |
| name | CharField(100) | Unique within project |
| category | CharField(20) | Choices: backlog, unstarted, started, completed, cancelled |
| color | CharField(7) | Hex color |
| sort_order | IntegerField | Column display order |
| is_default | BooleanField | One per project, used for new issues |
| created_at | DateTimeField | Auto |

Default statuses created per project:

1. Backlog (backlog, #95A2B3, sort=0)
2. Todo (unstarted, #E2E8F0, sort=1, **is_default**)
3. In Progress (started, #F59E0B, sort=2)
4. In Review (started, #8B5CF6, sort=3)
5. Done (completed, #10B981, sort=4)
6. Cancelled (cancelled, #EF4444, sort=5)

#### Label

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| workspace | FK(Workspace) | CASCADE |
| name | CharField(100) | Unique within workspace |
| color | CharField(7) | Hex color |
| description | TextField | Optional |
| created_at | DateTimeField | Auto |

#### Issue

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| identifier | CharField(30) | Unique, e.g., "WORK-123" |
| number | PositiveIntegerField | Sequential within workspace |
| workspace | FK(Workspace) | CASCADE |
| project | FK(Project) | CASCADE |
| status | FK(Status) | PROTECT |
| parent | FK(Issue, self) | Nullable, CASCADE. For sub-issues. |
| assignee | FK(User) | Nullable, SET_NULL. Not surfaced in v1 UI. |
| title | CharField(500) | |
| description | TextField | Optional |
| priority | IntegerField | 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low |
| estimate | IntegerField | Nullable. Fibonacci: 1, 2, 3, 5, 8, 13, 21 |
| labels | M2M(Label) | |
| sort_order | FloatField | For ordering within a status column |
| created_at | DateTimeField | Auto |
| updated_at | DateTimeField | Auto |
| completed_at | DateTimeField | Nullable, set when moved to completed |
| cancelled_at | DateTimeField | Nullable, set when moved to cancelled |
| legacy_todo_id | BigIntegerField | Nullable, for migration traceability |

**Sub-issue behavior:**
- Sub-issues inherit parent's project (enforced at creation)
- Sub-issues can have independent status, priority, labels, and estimates
- When all sub-issues reach "completed" category, prompt to complete parent (optional)
- Kanban cards show sub-issue count and completion progress (e.g., "2/5")

---

### UI Layout

```
+------------------------------------------------------------------+
|  Minimalist                                                [_][X] |
+----------+-------------------------------------------------------+
|          |  Toolbar: [Project v] [Board | List] [Filter] [+ New] |
|  Sidebar +-------------------------------------------------------+
|          |                                                        |
| [W] v    |  Kanban Board                                         |
| -------- |                                                        |
| Projects |  +----------+----------+----------+----------+         |
| > Backend|  | Backlog  | Todo     | In Prog  | Done     |         |
| > Front  |  |  (3)     |  (5)     |  (2)     |  (8)     |         |
| > Design |  |----------|----------|----------|----------|         |
| -------- |  | WORK-12  | WORK-8   | WORK-15  | WORK-1   |         |
| Labels   |  | Fix auth | Add API  | Refactor | Setup CI |         |
| > Bug    |  |  ! High  |  ~ Med   |  ~ Med   |          |         |
| > Feature|  |          |          |          |          |         |
| > Impr.  |  | WORK-14  | WORK-9   | WORK-16  | WORK-3   |         |
|          |  | DB mig.  | Tests    | Deploy   | Logging  |         |
|          |  +----------+----------+----------+----------+         |
|          |                                                        |
|          +---------------------------+----------------------------+
|          |  Issue Detail (slide-in)  |                            |
|          |  WORK-15 | In Progress    |                            |
|          |  [Refactor auth module]   |                            |
|          |  Priority: Medium         |                            |
|          |  Labels: [Improvement]    |                            |
|          |  Description: ...         |                            |
+----------+---------------------------+----------------------------+
|  Connected | WORK | Backend | 18 issues                          |
+------------------------------------------------------------------+
```

### Dark Theme Colors (Linear-inspired)

```python
DARK = {
    'bg_primary':    '#1A1A2E',   # Main background
    'bg_secondary':  '#16213E',   # Sidebar
    'bg_surface':    '#202437',   # Cards, panels
    'bg_hover':      '#2A2E45',   # Hover state
    'bg_selected':   '#1E4976',   # Selected state
    'bg_column':     '#1E1E32',   # Kanban column background
    'text_primary':  '#E2E8F0',   # Primary text
    'text_secondary':'#94A3B8',   # Secondary/muted text
    'text_muted':    '#64748B',   # Tertiary text
    'border':        '#334155',   # Borders
    'accent':        '#7C3AED',   # Brand accent (purple)
    'accent_hover':  '#6D28D9',   # Accent hover
}

PRIORITY = {
    'urgent': '#EF4444',  # Red
    'high':   '#F97316',  # Orange
    'medium': '#F59E0B',  # Yellow
    'low':    '#6B7280',  # Gray
}

STATUS = {
    'backlog':     '#95A2B3',
    'unstarted':   '#E2E8F0',
    'started':     '#F59E0B',
    'completed':   '#10B981',
    'cancelled':   '#EF4444',
}
```

### Keyboard Shortcuts (Linear-compatible)

**Global:**

| Key | Action |
|-----|--------|
| `c` | Create new issue |
| `/` | Focus search |
| `?` | Show shortcuts help |
| `Esc` | Close panel / clear selection |
| `Tab` | Cycle focus (sidebar <-> board) |

**Navigation:**

| Key | Action |
|-----|--------|
| `j` / Down | Next issue |
| `k` / Up | Previous issue |
| `h` / Left | Previous column (board) |
| `l` / Right | Next column (board) |
| `Enter` | Open issue detail |
| `g` then `w` | Workspace switcher |
| `g` then `p` | Focus project list |

**Issue Actions (with issue selected):**

| Key | Action |
|-----|--------|
| `e` | Edit title |
| `dd` | Delete (with confirm) |
| `x` | Toggle done/undone |
| `p` | Set priority |
| `L` | Set labels |
| `m` | Move to status (picker) |
| `]` | Move to next status |
| `[` | Move to previous status |
| `r` | Refresh |

---

## WebSocket Protocol v2

### Connection URL

`ws/workspace/<workspace_slug>/`

### Message Envelope

```json
{
    "type": "string",
    "data": {},
    "request_id": "string"
}
```

The `request_id` field is optional and echoed back in the response for client-side correlation.

### Server -> Client Messages

| Type | Payload | When |
|------|---------|------|
| `workspace.state` | `{workspace, projects: [{..., statuses: [...]}], labels}` | On connect |
| `issue.list` | `{issues: [...], total, page}` | Response to issue.list |
| `issue.created` | `{issue}` | After create |
| `issue.updated` | `{issue}` | After update |
| `issue.deleted` | `{id}` | After delete |
| `issue.moved` | `{issue, old_status_id}` | After status change |
| `project.created` | `{project}` | After create |
| `project.updated` | `{project}` | After update |
| `project.deleted` | `{id}` | After delete |
| `label.created` | `{label}` | After create |
| `label.updated` | `{label}` | After update |
| `label.deleted` | `{id}` | After delete |
| `status.created` | `{status}` | After create |
| `status.updated` | `{status}` | After update |
| `status.deleted` | `{id}` | After delete |
| `error` | `{message}` | On error |

### Client -> Server Messages

| Type | Payload |
|------|---------|
| `issue.list` | `{project_id, filters?, page?, page_size?}` |
| `issue.create` | `{project_id, title, description?, status_id?, priority?, estimate?, label_ids?, parent_id?}` |
| `issue.update` | `{id, title?, description?, priority?, estimate?, label_ids?, parent_id?}` |
| `issue.delete` | `{id}` |
| `issue.move` | `{id, status_id, sort_order?}` |
| `issue.reorder` | `{id, sort_order}` |
| `project.create` | `{name, description?, icon?, color?}` |
| `project.update` | `{id, name?, description?, icon?, color?}` |
| `project.delete` | `{id}` |
| `label.create` | `{name, color?, description?}` |
| `label.update` | `{id, name?, color?, description?}` |
| `label.delete` | `{id}` |
| `status.create` | `{project_id, name, category, color?}` |
| `status.update` | `{id, name?, color?, category?}` |
| `status.delete` | `{id, move_issues_to_status_id}` |
| `workspace.get` | `{}` |

---

## Migration Strategy

1. Create new `projects` Django app alongside existing `todos` app
2. **Migration 1**: Create all new tables (Workspace, Project, Status, Label, Issue)
3. **Migration 2**: Data migration — create default workspace ("Default", prefix "MIN"), default project ("General"), default statuses, convert each Todo to an Issue
4. **Migration 3** (deferred): Drop old `todos_todo` table after verification

Completed todos map to Issue with "Done" status. Incomplete todos map to Issue with "Todo" status (default).

---

## File Structure Changes

### New Server Files

```
server/projects/           # NEW Django app
  __init__.py
  apps.py
  models.py               # Workspace, Project, Status, Label, Issue
  consumers.py            # WorkspaceConsumer
  routing.py              # ws/workspace/<slug>/
  views.py                # REST endpoints
  urls.py                 # /api/workspaces/...
  serializers.py          # to_dict() helpers
  services.py             # Business logic (create_issue, move_issue)
  signals.py              # Auto-create default statuses on project create
  admin.py                # Admin for all models
  migrations/
  tests/
    test_models.py
    test_services.py
    test_consumers.py
    test_views.py
```

### Modified Server Files

- `server/config/settings.py` — Add `projects` to INSTALLED_APPS
- `server/config/asgi.py` — Import new routing
- `server/config/urls.py` — Add new API routes

### New Client Files

```
client/minimalist/         # NEW package (extracted from app.py)
  __init__.py
  main.py                 # MainFrame, app startup
  theme.py                # Dark theme colors, fonts
  config.py               # Server URL, settings
  connection.py           # WebSocket client, message routing
  state.py                # Client-side state cache
  models.py               # Dataclasses (Workspace, Project, Issue, etc.)
  keybindings.py          # Vim nav + Linear shortcuts
  views/
    sidebar.py            # WorkspaceSwitcher, ProjectList, LabelList
    toolbar.py            # Toolbar, FilterBar, ViewToggle
    kanban.py             # KanbanBoard, StatusColumn, IssueCard
    listview.py           # Enhanced ListCtrl
    issue_detail.py       # Slide-in detail panel
  dialogs/
    workspace.py          # Create/edit workspace
    project.py            # Create/edit project
    issue.py              # Create/edit issue
    status.py             # Manage statuses
    label.py              # Manage labels
  utils/
    formatting.py         # Date formatting, priority icons, estimate display
    persistence.py        # ~/.config/minimalist/settings.json read/write
```

### Modified Client Files

- `client/app.py` — Reduced to entry point (~20 lines, imports from `minimalist.main`)

---

## Phased Implementation

### Phase 1: Data Model & Server Foundation

Create `projects` Django app. All models, migrations (including data migration from todos), signals for default status creation, admin registration, and `services.py` business logic. No UI changes.

**Files**: All new `server/projects/` files except consumers.py, routing.py
**Depends on**: Nothing

### Phase 2: WebSocket Protocol v2

New `WorkspaceConsumer` with workspace-scoped connections. Full CRUD protocol for issues, projects, labels, statuses. Channel group broadcasting. Keep old `TodoConsumer` for backward compatibility.

**Files**: `server/projects/consumers.py`, `routing.py`, `serializers.py`, `config/asgi.py`
**Depends on**: Phase 1

### Phase 3: REST API

CRUD endpoints for all entities. Filtering and pagination for issues.

**Files**: `server/projects/views.py`, `urls.py`, `config/urls.py`
**Depends on**: Phase 1

### Phase 4: Client Restructuring

Split monolithic `app.py` into `minimalist/` package. State management, connection module, theme definitions, keybindings extraction. Old todo list still works.

**Files**: All new `client/minimalist/` core files (main.py, theme.py, config.py, connection.py, state.py, models.py, keybindings.py)
**Depends on**: Phase 2 (protocol to code against)

### Phase 5: Sidebar & Navigation

Workspace switcher, project list in left sidebar. `wx.SplitterWindow` layout. Workspace/project dialogs. Window resized to 1200x800.

**Files**: `client/minimalist/views/sidebar.py`, `dialogs/workspace.py`, `dialogs/project.py`, `main.py`
**Depends on**: Phase 4

### Phase 6: List View

Enhanced `wx.ListCtrl` with identifier, title, status, priority, labels, dates columns. Toolbar with project title, view toggle, filter bar.

**Files**: `client/minimalist/views/listview.py`, `views/toolbar.py`
**Depends on**: Phase 5

### Phase 7: Kanban Board

Multi-column board with custom-painted cards. Status columns with headers (name, count). Drag-and-drop or keyboard-based card movement between columns. View toggle (Board/List).

**Files**: `client/minimalist/views/kanban.py`, `dialogs/status.py`
**Depends on**: Phase 6

### Phase 8: Issue Detail Panel

Slide-in panel from right for full issue editing. Priority picker, label selector, status selector. Issue create dialog.

**Files**: `client/minimalist/views/issue_detail.py`, `dialogs/issue.py`, `dialogs/label.py`
**Depends on**: Phase 7

### Phase 9: Polish & Cleanup

Apply dark theme everywhere. Finalize keyboard shortcuts. Drop old `todos` app and table. Update documentation.

**Files**: Theme application across all views, `server/todos/` removal, docs
**Depends on**: Phase 8

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| wxPython Kanban drag-and-drop is non-trivial | Implement via mouse events (EVT_LEFT_DOWN/UP/MOTION). Fall back to keyboard `[`/`]` shortcuts if drag UX is poor. |
| Dark theming on macOS native widgets | Use custom-painted `wx.Panel` for cards and sidebar. Accept system-native scrollbars/menus. Test `wx.SystemSettings.SetAppearance()`. |
| supyx VimNavigationMixin assumes single ListCtrl | May need to extend supyx or build a custom focus manager for multi-panel layout. Test early in Phase 4. |
| Large issue counts (1000+) in Kanban | Lazy render only visible cards. Paginate issue loading. |

---

## Local Config Persistence

Client stores settings at `~/.config/minimalist/settings.json`:

```json
{
    "last_workspace_slug": "work",
    "last_project_id": "uuid-here",
    "view_preference": "board",
    "window": {
        "width": 1200,
        "height": 800,
        "x": 100,
        "y": 100,
        "maximized": false
    },
    "sidebar_width": 220
}
```

On launch: load config, connect to last workspace, select last project, restore window geometry.
On close: save current state. Config created on first run with defaults.

---

## Deferred to v2

These features are explicitly out of scope for v1:

- **Cycles/Sprints** — Time-boxed work periods with auto-roll
- **Custom views** — Saved filter/grouping configurations
- **Command palette** (Cmd+K) — Quick search and action execution
- **Issue relations** — Blocked/blocking/duplicate/related links
- **Activity log** — History of changes per issue
- **Notifications/Inbox** — Updates on subscribed issues
- **Multi-user** — Auth, permissions, assignee UI (model field exists but dormant)
- **Timeline/Gantt view**
- **Markdown description editing** — Rich text for issue descriptions

---

## Verification Plan

After each phase:

1. **Phase 1**: `make migrate` succeeds. Django admin shows all new models. Existing todos appear as Issues in admin.
2. **Phase 2**: Connect via WebSocket client to `ws/workspace/default/`. Send `issue.list`, receive issues. CRUD operations work.
3. **Phase 3**: `curl` REST endpoints return correct data. Filtering works.
4. **Phase 4**: `make dev-client` launches refactored client. Old todo functionality works unchanged.
5. **Phase 5**: Sidebar shows workspaces and projects. Switching projects updates the main view.
6. **Phase 6**: List view shows issues with all columns. Sorting and filtering work.
7. **Phase 7**: Kanban board renders columns per status. Cards display in correct columns. Moving cards updates status.
8. **Phase 8**: Clicking issue opens detail panel. Editing fields persists via WebSocket.
9. **Phase 9**: Dark theme applied. All shortcuts work. Clean startup with no legacy code warnings.

**End-to-end**: Create workspace -> Create project -> Create issues -> Move through statuses on Kanban -> Edit in detail panel -> Switch workspaces -> Verify all data persists.
