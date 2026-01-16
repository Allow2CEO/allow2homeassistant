# Allow2 API Integration Guide

This document describes how the Allow2 Home Assistant integration communicates with the Allow2 API using the **Device Pairing** model.

## Overview

Allow2 uses a device pairing model (similar to allow2nodered) rather than API key authentication. The integration pairs with a single parent's Allow2 account using their credentials, receives pairing tokens, and then uses those tokens for all subsequent API calls.

This is a **consumer device pairing** model, not a multi-tenant service model.

## Default Device Configuration

The Allow2 Home Assistant integration uses the following default device configuration:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `deviceToken` | `mtG8xbFR1cuJkuXn` | Pre-registered token for Home Assistant (vid=21588) |
| `vid` | `21588` | Vendor ID assigned to the Home Assistant integration |
| `deviceName` | `Home Assistant` | Default name (user can customize during pairing) |

## Authentication Flow

### Step 1: Initial Device Pairing (One-Time)

The integration performs a one-time pairing using the parent's Allow2 credentials:

**Endpoint:** `POST https://api.allow2.com/api/pairDevice`

**Request:**
```json
{
  "user": "parent@email.com",
  "pass": "password",
  "deviceToken": "mtG8xbFR1cuJkuXn",
  "name": "Home Assistant"
}
```

**Response (Success):**
```json
{
  "userId": 12345,
  "pairId": 67890,
  "token": "returned_pair_token",
  "children": [
    {"id": 111, "name": "Child 1"},
    {"id": 222, "name": "Child 2"}
  ]
}
```

**Important:** The `userId`, `pairId`, and `token` values MUST be persisted securely. These are used for all subsequent API calls.

**Response (Error):**
```json
{
  "error": "invalid_credentials"
}
```

### Step 2: Subsequent API Calls

After pairing, all API calls use the stored `userId`, `pairId`, and `pairToken` values. The parent's email and password are never stored.

## API Endpoints

### Check Quota / Activity Allowance

Use this endpoint to check if a child is allowed to perform specific activities.

**Endpoint:** `POST https://api.allow2.com/serviceapi/check`

> **Note:** This is `/serviceapi/check`, NOT `/serviceapi/checkRequest` (which is used for service/API key mode).

