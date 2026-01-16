# Allow2 Home Assistant Integration - API Integration

## Overview

This document describes how **allow2homeassistant** communicates with the Allow2 cloud API. It's designed similarly to [allow2nodered](https://www.npmjs.com/package/allow2nodered), adapted for Home Assistant's Python environment.

## Allow2 API Basics

### Base URL
```
https://api.allow2.com
```

### Authentication
All requests use API Key authentication:
```
Authorization: Bearer ak_your_api_key_here
```

### Content Type
```
Content-Type: application/json
```

## API Endpoints

### 1. Check Quota & Request Access

**Endpoint**: `POST /serviceapi/checkRequest`

**Purpose**: Check if a child has quota remaining for an activity.

**Request**:
```json
{
  "userId": 12345,
  "activity": "gaming",
  "deviceId": "xbox_living_room",
  "tz": "America/Los_Angeles"
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `userId` | integer | Yes | Child's Allow2 user ID |
| `activity` | string | Yes | Activity type (lowercase) |
| `deviceId` | string | No | Device identifier for logging |
| `tz` | string | No | Timezone (e.g., "America/New_York") |

**Response** (Success):
```json
{
  "allowed": true,
  "activities": {
    "gaming": {
      "id": 3,
      "name": "Gaming",
      "timed": true,
      "remaining": 7200,
      "cached": false,
      "units": "seconds",
      "expires": "2026-01-15T23:59:59Z"
    }
  },
  "dayTypes": {
    "today": {
      "name": "School Day",
      "maxTime": 7200
    }
  },
  "ban": null,
  "subscription": {
    "active": true,
    "expires": "2026-12-31T23:59:59Z"
  }
}
```

**Response** (Quota Exhausted):
```json
{
  "allowed": false,
  "activities": {
    "gaming": {
      "id": 3,
      "name": "Gaming",
      "timed": true,
      "remaining": 0,
      "cached": false,
      "units": "seconds",
      "expires": "2026-01-15T23:59:59Z"
    }
  },
  "dayTypes": {
    "today": {
      "name": "School Day",
      "maxTime": 7200
    }
  },
  "ban": null,
  "reason": "daily quota exhausted"
}
```

**Response** (Ban Window):
```json
{
  "allowed": false,
  "activities": {
    "gaming": {
      "id": 3,
      "name": "Gaming",
      "timed": true,
      "remaining": 3600,
      "cached": false,
      "units": "seconds"
    }
  },
  "ban": {
    "reason": "Homework time",
    "start": "16:00:00",
    "end": "18:00:00"
  },
  "reason": "ban window active"
}
```

**Error Response**:
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or expired"
  }
}
```

### 2. Log Activity

**Endpoint**: `POST /serviceapi/logActivity`

**Purpose**: Record device usage time for a child.

**Request**:
```json
{
  "userId": 12345,
  "activity": "gaming",
  "deviceId": "xbox_living_room",
  "duration": 300,
  "tz": "America/Los_Angeles"
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `userId` | integer | Yes | Child's Allow2 user ID |
| `activity` | string | Yes | Activity type |
| `deviceId` | string | No | Device identifier |
| `duration` | integer | Yes | Usage time in seconds |
| `tz` | string | No | Timezone |

**Response** (Success):
```json
{
  "success": true,
  "logged": {
    "activity": "gaming",
    "duration": 300,
    "timestamp": "2026-01-15T15:30:00Z"
  },
  "remaining": {
    "gaming": 6900
  }
}
```

**Note**: The `check_quota` service automatically logs activity, so manual logging is rarely needed.

### 3. Get Children (Internal Use)

**Endpoint**: `GET /serviceapi/children`

**Purpose**: Retrieve list of children associated with the API key.

**Request**:
```
GET /serviceapi/children
Authorization: Bearer ak_your_api_key
```

**Response**:
```json
{
  "children": [
    {
      "id": 12345,
      "name": "Johnny",
      "dateOfBirth": "2014-03-15",
      "avatar": "https://allow2.com/avatars/12345.jpg"
    },
    {
      "id": 67890,
      "name": "Sarah",
      "dateOfBirth": "2016-07-22",
      "avatar": "https://allow2.com/avatars/67890.jpg"
    }
  ]
}
```

**Used By**: Integration setup to validate API key and display available children.

## Python API Client Implementation

### API Client Class Structure

```python
# custom_components/allow2/api.py

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://api.allow2.com"
API_TIMEOUT = 10  # seconds

class Allow2APIError(Exception):
    """Base exception for Allow2 API errors."""
    pass

class Allow2AuthError(Allow2APIError):
    """Authentication error (invalid API key)."""
    pass

