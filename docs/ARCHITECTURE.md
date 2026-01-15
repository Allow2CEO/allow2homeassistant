# Allow2 Home Assistant Integration - Architecture

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Home Assistant                         │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │         allow2homeassistant Integration        │   │
│  │                                                 │   │
│  │  ┌──────────────┐      ┌──────────────────┐  │   │
│  │  │  Config Flow │      │  Allow2 API      │  │   │
│  │  │  (UI Setup)  │      │  Client          │  │   │
│  │  └──────────────┘      └──────────────────┘  │   │
│  │                                                 │   │
│  │  ┌──────────────┐      ┌──────────────────┐  │   │
│  │  │  Services    │      │  Coordinator     │  │   │
│  │  │  - check_quota│      │  (Data Updates) │  │   │
│  │  │  - log_activity│     └──────────────────┘  │   │
│  │  └──────────────┘                              │   │
│  │                                                 │   │
│  │  ┌──────────────┐      ┌──────────────────┐  │   │
│  │  │  Sensors     │      │  Local Cache     │  │   │
│  │  │  (Optional)  │      │  (Quota Data)    │  │   │
│  │  └──────────────┘      └──────────────────┘  │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │         Home Assistant Automations             │   │
│  │  - Monitor device state                        │   │
│  │  - Call allow2.check_quota service            │   │
│  │  - Enforce limits (turn off devices)          │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │         Device Integrations                    │   │
│  │  - media_player.xbox                          │   │
│  │  - switch.computer_plug                       │   │
│  │  - media_player.living_room_tv               │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS
                          ↓
                ┌──────────────────┐
                │   Allow2 Cloud   │
                │   API Service    │
                │                  │
                │  - Authenticate  │
                │  - Check Quota   │
                │  - Log Usage     │
                │  - Get Status    │
                └──────────────────┘
```

## Core Components

### 1. Integration Entry Point

**File**: `custom_components/allow2/__init__.py`

**Responsibilities**:
- Register the integration with Home Assistant
- Set up config entry
- Initialize API client
- Register services
- Set up data coordinator

**Key Functions**:
```python
async def async_setup_entry(hass, entry):
    """Set up Allow2 from a config entry."""
    # Initialize API client with credentials
    # Set up data update coordinator
    # Register services
    # Store data in hass.data
```

### 2. Config Flow

**File**: `custom_components/allow2/config_flow.py`

**Responsibilities**:
- UI-based configuration
- Validate Allow2 API credentials
- Test connection to Allow2 API
- Handle reconfiguration

**User Input**:
- API Key (from Allow2 parent account)
- Optional: Update interval
- Optional: Cache duration
- Optional: Default device names

**Flow**:
```
User installs integration
  ↓
Config Flow UI appears
  ↓
User enters API key
  ↓
Integration validates with Allow2 API
  ↓
Success: Integration configured
  ↓
Services available for use
```

### 3. Allow2 API Client

**File**: `custom_components/allow2/api.py`

**Responsibilities**:
- Communication with Allow2 cloud API
- Authentication
- Quota checking
- Usage logging
- Error handling and retries

**Key Methods**:
```python
class Allow2API:
    async def authenticate(self):
        """Authenticate with Allow2 API using API key."""

    async def check_quota(self, child_id, activity, device_id):
        """Check if child has quota remaining for activity."""

    async def log_activity(self, child_id, activity, device_id, duration):
        """Log usage time to Allow2."""

    async def get_children(self):
        """Get list of children for this account."""
```

**API Endpoints** (based on allow2nodered):
- `POST /serviceapi/checkRequest` - Check quota and get status
- `POST /serviceapi/logActivity` - Record usage time

### 4. Data Update Coordinator

**File**: `custom_components/allow2/coordinator.py`

**Responsibilities**:
- Periodic quota updates
- Local caching
- Throttling API calls
- Data freshness management

**Behavior**:
- Fetches child list periodically (every 30 minutes)
- Caches quota responses (configurable duration)
- Handles API rate limiting
- Provides fallback data on API errors

### 5. Services

**File**: `custom_components/allow2/services.py`

**Services Provided**:

#### `allow2.check_quota`
Check if child has quota remaining for activity.

**Input**:
```yaml
service: allow2.check_quota
data:
  child_id: 12345
  activity: "gaming"  # or "internet", "television", etc.
  device_id: "xbox"   # Optional identifier
```

**Output** (response_variable):
```yaml
{
  "allowed": true,
  "remaining_minutes": 45,
  "reason": null,  # Or "daily quota exhausted", "ban window active", etc.
  "activities": {
    "gaming": {
      "remaining": 2700  # seconds
    }
  }
}
```

#### `allow2.log_activity`
Manually log activity time (usually automatic).

**Input**:
```yaml
service: allow2.log_activity
data:
  child_id: 12345
  activity: "gaming"
  device_id: "xbox"
  duration: 300  # seconds
```

### 6. Sensors (Optional Future Feature)

**File**: `custom_components/allow2/sensor.py`

**Potential Sensors**:
- `sensor.johnny_gaming_remaining` - Minutes remaining for gaming
- `sensor.johnny_total_screen_time` - Total screen time today
- `sensor.johnny_quota_status` - "allowed", "exhausted", "banned"

**Benefits**:
- Dashboard visualization
- Conditional automation triggers
- Lovelace card integration

### 7. Local Cache

**Implementation**:
- Use Home Assistant's data store
- Cache quota responses per child
- Configurable TTL (Time To Live)
- Fallback when API unavailable

**Cache Structure**:
```python
{
    "child_12345": {
        "quota_data": {
            "allowed": true,
            "remaining_minutes": 45,
            "activities": {...}
        },
        "timestamp": 1234567890,
        "ttl": 300  # 5 minutes
    }
}
```

## Data Flow

### Quota Check Flow

```
1. Automation triggers
   ↓
