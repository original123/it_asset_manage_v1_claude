# API Endpoints Reference

Base URL: `/api`

## Authentication

### POST /auth/login
Login and get access tokens.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "user": { "id": 1, "username": "admin", ... }
  }
}
```

### POST /auth/logout
Logout current user (client should delete tokens).

### POST /auth/refresh
Refresh access token using refresh token.

**Headers:** `Authorization: Bearer <refresh_token>`

**Response:**
```json
{
  "code": 0,
  "data": { "access_token": "eyJ..." }
}
```

### GET /auth/me
Get current user info.

### POST /auth/change-password
Change current user's password.

**Request:**
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

---

## Servers

### GET /servers
List servers with pagination and filters.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| page | int | Page number (default: 1) |
| page_size | int | Items per page (default: 20, max: 100) |
| datacenter_id | int | Filter by datacenter |
| environment_id | int | Filter by environment |
| status | string | Filter by status (online/offline/maintenance) |
| keyword | string | Search in name, IPs, responsible_person |

### GET /servers/tree
Get server tree with nested containers, services, and GPUs.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| datacenter_id | int | Filter by datacenter |
| environment_id | int | Filter by environment |
| expand_level | int | 1=server, 2=+containers, 3=+services |

### GET /servers/:id
Get server details with children.

### POST /servers
Create new server. **Admin only.**

**Request:**
```json
{
  "name": "string (required)",
  "datacenter_id": "int (required)",
  "environment_id": "int (required)",
  "internal_ip": "string (required, valid IPv4)",
  "external_ip": "string (optional)",
  "cpu_cores": "int",
  "memory_gb": "int",
  "disk_gb": "int",
  "os_type": "string",
  "status": "online|offline|maintenance",
  "responsible_person": "string",
  "description": "string",
  "ssh_port": "int (default: 22)",
  "ssh_user": "string (default: root)"
}
```

### PUT /servers/:id
Update server. **Admin only.**

### DELETE /servers/:id
Delete server. **Admin only.**

---

## Containers

### GET /containers
List containers with filters.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| server_id | int | Filter by server |
| owner_id | int | Filter by owner |
| status | string | Filter by status |
| keyword | string | Search in name |

### GET /containers/:id
Get container details with port mappings.

### POST /containers
Create new container.

**Request:**
```json
{
  "name": "string (required)",
  "server_id": "int (required)",
  "image": "string",
  "container_id": "string",
  "cpu_limit": "float",
  "memory_limit_mb": "int",
  "status": "running|stopped|error",
  "description": "string",
  "port_mappings": [
    {
      "container_port": "int",
      "internal_ip": "string",
      "internal_port": "int",
      "external_ip": "string",
      "external_port": "int",
      "protocol": "tcp|udp",
      "description": "string"
    }
  ]
}
```

### PUT /containers/:id
Update container. **Admin or owner only.**

### DELETE /containers/:id
Delete container. **Admin or owner only.**

---

## Services

### GET /services
List services with filters.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| container_id | int | Filter by container |
| owner_id | int | Filter by owner |
| status | string | Filter by status |

### GET /services/:id
Get service details.

### POST /services
Create new service.

**Request:**
```json
{
  "name": "string (required)",
  "container_id": "int (required)",
  "service_type": "web|api|database|cache|queue|proxy|monitor|other",
  "port": "int (1-65535)",
  "version": "string",
  "status": "healthy|unhealthy|stopped",
  "health_check_url": "string",
  "description": "string"
}
```

### PUT /services/:id
Update service. **Admin or owner only.**

### DELETE /services/:id
Delete service. **Admin or owner only.**

---

## GPUs

### GET /gpus
List GPUs with filters.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| server_id | int | Filter by server |
| status | string | Filter by status (free/in_use/error) |
| assigned_to | int | Filter by assigned user |

### GET /gpus/:id
Get GPU details.

### POST /gpus
Create new GPU. **Admin only.**

**Request:**
```json
{
  "server_id": "int (required)",
  "model": "string (required)",
  "memory_gb": "int (required)",
  "index": "int (default: 0)",
  "status": "free|in_use|error",
  "description": "string"
}
```

### PUT /gpus/:id
Update GPU. **Admin only.**

### POST /gpus/:id/assign
Assign GPU to user. **Admin only.**

**Request:**
```json
{
  "user_id": "int (required)"
}
```

### POST /gpus/:id/release
Release GPU from user. **Admin only.**

### DELETE /gpus/:id
Delete GPU. **Admin only.**

---

## Datacenters

### GET /datacenters
List all active datacenters.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| include_stats | bool | Include server counts |

### GET /datacenters/overview
Get datacenter statistics overview.

### GET /datacenters/:id
Get datacenter details with stats.

### POST /datacenters
Create datacenter. **Admin only.**

**Request:**
```json
{
  "name": "string (required)",
  "location": "string",
  "description": "string"
}
```

### PUT /datacenters/:id
Update datacenter. **Admin only.**

### DELETE /datacenters/:id
Delete datacenter. **Admin only.** Fails if servers exist.

---

## Environments

### GET /environments
List all environments.

### GET /environments/:id
Get environment details with server count.

---

## Users

### GET /users
List users with filters. **Admin only.**

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| role | string | Filter by role |
| is_active | bool | Filter by active status |
| keyword | string | Search in username, display_name, email |

### GET /users/:id
Get user details. **Admin only.**

### POST /users
Create user. **Admin only.**

**Request:**
```json
{
  "username": "string (required, 3-64 chars)",
  "password": "string (required, 6-128 chars)",
  "display_name": "string (required)",
  "email": "string (optional, valid email)",
  "role": "admin|user",
  "is_active": "bool"
}
```

### PUT /users/:id
Update user. **Admin only.**

### DELETE /users/:id
Delete user. **Admin only.** Cannot delete self.

### GET /users/options
Get user options for dropdowns (id, username, display_name).

---

## Audit Logs

### GET /audit-logs
List audit logs with filters. **Admin only.**

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| user_id | int | Filter by user |
| action | string | Filter by action (create/update/delete) |
| resource_type | string | Filter by resource type |
| start_date | string | Filter by start date (YYYY-MM-DD) |
| end_date | string | Filter by end date |

### GET /audit-logs/:id
Get audit log details. **Admin only.**

---

## Search

### GET /search
Global search across all resources.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| q | string | Search query (required) |
| type | string | Filter by type (server/container/service/gpu) |

---

## Import/Export

### POST /import-export/import
Import data from Excel file. **Admin only.**

**Request:** multipart/form-data with Excel file

### GET /import-export/export
Export all data to Excel. **Admin only.**

### GET /import-export/template
Download import template Excel file.

---

## Common Response Codes

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request / Validation error |
| 401 | Unauthorized / Token invalid |
| 403 | Forbidden / Insufficient permissions |
| 404 | Resource not found |
| 422 | Validation failed |
| 500 | Internal server error |

## Pagination Response

All list endpoints return pagination info:

```json
{
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "pages": 5
  }
}
```
