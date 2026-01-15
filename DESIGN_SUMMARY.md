# allow2homeassistant - Design Summary

## Executive Summary

**allow2homeassistant** is a native Home Assistant custom integration that provides parental controls using the Allow2 API. It runs entirely within Home Assistant and is the **inverse** of the existing `allow2automate-homeassistant` plugin.

**Integration Domain**: `allow2`
**Display Name**: "Allow2"
**Repository**: `allow2/homeassistant` (recommended)
**HACS Name**: "Allow2 Parental Controls"

## Key Differentiators

### allow2homeassistant vs. allow2automate-homeassistant

| Feature | allow2automate-homeassistant | allow2homeassistant |
|---------|------------------------------|---------------------|
| **Architecture** | External agent → HA | Native HA integration |
| **Runs On** | Parent's computer/server | Inside Home Assistant |
| **Installation** | Requires allow2automate app | HACS or manual install |
| **Configuration** | Parent app GUI | Home Assistant UI |
| **Device Control** | WebSocket/REST API | Native HA service calls |
| **Dependencies** | allow2automate + agent | Self-contained |
| **Use Case** | Multi-platform control | HA-only environments |
| **Best For** | Parents managing multiple device types | Tech-savvy HA users |

## Design Philosophy

**Inspired by allow2nodered**: This integration follows the same architectural patterns as the allow2nodered Node-RED package, adapted for Home Assistant's Python environment.

### Core Principles

1. **Native Integration**: Uses Home Assistant's official integration framework
2. **Direct API Communication**: Calls Allow2 cloud API without intermediaries
3. **Self-Contained**: No external dependencies or agents required
4. **Automation-Driven**: Enforces controls via HA automations (not standalone service)
5. **Flexible**: Works with any HA entity (media players, switches, smart plugs)

## Architecture

### System Components

```
Home Assistant
├── allow2homeassistant Integration
│   ├── Config Flow (UI setup)
│   ├── Allow2 API Client (Python)
│   ├── Data Coordinator (caching)
│   ├── Services (check_quota, log_activity)
│   └── Local Cache (quota data)
├── User Automations
│   ├── Monitor device state
│   ├── Call allow2.check_quota
│   └── Enforce limits (turn off devices)
└── Device Integrations
    ├── media_player.xbox
    ├── switch.computer_plug
    └── media_player.tv

           ↓ HTTPS
    Allow2 Cloud API
    (Quota checking, usage logging)
```

### Data Flow

1. **Device Usage Detected** → HA automation triggers
2. **Quota Check** → Integration calls Allow2 API
3. **Response Cached** → Local cache updated (5-minute TTL)
4. **Decision Made** → Automation evaluates quota status
5. **Action Taken** → Device turned off if quota exhausted

## Key Features

### Services Provided

#### `allow2.check_quota`
- Checks if child has quota remaining
- Returns allowed/denied status
- Includes remaining time in minutes/seconds
- Provides reason if denied (quota exhausted, ban window, etc.)
- Automatically logs usage time

#### `allow2.log_activity`
- Manually logs usage time (rarely needed)
- Records activity to Allow2 cloud
- Updates quota balances

### Benefits

**For Parents**:
- Automated enforcement of screen time limits
- No additional software to maintain
- Native HA integration and automations
- Flexible device control

**For Tech-Savvy Users**:
- Deep integration with HA automation engine
- Customizable enforcement logic
- Works with any HA-controllable device
- Open source and extensible

## Technical Implementation

### Language & Libraries
- **Python 3.11+** (Home Assistant requirement)
- **aiohttp** (async HTTP client)
- **Home Assistant Integration API** (config flow, services, coordinators)

### API Communication
- **Base URL**: `https://api.allow2.com`
- **Authentication**: Bearer token (API key)
- **Endpoints**:
  - `POST /serviceapi/checkRequest` (quota checking)
  - `POST /serviceapi/logActivity` (usage logging)
  - `GET /serviceapi/children` (child list)

### Caching Strategy
- **Local in-memory cache** (5-minute TTL by default)
- **Fail-open behavior** (allow usage if API unavailable)
- **Reduces API calls by 80-90%**
- **Graceful degradation** on network issues

### Error Handling
- **Retry logic** with exponential backoff
- **Rate limiting** to respect API limits
- **Fallback to cached data** on failures
- **Detailed logging** for troubleshooting

## Use Cases

### Primary Scenarios

1. **Gaming Console Control** (Xbox, PlayStation)
2. **TV/Media Center Limits** (Kodi, Plex, smart TVs)
3. **Computer Access** (via smart plugs)
4. **Internet Control** (router/AP management)
5. **Bedtime Enforcement** (turn off all devices)
6. **Homework Protection** (block during study hours)
7. **Multi-Child Management** (shared devices)

### Example Automation Pattern

```yaml
automation:
  - trigger:
      platform: time_pattern
      minutes: "/5"  # Check every 5 minutes
    condition:
      - condition: state
        entity_id: media_player.xbox
        state: "playing"
    action:
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "gaming"
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

## Installation Options

### HACS (Recommended)
1. Add custom repository to HACS
2. Install "Allow2 Parental Controls"
3. Restart Home Assistant
4. Add integration via UI

### Manual
1. Copy `custom_components/allow2/` to HA config
2. Restart Home Assistant
3. Add integration via UI

## Configuration

### UI-Based Setup
- **API Key**: From Allow2 web portal
- **Update Interval**: How often to refresh child data (default: 30 min)
- **Cache Duration**: Local cache TTL (default: 5 min)

### YAML Configuration (Advanced)
```yaml
allow2:
  cache_duration: 300  # seconds
  update_interval: 1800  # seconds
  fail_open: true  # Allow usage if API fails