2. Call allow2.check_quota service
   ↓
3. Service checks local cache
   ├─ Cache valid? Use cached data
   │   ↓
   │   Return cached response
   │
   └─ Cache expired/missing?
       ↓
       Call Allow2 API
       ↓
       API responds with quota data
       ↓
       Cache response locally
       ↓
       Return to automation
       ↓
4. Automation evaluates response
   ├─ Allowed: Continue
   └─ Not allowed: Turn off device
```

### Activity Logging Flow

```
1. Device state change detected
   ↓
2. Automation calculates usage time
   ↓
3. Call allow2.log_activity service
   ↓
4. Service calls Allow2 API
   ↓
5. API records usage
   ↓
6. Local cache updated
   ↓
7. Success response returned
```

## Integration with Home Assistant

### Automation Integration

Automations use the integration services:

```yaml
automation:
  - alias: "Check Xbox Quota"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    condition:
      - condition: state
        entity_id: media_player.xbox
        state: "playing"
    action:
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "gaming"
          device_id: "xbox"
        response_variable: quota
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox
```

### Script Integration

Scripts can also use the services:

```yaml
script:
  check_and_enforce_quota:
    sequence:
      - service: allow2.check_quota
        data:
          child_id: "{{ child_id }}"
          activity: "{{ activity_type }}"
          device_id: "{{ device_id }}"
        response_variable: quota_result
      - condition: template
        value_template: "{{ not quota_result.allowed }}"
      - service: homeassistant.turn_off
        target:
          entity_id: "{{ entity_id }}"
```

## Error Handling

### API Failures

**Strategy**: Graceful degradation
- Use cached data when API unavailable
- Log errors but don't break automations
- Retry with exponential backoff
- Notify parent of persistent failures

**Failure Modes**:
1. **Network error**: Use cache, retry later
2. **Invalid credentials**: Notify parent, disable integration
3. **Rate limiting**: Queue requests, spread over time
4. **Service downtime**: Use cache, log for parent

### Invalid Responses

**Validation**:
- Check response structure
- Validate data types
- Handle missing fields
- Default to "allowed" on ambiguous errors (fail-open for user experience)

## Security Considerations

### API Key Storage
- Stored in Home Assistant's config entry (encrypted)
- Never logged or exposed in UI
- Separate from Home Assistant authentication

### Communication
- All API calls over HTTPS
- API key in header (not URL)
- No sensitive child data transmitted

### Access Control
- Services require Home Assistant authentication
- Config flow requires admin privileges
- API key can't be read through services

## Performance Considerations

### API Call Optimization

**Strategies**:
1. **Local Caching**: Reduce API calls by 80-90%
2. **Batch Requests**: Combine multiple checks (future feature)
3. **Async Operations**: Non-blocking API calls
4. **Smart Polling**: Only check when device in use

**Expected Load**:
- Typical family: 10-20 API calls/hour
- Heavy usage: 100-200 API calls/hour
- Well within Allow2 rate limits

### Memory Footprint

**Estimated Usage**:
- Integration code: ~50 KB
- Cached data per child: ~2 KB
- Total for 3 children: ~60 KB
- Negligible impact on Home Assistant

## Extensibility

### Future Components

**Planned**:
- **Sensors**: Expose quota data as entities
- **Lovelace Cards**: Custom UI cards
- **Blueprints**: Pre-built automation templates
- **Events**: Fire events for quota changes

**Possible**:
- **Binary Sensors**: "quota_available" on/off sensor
- **Notifications**: Built-in notification system
- **Dashboard**: Parent control panel in HA
- **Voice Integration**: Alexa/Google Assistant support

## Comparison with allow2nodered

This integration is inspired by allow2nodered's design:

| Aspect | allow2nodered | allow2homeassistant |
|--------|---------------|---------------------|
| **Platform** | Node-RED | Home Assistant |
| **Language** | JavaScript | Python |
| **Configuration** | Node properties | Config flow UI |
| **API Client** | Axios HTTP | aiohttp async |
| **Caching** | In-memory | HA data store |
| **Services** | Node outputs | HA services |
| **Flow Control** | Node-RED flows | HA automations |

**Shared Concepts**:
- Same Allow2 API endpoints
- Similar quota check logic
- Comparable activity logging
- Cache strategy

## Development Guidelines

### Code Structure
```
custom_components/allow2/
├── __init__.py          # Integration entry point
├── manifest.json        # Integration metadata
├── config_flow.py       # Configuration UI
├── const.py             # Constants
├── api.py               # Allow2 API client
├── coordinator.py       # Data update coordinator
├── services.py          # Service definitions
├── sensor.py            # Sensor platform (future)
├── strings.json         # UI strings
└── translations/
    └── en.json          # English translations
```

### Code Standards
- **Python 3.11+**: Modern Python features
- **async/await**: Non-blocking operations
- **Type Hints**: Full type annotations
- **Testing**: Unit tests for all components
- **Documentation**: Docstrings for all classes/methods
- **Home Assistant Guidelines**: Follow official HA integration standards

### Dependencies
```python
# manifest.json
{
  "domain": "allow2",
  "name": "Allow2 Parental Controls",
  "requirements": [
    "aiohttp>=3.8.0"  # Async HTTP client
  ],
  "dependencies": [],
  "codeowners": ["@author"],
  "config_flow": true,
  "iot_class": "cloud_polling",
  "version": "1.0.0"
}
```

## Next Steps

For implementation details, see:
- [Installation Guide](INSTALLATION.md) - How to install the integration
- [Configuration Guide](CONFIGURATION.md) - Setup and configuration
- [API Integration](API_INTEGRATION.md) - Allow2 API communication details
