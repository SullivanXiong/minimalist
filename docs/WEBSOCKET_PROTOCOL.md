# Minimalist WebSocket Protocol

## Connection

```
wss://<host>/ws/workspace/<slug>/?token=<jwt>
```

Authentication is required when `AUTH_REQUIRED=True`. Pass a valid JWT access token
as a query parameter.

## Message Envelope

All messages follow this structure:

```json
{
  "type": "message.type",
  "data": { ... },
  "request_id": "optional-correlation-id"
}
```

## Message Types

### Workspace

| Type | Direction | Description |
|------|-----------|-------------|
| `workspace.get` | client -> server | Request workspace state |
| `workspace.state` | server -> client | Full workspace context (sent on connect) |

**`workspace.state` data:**
```json
{
  "workspace": { "id": "uuid", "name": "...", "slug": "...", ... },
  "projects": [{ "id": "uuid", "name": "...", "statuses": [...], ... }],
  "labels": [{ "id": "uuid", "name": "...", ... }]
}
```

### Issues

| Type | Direction | Description |
|------|-----------|-------------|
| `issue.list` | client -> server | List issues (with filters) |
| `issue.list` | server -> client | Issue list response |
| `issue.create` | client -> server | Create new issue |
| `issue.created` | server -> client | Broadcast: issue created |
| `issue.update` | client -> server | Update issue fields |
| `issue.updated` | server -> client | Broadcast: issue updated |
| `issue.move` | client -> server | Move issue to new status |
| `issue.delete` | client -> server | Delete issue |
| `issue.deleted` | server -> client | Broadcast: issue deleted |

**`issue.create` data:**
```json
{
  "project_id": "uuid",
  "title": "Issue title",
  "description": "Optional description",
  "priority": 0,
  "status_id": "uuid (optional)",
  "parent_id": "uuid (optional)",
  "label_ids": ["uuid", "..."],
  "estimate": 3,
  "sort_order": 0
}
```

### Projects

| Type | Direction | Description |
|------|-----------|-------------|
| `project.list` | client -> server | List projects |
| `project.create` | client -> server | Create project |
| `project.created` | server -> client | Broadcast: project created |
| `project.update` | client -> server | Update project |
| `project.updated` | server -> client | Broadcast: project updated |
| `project.delete` | client -> server | Delete project |
| `project.deleted` | server -> client | Broadcast: project deleted |

### Labels

| Type | Direction | Description |
|------|-----------|-------------|
| `label.list` | client -> server | List labels |
| `label.create` | client -> server | Create label |
| `label.created` | server -> client | Broadcast: label created |
| `label.update` | client -> server | Update label |
| `label.updated` | server -> client | Broadcast: label updated |
| `label.delete` | client -> server | Delete label |
| `label.deleted` | server -> client | Broadcast: label deleted |

### Statuses

| Type | Direction | Description |
|------|-----------|-------------|
| `status.list` | client -> server | List statuses |
| `status.create` | client -> server | Create status |
| `status.created` | server -> client | Broadcast: status created |
| `status.update` | client -> server | Update status |
| `status.updated` | server -> client | Broadcast: status updated |
| `status.delete` | client -> server | Delete status (requires `move_to_id`) |
| `status.deleted` | server -> client | Broadcast: status deleted |

### Errors

| Type | Direction | Description |
|------|-----------|-------------|
| `error` | server -> client | Error response |

```json
{
  "type": "error",
  "data": { "message": "Error description" },
  "request_id": "correlation-id"
}
```
