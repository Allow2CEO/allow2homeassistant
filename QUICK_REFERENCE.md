# allow2homeassistant - Quick Reference

## One-Page Overview

### What Is It?

A **native Home Assistant custom integration** that provides parental controls using the Allow2 API. Runs entirely within Home Assistant - no external dependencies.

### When to Use?

✅ **Use allow2homeassistant if:**
- You ONLY need to control Home Assistant devices
- You're comfortable writing HA automations
- You prefer self-contained, native integrations
- You want deeper HA automation capabilities

❌ **Use allow2automate-homeassistant instead if:**
- You need to control multiple platforms (HA + PCs + phones)
- You prefer GUI configuration over YAML
- You want centralized management outside HA
- You're less technical and want simpler setup

---

## Quick Setup (5 Minutes)

### 1. Get Allow2 API Key
```
1. Visit https://allow2.com
2. Login → Settings → API Access
3. Generate New API Key
4. Copy: ak_xxxxxxxxxxxx
```

### 2. Install Integration
```
HACS:
  Integrations → ⋮ → Custom repositories
  → https://github.com/allow2/allow2homeassistant
  → Download → Restart HA

Manual:
  Copy custom_components/allow2/ to /config/
  → Restart HA
```

### 3. Add Integration
```
Settings → Devices & Services → Add Integration
→ Search "Allow2" → Enter API Key → Done
```

### 4. Find Child IDs
```
Settings → System → Logs → Search "allow2"
→ Look for: "Found children: ID: 12345, Name: Johnny"
```

---

## Basic Automation Template

```yaml
automation:
  - alias: "Enforce [Device] Quota for [Child]"
    trigger:
      - platform: time_pattern
        minutes: "/5"  # Check every 5 minutes

    condition:
      - condition: state
        entity_id: media_player.xbox  # Your device
        state: "playing"  # Active state

    action:
      # Check quota
      - service: allow2.check_quota
        data:
          child_id: 12345  # Your child's ID
          activity: "gaming"  # Activity type
          device_id: "xbox"  # Device name
        response_variable: quota

      # Warn at 15 minutes
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ quota.allowed and quota.remaining_minutes <= 15 }}"
            sequence:
              - service: notify.mobile_app_phone
                data:
                  message: "Warning: {{ quota.remaining_minutes }} minutes left!"

      # Turn off when quota exhausted
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox
              - service: notify.mobile_app_phone
                data:
                  message: "Time's up! Xbox turned off."
```

---

## Services Reference

### allow2.check_quota

**Check if child has quota remaining**

```yaml
service: allow2.check_quota
data:
  child_id: 12345           # Required: Child's Allow2 ID
  activity: "gaming"        # Required: Activity type
  device_id: "xbox"         # Optional: Device identifier
response_variable: quota    # Store response
```

**Response:**
```yaml
quota:
  allowed: true             # or false
  remaining_minutes: 45     # Minutes left
  remaining_seconds: 2700   # Seconds left
  reason: null              # Or "daily quota exhausted", etc.
  activities:
    gaming:
      remaining: 2700       # Seconds
```

**Activity Types:**
- `"gaming"` - Video games
- `"internet"` - General computer/internet
- `"television"` - TV watching
- `"social"` - Social media
- `"school"` - Educational
- `"custom"` - Your custom activities

### allow2.log_activity

**Manually log usage time (rarely needed)**

```yaml
service: allow2.log_activity
data:
  child_id: 12345
  activity: "gaming"
  device_id: "xbox"
  duration: 300  # Seconds
```

**Note:** `check_quota` automatically logs usage, so manual logging is usually unnecessary.

---

## Common Device Patterns

### Gaming Console (Xbox, PlayStation)
```yaml
entity_id: media_player.xbox
state: "playing"
activity: "gaming"
```

### Smart TV
```yaml
entity_id: media_player.living_room_tv
state: "on"
activity: "television"
```

### Computer via Smart Plug
```yaml
entity_id: switch.computer_plug
state: "on"
activity: "internet"
```

### Streaming Device
```yaml
entity_id: media_player.chromecast
state: "playing"
activity: "television"
```

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Integration not found** | Check files in `/config/custom_components/allow2/`, restart HA |
| **Invalid API key** | Verify key in Allow2 portal, regenerate if needed |
| **Quota always "allowed"** | Check child_id correct, activity matches Allow2 config (lowercase) |
| **Device won't turn off** | Test `turn_off` service manually in Developer Tools |
| **No children found** | Verify children exist in Allow2 portal, check API key permissions |

**Enable Debug Logging:**
```yaml
# configuration.yaml
logger:
  logs:
    custom_components.allow2: debug
```

---

## Configuration Examples

### Multi-Child Device Selector
```yaml
input_select:
  xbox_user:
    name: Xbox Current User
    options:
      - "Not in use"
      - "Johnny (12345)"
      - "Sarah (67890)"
    initial: "Not in use"
```