**Request:**
```json
{
  "userId": 12345,
  "pairId": 67890,
  "pairToken": "stored_token",
  "deviceToken": "mtG8xbFR1cuJkuXn",
  "tz": "Australia/Brisbane",
  "childId": 111,
  "activities": [1, 3, 7],
  "log": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | integer | Yes | User ID from pairing response |
| `pairId` | integer | Yes | Pair ID from pairing response |
| `pairToken` | string | Yes | Token from pairing response |
| `deviceToken` | string | Yes | Device token (`mtG8xbFR1cuJkuXn`) |
| `tz` | string | Yes | Timezone (IANA format, e.g., `Australia/Brisbane`) |
| `childId` | integer | Yes | ID of the child to check |
| `activities` | array | Yes | Array of activity IDs to check |
| `log` | boolean | No | Whether to log this activity check |

**Response (Success):**
```json
{
  "allowed": true,
  "activities": {
    "1": {
      "id": 1,
      "name": "Internet",
      "allowed": true,
      "remaining": 3600,
      "quota": 7200
    },
    "3": {
      "id": 3,
      "name": "Gaming",
      "allowed": false,
      "remaining": 0,
      "quota": 3600,
      "reason": "quota_exceeded"
    }
  },
  "dayTypes": {
    "today": "school_day",
    "tomorrow": "weekend"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `allowed` | boolean | Overall allowance (true if ANY activity is allowed) |
| `activities` | object | Per-activity allowance details |
| `activities[].allowed` | boolean | Whether this specific activity is allowed |
| `activities[].remaining` | integer | Remaining time in seconds |
| `activities[].quota` | integer | Total daily quota in seconds |
| `activities[].reason` | string | Reason for denial (if not allowed) |

## Activity IDs

Allow2 uses numeric IDs for different activity types:

| ID | Activity | Description |
|----|----------|-------------|
| 1 | Internet | General internet usage |
| 2 | Gaming | Video games, console, PC games |
| 3 | Social Media | Social networking sites |
| 4 | Television | TV watching, streaming services |
| 5 | Screen Time | General screen time |
| 6 | Messaging | Chat, messaging apps |
| 7 | Other | Miscellaneous activities |

> **Note:** Activity definitions may vary based on account configuration.

## Error Handling

### Common Error Responses

**Invalid Credentials (Pairing):**
```json
{
  "error": "invalid_credentials",
  "message": "The email or password is incorrect"
}
```

**Invalid Token (Check):**
```json
{
  "error": "invalid_token",
  "message": "The pair token is invalid or expired"
}
```

**Child Not Found:**
```json
{
  "error": "child_not_found",
  "message": "The specified child ID does not exist"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 401 | Unauthorized (invalid credentials or token) |
| 403 | Forbidden (device not paired) |
| 404 | Not Found (child or resource not found) |
| 429 | Rate Limited (too many requests) |
| 500 | Server Error |

## Key Differences from Service Mode

This integration uses **Device Pairing Mode**, not **Service Mode**:

| Aspect | Device Pairing Mode | Service Mode |
|--------|---------------------|--------------|
| Authentication | Email/password for one-time pairing | API key |
| Stored Credentials | userId, pairId, pairToken | API key |
| Endpoint | `/serviceapi/check` | `/serviceapi/checkRequest` |
| Use Case | Single family connection | Multi-tenant service |
| Device Token | Required (identifies device type) | Not required |

## Security Considerations

1. **Never store parent credentials** - Only the pairing tokens are stored
2. **Secure token storage** - Use Home Assistant's encrypted storage for tokens
3. **Token refresh** - Re-pair if tokens become invalid
4. **HTTPS only** - All API calls use TLS encryption

## Rate Limiting

- Quota checks: Maximum 1 request per child per minute recommended
- Pairing: Maximum 10 attempts per hour per IP
- Implement exponential backoff on 429 responses

## Example Integration Flow

```
1. User enters Allow2 credentials in Home Assistant UI
2. Integration calls /api/pairDevice with credentials
3. On success, store userId, pairId, token securely
4. Discard credentials (never stored)
5. Periodically call /serviceapi/check for each child
6. Update Home Assistant entities based on responses
7. If token becomes invalid, prompt user to re-pair
```

## Implementation Patterns

### Caching Strategy

To reduce API calls, implement local caching:

```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class QuotaCache:
    """Local cache for quota responses to reduce API calls."""

    def __init__(self, ttl_seconds: int = 300):
        """Initialize cache with TTL (default: 5 minutes)."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def _cache_key(self, child_id: int, activity: str) -> str:
        """Generate cache key."""
        return f"{child_id}:{activity}"

    def get(self, child_id: int, activity: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached quota data if still valid."""
        key = self._cache_key(child_id, activity)

        if key not in self._cache:
            return None

        cached = self._cache[key]
        timestamp = cached.get("timestamp")

        if not timestamp:
            return None

        age = datetime.now() - timestamp

        if age > self._ttl:
            del self._cache[key]
            return None

        return cached.get("data")

    def set(self, child_id: int, activity: str, data: Dict[str, Any]) -> None:
        """Store quota data in cache."""
        key = self._cache_key(child_id, activity)
        self._cache[key] = {
            "timestamp": datetime.now(),
            "data": data
        }
```

### Error Handling and Retry Logic

Implement exponential backoff for transient failures:

```python
import asyncio
from functools import wraps

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry API calls on failure."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except RateLimitError:
                    # Longer wait for rate limits
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt) * 2
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                except AuthError:
                    # Don't retry auth errors
                    raise
                except APIError as err:
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        await asyncio.sleep(wait_time)
                    else:
                        raise
        return wrapper
    return decorator
```

### Graceful Degradation (Fail-Open)

When the API is unavailable, fail safely:

```python
async def check_quota_with_fallback(
    api_client,
    cache: QuotaCache,
    child_id: int,
    activity: str,
    device_id: Optional[str] = None
) -> Dict[str, Any]:
    """Check quota with fallback to cached data on API failure."""
    try:
        # Try API call
        quota_data = await api_client.check_quota(child_id, activity, device_id)
        cache.set(child_id, activity, quota_data)
        return quota_data

    except APIError as err:
        # Try to use cached data (even if expired)
        cached_data = cache.get(child_id, activity)

        if cached_data:
            cached_data["_from_cache"] = True
            return cached_data

        # No cache available - fail open (allow usage)
        return {
            "allowed": True,  # Fail-open: allow usage
            "remaining_seconds": 3600,
            "remaining_minutes": 60,
            "reason": "API unavailable - using default allowance",
            "_error": True
        }
```

### Client-Side Rate Limiting

Prevent hitting API rate limits:

```python
from collections import deque

class RateLimiter:
    """Client-side rate limiter to avoid hitting API limits."""

    def __init__(self, max_calls: int = 60, window_seconds: int = 60):
        """Initialize with max calls per window."""
        self._max_calls = max_calls
        self._window = timedelta(seconds=window_seconds)
        self._calls: deque = deque()

    async def acquire(self) -> None:
        """Wait if necessary to respect rate limit."""
        now = datetime.now()

        # Remove old calls outside the window
        while self._calls and self._calls[0] < now - self._window:
            self._calls.popleft()

        # If at limit, wait until oldest call expires
        if len(self._calls) >= self._max_calls:
            wait_until = self._calls[0] + self._window
            wait_seconds = (wait_until - now).total_seconds()

            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

        self._calls.append(now)
```

## Best Practices

### 1. Always Use Caching
Reduce API calls by caching quota responses for 5 minutes.

### 2. Implement Retry Logic
Handle transient network errors with exponential backoff.

### 3. Fail Open, Not Closed
If API is unavailable, default to allowing usage (better user experience).

### 4. Log API Errors
Help parents troubleshoot by logging detailed error information.

### 5. Respect Rate Limits
Implement client-side rate limiting to avoid hitting API limits.

### 6. Use Appropriate Timeouts
Set reasonable timeouts (10 seconds) to avoid blocking Home Assistant.

### 7. Handle Timezones Correctly
Pass user's timezone to API for accurate quota calculation.

## Webhook Support (Future Enhancement)

Allow2 may support webhooks for real-time notifications. When implemented, this could provide:

- Instant notification when quotas change
- Real-time ban/unban events
- Day type changes at midnight

Currently, the integration relies on polling. Webhook support may be added in future versions.

## References

- [Allow2 Developer Documentation](https://developer.allow2.com)
- [allow2nodered Reference Implementation](https://github.com/AuScope/allow2nodered)
- [Main Documentation](../DOCS.md)
- [Configuration Guide](CONFIGURATION.md)
- [Changelog](../CHANGELOG.md)