```

## Documentation Structure

### Created Documents

1. **README.md** (4.2 KB)
   - Quick overview and comparison table
   - When to use each integration
   - Quick start example

2. **OVERVIEW.md** (7.0 KB)
   - Detailed purpose and use cases
   - Target audience
   - How it works

3. **ARCHITECTURE.md** (15 KB)
   - System architecture diagrams
   - Component descriptions
   - Data flow explanations
   - Code structure guidelines

4. **INSTALLATION.md** (11 KB)
   - HACS installation steps
   - Manual installation guide
   - Configuration walkthrough
   - Troubleshooting common issues

5. **CONFIGURATION.md** (18 KB)
   - API key setup
   - Service usage details
   - Child and device mapping
   - Automation patterns
   - Advanced YAML configuration

6. **USE_CASES.md** (45 KB)
   - 10 real-world scenarios
   - Complete copy-paste automations
   - Multi-child management examples
   - Progressive warnings patterns

7. **API_INTEGRATION.md** (25 KB)
   - Allow2 API endpoint documentation
   - Python implementation details
   - Caching and retry strategies
   - Error handling patterns
   - Testing examples

**Total Documentation**: ~125 KB, 7 comprehensive files

## Comparison with Inspirations

### Based on allow2nodered

| Aspect | allow2nodered | allow2homeassistant |
|--------|---------------|---------------------|
| Platform | Node-RED | Home Assistant |
| Language | JavaScript | Python |
| HTTP Client | axios | aiohttp |
| Configuration | Node properties | Config flow UI |
| Flow Control | Node-RED flows | HA automations |
| API Endpoints | Same | Same |
| Caching Strategy | Similar | Enhanced |

### Different from allow2automate-homeassistant

**allow2automate-homeassistant** is designed for parents who want:
- Simple GUI configuration
- Multi-platform control (HA + Windows + macOS + phones)
- Centralized management outside HA
- No need to write automations

**allow2homeassistant** is designed for users who want:
- Native HA integration
- HA-only device control
- Deeper automation capabilities
- No external software dependencies

## Development Roadmap

### Phase 1: Core Integration (v1.0)
- [x] Design documentation
- [ ] Config flow implementation
- [ ] API client
- [ ] Services (check_quota, log_activity)
- [ ] Data coordinator
- [ ] Local caching
- [ ] Error handling and retry logic

### Phase 2: Enhanced Features (v1.1)
- [ ] Sensors (quota remaining, status)
- [ ] Binary sensors (quota_available)
- [ ] Events (quota_exhausted, quota_warning)
- [ ] Lovelace card for quota visualization

### Phase 3: Advanced Features (v1.2)
- [ ] Blueprint library
- [ ] Voice assistant integration
- [ ] Multiple API key support (multi-parent households)
- [ ] Offline mode with extended caching

## Security Considerations

### Data Privacy
- **Child IDs only** (no personal information sent to Allow2)
- **Activity types and durations** (generic, not content-specific)
- **Device identifiers** (generic names like "xbox")

### API Security
- **HTTPS only** for all communication
- **API key stored encrypted** in HA config
- **No credentials in logs**
- **Rate limiting** to prevent abuse

### Access Control
- **Admin privileges required** for config
- **HA authentication** required for service calls
- **Parent notifications** for enforcement events

## Target Audience

### Perfect For
- Tech-savvy parents comfortable with Home Assistant
- Users with HA-controlled entertainment devices
- Households wanting self-hosted parental controls
- Developers wanting to extend/customize

### NOT Recommended For
- Parents unfamiliar with Home Assistant automations
- Users needing to control non-HA devices (laptops, phones)
- Those wanting simple GUI without YAML
- Multi-platform control needs → use **allow2automate** instead

## Success Metrics

### Expected Outcomes
- **10-20 API calls/hour** per child (well below rate limits)
- **80-90% cache hit rate** (most checks use cached data)
- **<100ms latency** for cached quota checks
- **<2s latency** for API calls
- **<60KB memory** footprint per child

### User Benefits
- **Automated enforcement** (no manual intervention)
- **Consistent rules** (apply even when parents away)
- **Transparency** (children see remaining time)
- **Flexibility** (adjust limits remotely via Allow2 app)

## Next Steps

### For Developers
1. **Review architecture**: See ARCHITECTURE.md
2. **Implement core components**: API client, config flow, services
3. **Write tests**: Unit tests for all components
4. **Create example automations**: Blueprints for common scenarios

### For Users
1. **Install integration**: Via HACS or manual
2. **Configure API key**: From Allow2 web portal
3. **Create automations**: Using examples from USE_CASES.md
4. **Test thoroughly**: Verify quota checking and enforcement

### For Contributors
1. **Read documentation**: All 7 design docs
2. **Follow HA guidelines**: Official integration standards
3. **Submit PRs**: With tests and documentation
4. **Join community**: Home Assistant forums

## Conclusion

**allow2homeassistant** fills a specific niche: native Home Assistant parental controls for users who want deep integration without external dependencies. It complements (doesn't replace) allow2automate-homeassistant, offering a different approach for different use cases.

By following the proven patterns from allow2nodered and adapting them to Home Assistant's ecosystem, this integration provides a robust, flexible, and user-friendly solution for HA-centric households.

---

**Documentation Created**: 2026-01-15
**Total Documentation Size**: ~125 KB (7 files)
**Implementation Status**: Design complete, ready for development
**License**: MIT (expected)
**Repository**: https://github.com/allow2/allow2homeassistant (planned)