### Progressive Warnings
```yaml
# 30-minute warning
- condition: template
  value_template: "{{ quota.remaining_minutes <= 30 }}"
- service: notify.mobile_app
  data:
    message: "30 minutes left"

# 15-minute warning
- condition: template
  value_template: "{{ quota.remaining_minutes <= 15 }}"
- service: notify.mobile_app
  data:
    message: "15 minutes left!"

# 5-minute URGENT warning
- condition: template
  value_template: "{{ quota.remaining_minutes <= 5 }}"
- service: notify.mobile_app
  data:
    message: "URGENT: 5 minutes! Save your game!"
    data:
      priority: high
```

### Bedtime Enforcement
```yaml
automation:
  - alias: "Bedtime - All Devices Off"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: homeassistant.turn_off
        target:
          entity_id:
            - media_player.xbox
            - media_player.tv
            - switch.computer_plug
      - service: notify.mobile_app_kids
        data:
          message: "Bedtime! All devices off. Good night!"
```

### Homework Time Block
```yaml
automation:
  - alias: "Block Devices During Homework"
    trigger:
      - platform: state
        entity_id: media_player.xbox
        to: "on"
    condition:
      - condition: time
        after: "16:00:00"
        before: "18:00:00"
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: homeassistant.turn_off
        target:
          entity_id: media_player.xbox
      - service: notify.mobile_app
        data:
          message: "Homework time! Xbox blocked until 6pm."
```

---

## File Structure

```
custom_components/allow2/
├── __init__.py          # Integration entry
├── manifest.json        # Metadata
├── config_flow.py       # UI configuration
├── const.py             # Constants
├── api.py               # Allow2 API client
├── coordinator.py       # Data coordinator
├── services.py          # Service handlers
├── strings.json         # UI strings
└── translations/
    └── en.json          # English translations
```

---

## Documentation Index

| Document | Lines | Purpose |
|----------|-------|---------|
| **README.md** | 104 | Quick overview, comparison table |
| **OVERVIEW.md** | 210 | Detailed purpose, target audience |
| **ARCHITECTURE.md** | 491 | Technical design, components |
| **INSTALLATION.md** | 440 | Step-by-step installation |
| **CONFIGURATION.md** | 693 | Service config, automations |
| **USE_CASES.md** | 1573 | 10 real-world examples |
| **API_INTEGRATION.md** | 920 | API details, Python code |
| **DESIGN_SUMMARY.md** | 370 | Executive summary |
| **QUICK_REFERENCE.md** | This file | One-page cheat sheet |

**Total:** 4,801 lines of documentation

---

## Key Differences vs. allow2automate-homeassistant

```
allow2automate-homeassistant:
┌──────────────────────────┐
│  Parent's Computer       │
│  ┌────────────────────┐  │
│  │ allow2automate App│  │
│  └────────────────────┘  │
│           ↓              │
│  ┌────────────────────┐  │
│  │ HA Plugin (Agent) │  │
│  └────────────────────┘  │
└──────────────────────────┘
           ↓ WebSocket/REST
┌──────────────────────────┐
│  Home Assistant          │
│  - Devices controlled    │
└──────────────────────────┘

allow2homeassistant:
┌──────────────────────────┐
│  Home Assistant          │
│  ┌────────────────────┐  │
│  │ allow2 Integration│  │
│  │ (Native)          │  │
│  └────────────────────┘  │
│           ↓              │
│  ┌────────────────────┐  │
│  │ HA Automations    │  │
│  └────────────────────┘  │
│           ↓              │
│  - Devices controlled    │
└──────────────────────────┘
           ↓ HTTPS
     Allow2 Cloud API
```

---

## Performance Expectations

- **API Calls**: 10-20/hour per child (with caching)
- **Cache Hit Rate**: 80-90% (most checks cached)
- **Latency**: <100ms (cached), <2s (API)
- **Memory**: <60KB per child
- **CPU**: Negligible impact

---

## Support Resources

- **GitHub**: https://github.com/allow2/allow2homeassistant
- **HA Forums**: Home Assistant community forums
- **Allow2 Support**: https://allow2.com/support
- **Documentation**: /plugins/allow2homeassistant/docs/

---

## License

MIT License (expected)

---

## Quick Start Checklist

- [ ] Allow2 account created
- [ ] API key generated
- [ ] Child profiles configured in Allow2
- [ ] Quotas set in Allow2 portal
- [ ] Integration installed in HA
- [ ] API key configured via config flow
- [ ] Child IDs identified from logs
- [ ] Test automation created
- [ ] `check_quota` service tested
- [ ] Device control verified
- [ ] Notifications configured
- [ ] Production automations deployed

---

**Last Updated**: 2026-01-15
**Version**: Design Phase (v1.0 pending)
