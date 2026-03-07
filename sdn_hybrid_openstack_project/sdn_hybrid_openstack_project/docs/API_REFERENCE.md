# API Reference

## Controller REST API
Base URL example: `http://10.10.10.10:8080`

### GET `/lb/status`
Returns:
- VIP information
- controller timing / mode
- backend list
- current GA weights
- active flow count
- eligible backends

### POST `/lb/recompute`
Triggers an immediate GA recomputation.

Response example:
```json
{
  "weights": {
    "srv1": 0.52,
    "srv2": 0.28,
    "srv3": 0.20
  }
}
```

### POST `/lb/health/<name>`
Set backend health manually.

Request body:
```json
{"healthy": false}
```

## Flask Dashboard
Base URL example: `http://10.10.10.10:5555`

Features:
- view controller state
- trigger GA recompute
- mark backend healthy/unhealthy
- inspect OpenStack instances, networks, and floating IPs
- optionally scale out/in managed OpenStack servers when SDK settings are provided