class Allow2RateLimitError(Allow2APIError):
    """Rate limit exceeded."""
    pass

class Allow2API:
    """Client for communicating with Allow2 API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        """Initialize API client.

        Args:
            api_key: Allow2 parent account API key
            session: aiohttp ClientSession for making requests
        """
        self._api_key = api_key
        self._session = session
        self._timezone = str(datetime.now(timezone.utc).astimezone().tzinfo)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Allow2 API.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            data: Request body data (for POST)

        Returns:
            Response data as dictionary

        Raises:
            Allow2AuthError: Invalid API key
            Allow2RateLimitError: Rate limit exceeded
            Allow2APIError: Other API errors
        """
        url = f"{API_BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": "allow2homeassistant/1.0.0"
        }

        try:
            async with asyncio.timeout(API_TIMEOUT):
                if method == "GET":
                    async with self._session.get(url, headers=headers) as response:
                        return await self._handle_response(response)
                elif method == "POST":
                    async with self._session.post(
                        url, headers=headers, json=data
                    ) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout communicating with Allow2 API")
            raise Allow2APIError("Request timeout")
        except aiohttp.ClientError as err:
            _LOGGER.error("Error communicating with Allow2 API: %s", err)
            raise Allow2APIError(f"Connection error: {err}")

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response and errors.

        Args:
            response: aiohttp response object

        Returns:
            Parsed JSON response

        Raises:
            Allow2AuthError: Authentication failed
            Allow2RateLimitError: Rate limit exceeded
            Allow2APIError: Other errors
        """
        try:
            data = await response.json()
        except aiohttp.ContentTypeError:
            text = await response.text()
            _LOGGER.error("Invalid JSON response: %s", text)
            raise Allow2APIError("Invalid response from API")

        if response.status == 200:
            return data

        # Handle error responses
        if response.status == 401:
            error_msg = data.get("error", {}).get("message", "Invalid API key")
            _LOGGER.error("Authentication failed: %s", error_msg)
            raise Allow2AuthError(error_msg)

        if response.status == 429:
            _LOGGER.warning("Allow2 API rate limit exceeded")
            raise Allow2RateLimitError("Rate limit exceeded")

        if response.status >= 400:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            _LOGGER.error("Allow2 API error %s: %s", response.status, error_msg)
            raise Allow2APIError(f"API error: {error_msg}")

        return data

    async def authenticate(self) -> bool:
        """Test API key by fetching children list.

        Returns:
            True if authentication successful

        Raises:
            Allow2AuthError: Invalid API key
        """
        try:
            await self.get_children()
            return True
        except Allow2AuthError:
            return False

    async def get_children(self) -> list[Dict[str, Any]]:
        """Get list of children for this account.

        Returns:
            List of child dictionaries with id, name, dateOfBirth

        Raises:
            Allow2APIError: API communication error
        """
        response = await self._make_request("GET", "/serviceapi/children")
        children = response.get("children", [])

        _LOGGER.debug("Found %d children", len(children))
        return children

    async def check_quota(
        self,
        user_id: int,
        activity: str,
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check if child has quota remaining for activity.

        Args:
            user_id: Child's Allow2 user ID
            activity: Activity type (e.g., "gaming", "television")
            device_id: Optional device identifier

        Returns:
            Dictionary with quota information:
            {
                "allowed": bool,
                "remaining": int (seconds),
                "reason": str or None,
                "activities": dict,
                "ban": dict or None
            }

        Raises:
            Allow2APIError: API communication error
        """
        request_data = {
            "userId": user_id,
            "activity": activity,
            "tz": self._timezone
        }

        if device_id:
            request_data["deviceId"] = device_id

        _LOGGER.debug(
            "Checking quota for user %s, activity %s, device %s",
            user_id, activity, device_id
        )

        response = await self._make_request(
            "POST",
            "/serviceapi/checkRequest",
            request_data
        )

        # Parse response into simplified format
        allowed = response.get("allowed", False)
        activities = response.get("activities", {})
        activity_data = activities.get(activity, {})
        remaining_seconds = activity_data.get("remaining", 0)
        remaining_minutes = remaining_seconds // 60
        ban = response.get("ban")
        reason = response.get("reason")

        result = {
            "allowed": allowed,
            "remaining_seconds": remaining_seconds,
            "remaining_minutes": remaining_minutes,
            "reason": reason,
            "activities": activities,
            "ban": ban
        }

        _LOGGER.debug(
            "Quota check result: allowed=%s, remaining=%d minutes",
            allowed, remaining_minutes
        )

        return result

    async def log_activity(
        self,
        user_id: int,
        activity: str,
        duration: int,
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log activity usage time.

        Args:
            user_id: Child's Allow2 user ID
            activity: Activity type
            duration: Usage time in seconds
            device_id: Optional device identifier

        Returns:
            Dictionary with logging confirmation and remaining quota

        Raises:
            Allow2APIError: API communication error
        """
        request_data = {
            "userId": user_id,
            "activity": activity,
            "duration": duration,
            "tz": self._timezone
        }

        if device_id:
            request_data["deviceId"] = device_id

        _LOGGER.debug(
            "Logging activity: user %s, activity %s, duration %s seconds",
            user_id, activity, duration
        )

        response = await self._make_request(
            "POST",
            "/serviceapi/logActivity",
            request_data
        )

        _LOGGER.debug("Activity logged successfully")
        return response
```

## Caching Strategy

### Local Cache Implementation

```python
# custom_components/allow2/coordinator.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

_LOGGER = logging.getLogger(__name__)

class QuotaCache:
    """Local cache for quota responses to reduce API calls."""

    def __init__(self, ttl_seconds: int = 300):
        """Initialize cache.

        Args:
            ttl_seconds: Cache time-to-live in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def _cache_key(self, user_id: int, activity: str) -> str:
        """Generate cache key."""
        return f"{user_id}:{activity}"

    def get(self, user_id: int, activity: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached quota data if still valid.

        Args:
            user_id: Child ID
            activity: Activity type

        Returns:
            Cached quota data or None if expired/missing
        """
        key = self._cache_key(user_id, activity)

        if key not in self._cache:
            return None

        cached = self._cache[key]
        timestamp = cached.get("timestamp")

        if not timestamp:
            return None

        age = datetime.now() - timestamp

        if age > self._ttl:
            _LOGGER.debug("Cache expired for %s", key)
            del self._cache[key]
            return None

        _LOGGER.debug("Cache hit for %s (age: %s)", key, age)
        return cached.get("data")

    def set(self, user_id: int, activity: str, data: Dict[str, Any]) -> None:
        """Store quota data in cache.

        Args:
            user_id: Child ID
            activity: Activity type
            data: Quota data to cache
        """
        key = self._cache_key(user_id, activity)

        self._cache[key] = {
            "timestamp": datetime.now(),
            "data": data
        }

        _LOGGER.debug("Cached quota data for %s", key)

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache = {}
        _LOGGER.debug("Cache cleared")

    def clear_child(self, user_id: int) -> None:
        """Clear cache for specific child.

        Args:
            user_id: Child ID
        """
        keys_to_remove = [
            key for key in self._cache.keys()
            if key.startswith(f"{user_id}:")
        ]

        for key in keys_to_remove:
            del self._cache[key]

        _LOGGER.debug("Cleared cache for user %s", user_id)
```

### Cache Usage in Services

```python
# In service handler
async def handle_check_quota(call):
    """Handle check_quota service call."""
    user_id = call.data["child_id"]
    activity = call.data["activity"]
    device_id = call.data.get("device_id")

    # Try cache first
    cached_data = quota_cache.get(user_id, activity)

    if cached_data:
        _LOGGER.debug("Using cached quota data")
        return cached_data

    # Cache miss - call API
    api_client = hass.data[DOMAIN]["api"]
    quota_data = await api_client.check_quota(user_id, activity, device_id)

    # Cache the result
    quota_cache.set(user_id, activity, quota_data)

    return quota_data
```

## Error Handling and Retry Logic

### Retry Strategy

```python
import asyncio
from functools import wraps

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry API calls on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (exponential backoff)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Allow2RateLimitError:
                    # Don't retry rate limits immediately
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt) * 2  # Longer wait for rate limits
                        _LOGGER.warning(
                            "Rate limited, retrying in %s seconds (attempt %s/%s)",
                            wait_time, attempt + 1, max_retries
                        )
                        await asyncio.sleep(wait_time)
                        last_exception = None
                    else:
                        raise
                except Allow2AuthError:
                    # Don't retry auth errors
                    raise
                except Allow2APIError as err:
                    last_exception = err
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        _LOGGER.warning(
                            "API error, retrying in %s seconds (attempt %s/%s): %s",
                            wait_time, attempt + 1, max_retries, err
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        raise

            if last_exception:
                raise last_exception

        return wrapper
    return decorator

# Usage
class Allow2API:
    @retry_on_error(max_retries=3, delay=1.0)
    async def check_quota(self, user_id: int, activity: str, device_id: Optional[str] = None):
        # ... implementation
        pass
```

### Graceful Degradation

```python
async def check_quota_with_fallback(
    api_client: Allow2API,
    cache: QuotaCache,
    user_id: int,
    activity: str,
    device_id: Optional[str] = None
) -> Dict[str, Any]:
    """Check quota with fallback to cached data on API failure.

    This implements a "fail-open" strategy - if the API is unavailable,
    we use cached data to avoid blocking the child unnecessarily.
    """
    try:
        # Try API call
        quota_data = await api_client.check_quota(user_id, activity, device_id)

        # Cache successful response
        cache.set(user_id, activity, quota_data)

        return quota_data

    except Allow2APIError as err:
        _LOGGER.warning("API call failed, attempting to use cached data: %s", err)

        # Try to use cached data (even if expired)
        cached_data = cache.get(user_id, activity)

        if cached_data:
            _LOGGER.info("Using cached quota data as fallback")
            # Mark as cached for transparency
            cached_data["_from_cache"] = True
            cached_data["_cache_age"] = "expired"
            return cached_data

        # No cache available - fail open (allow usage)
        _LOGGER.error(
            "No cached data available and API failed. Defaulting to 'allowed' for user experience."
        )
        return {
            "allowed": True,  # Fail-open: allow usage
            "remaining_seconds": 3600,  # Show reasonable default
            "remaining_minutes": 60,
            "reason": "API unavailable - using default allowance",
            "activities": {},
            "ban": None,
            "_error": True,
            "_error_message": str(err)
        }
```

## Rate Limiting

### Client-Side Rate Limiting

```python
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """Client-side rate limiter to avoid hitting API limits."""

    def __init__(self, max_calls: int = 60, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum calls per window
            window_seconds: Time window in seconds
        """
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
                _LOGGER.debug("Rate limit reached, waiting %s seconds", wait_seconds)
                await asyncio.sleep(wait_seconds)

        # Record this call
        self._calls.append(now)
```

## Testing

### Mock API for Testing

```python
# tests/test_api.py

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from custom_components.allow2.api import Allow2API, Allow2AuthError

@pytest.fixture
async def api_client():
    """Create API client for testing."""
    async with ClientSession() as session:
        yield Allow2API("test_api_key", session)

@pytest.mark.asyncio
async def test_check_quota_allowed(api_client):
    """Test successful quota check."""
    with aioresponses() as m:
        m.post(
            "https://api.allow2.com/serviceapi/checkRequest",
            payload={
                "allowed": True,
                "activities": {
                    "gaming": {
                        "remaining": 7200
                    }
                }
            }
        )

        result = await api_client.check_quota(12345, "gaming")

        assert result["allowed"] is True
        assert result["remaining_seconds"] == 7200
        assert result["remaining_minutes"] == 120

@pytest.mark.asyncio
async def test_check_quota_exhausted(api_client):
    """Test quota exhausted response."""
    with aioresponses() as m:
        m.post(
            "https://api.allow2.com/serviceapi/checkRequest",
            payload={
                "allowed": False,
                "activities": {
                    "gaming": {
                        "remaining": 0
                    }
                },
                "reason": "daily quota exhausted"
            }
        )

        result = await api_client.check_quota(12345, "gaming")

        assert result["allowed"] is False
        assert result["remaining_seconds"] == 0
        assert result["reason"] == "daily quota exhausted"

@pytest.mark.asyncio
async def test_invalid_api_key(api_client):
    """Test authentication error handling."""
    with aioresponses() as m:
        m.post(
            "https://api.allow2.com/serviceapi/checkRequest",
            status=401,
            payload={
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid API key"
                }
            }
        )

        with pytest.raises(Allow2AuthError):
            await api_client.check_quota(12345, "gaming")
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

### 8. Batch When Possible
Future: Implement batch quota checking for multiple children/activities.

## Comparison with allow2nodered

This implementation closely follows allow2nodered's approach:

| Aspect | allow2nodered | allow2homeassistant |
|--------|---------------|---------------------|
| **Language** | JavaScript | Python |
| **HTTP Client** | axios | aiohttp |
| **Caching** | In-memory | QuotaCache class |
| **Error Handling** | try/catch | async/await + exceptions |
| **Retry Logic** | Built-in | Custom decorator |
| **Rate Limiting** | None | RateLimiter class |
| **Config** | Node properties | Config flow |

**Key Similarities**:
- Same API endpoints
- Same request/response format
- Similar caching strategy
- Same fail-open philosophy

## Next Steps

For implementation examples, see:
- [Use Cases](USE_CASES.md) - Real-world automation examples
- [Configuration](CONFIGURATION.md) - Service configuration
- [Architecture](ARCHITECTURE.md) - System design

For Allow2 API documentation, visit https://developer.allow2.com
