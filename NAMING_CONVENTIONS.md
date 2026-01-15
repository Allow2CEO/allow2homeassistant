# Home Assistant Integration Naming Conventions

This document defines the official naming conventions for the **allow2homeassistant** integration, following Home Assistant and HACS best practices.

---

## Overview

Based on [Home Assistant Developer Documentation](https://developers.home-assistant.io/docs/creating_integration_manifest/) and HACS community standards, here are the naming conventions used throughout this integration.

---

## 1. Integration Domain (Technical Identifier)

**Value:** `allow2`

### Rules
- ✅ Must use `lowercase_with_underscores`
- ✅ Must be unique across all Home Assistant integrations
- ✅ Cannot be changed after creation
- ✅ Can use letters, numbers, and underscores only
- ❌ Cannot start or end with underscore
- ✅ Must match the directory name under `custom_components/`

### Examples in Use
```python
# Service calls
service: allow2.check_quota
service: allow2.log_activity

# Entity IDs
sensor.allow2_bobby_gaming_remaining
sensor.allow2_sarah_internet_quota
binary_sensor.allow2_johnny_banned

# Config directory
config/custom_components/allow2/
```

### Why "allow2"?
- Short and simple (best practice)
- Matches the brand name exactly
- Easy to remember and type
- Follows pattern of other integrations (e.g., `hue`, `nest`, `ring`)

---

## 2. Integration Name (User-Facing Display)

**Value:** `"Allow2"`

### Rules
- Defined in `manifest.json` as `"name": "Allow2"`
- Can use mixed case, spaces, special characters
- Shows in Home Assistant UI
- Should match brand presentation

### Examples in Use
```json
{
  "domain": "allow2",
  "name": "Allow2",
  "documentation": "https://github.com/allow2/homeassistant",
  "version": "1.0.0"
}
```

### UI Display
- Configuration panel title: "Allow2"
- Integration card: "Allow2"
- Settings: "Allow2 Configuration"

---

## 3. GitHub Repository Name

**Value:** `allow2/homeassistant`

### Conventions
- Typically use `lowercase-with-hyphens` for readability
- Often include prefix: `hacs-`, `ha-`, or `hass-`
- Must be public
- Should be descriptive

### Options Considered

| Repository Name | Pros | Cons | Recommendation |
|-----------------|------|------|----------------|
| `allow2/homeassistant` | ✅ Clean, under org<br>✅ Clear purpose | ⚠️ Requires GitHub org | **Recommended** if under Allow2 org |
| `allow2-homeassistant` | ✅ Follows community pattern<br>✅ Descriptive | ⚠️ Hyphen convention | **Recommended** alternative |
| `hacs-allow2` | ✅ HACS convention | ❌ Less descriptive | Good for discovery |
| `ha-allow2` | ✅ HA convention | ❌ Less clear | Acceptable |

### Recommended
```
Repository: allow2/homeassistant
OR
Repository: allow2-homeassistant
```

---

## 4. HACS Display Name

**Value:** `"Allow2 Parental Controls"`

### Purpose
- Used in HACS store for discovery
- More descriptive than just "Allow2"
- Helps users understand functionality

### Location
Set in `hacs.json`:
```json
{
  "name": "Allow2 Parental Controls",
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

---

## 5. Directory Structure

```
homeassistant/                          # GitHub repository
├── README.md
├── hacs.json
├── LICENSE
└── custom_components/
    └── allow2/                         # Integration domain
        ├── __init__.py
        ├── manifest.json               # domain: "allow2", name: "Allow2"
        ├── config_flow.py
        ├── const.py
        ├── api.py
        ├── coordinator.py
        ├── sensor.py
        ├── switch.py
        ├── services.yaml
        ├── strings.json
        └── translations/
            └── en.json
```

---

## 6. manifest.json (Complete Example)

```json
{
  "domain": "allow2",
  "name": "Allow2",
  "codeowners": ["@allow2"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/allow2/homeassistant",
  "iot_class": "cloud_polling",
  "issue_tracker": "https://github.com/allow2/homeassistant/issues",
  "requirements": ["aiohttp>=3.8.0"],
  "version": "1.0.0",
  "integration_type": "hub"
}
```

### Key Fields Explained

| Field | Value | Purpose |
|-------|-------|---------|
| `domain` | `"allow2"` | Technical identifier, must be unique |
| `name` | `"Allow2"` | User-facing name in UI |
| `config_flow` | `true` | Enables UI-based configuration |
| `iot_class` | `"cloud_polling"` | Indicates cloud API polling |
| `integration_type` | `"hub"` | Acts as hub for multiple children/devices |

---

## 7. Service Names

Services are prefixed with the domain automatically.

### Pattern
```
allow2.<service_name>
```

### Services Provided
```yaml
# services.yaml
check_quota:
  name: Check Quota
  description: Check if a child has quota remaining for an activity
  fields:
    child_id:
      description: Allow2 child ID
      example: 12345
    activity:
      description: Activity type (gaming, internet, etc.)
      example: "gaming"

log_activity:
  name: Log Activity
  description: Log usage and consume quota
  fields:
    child_id:
      description: Allow2 child ID
      example: 12345
    activity:
      description: Activity type
      example: "gaming"
    duration_seconds:
      description: Duration in seconds
      example: 300
```

### Usage in Automations
```yaml
service: allow2.check_quota
service: allow2.log_activity
```

---

## 8. Entity Naming

Entities follow the pattern: `<platform>.<domain>_<description>`

### Examples
```python
# Sensors (time remaining)
sensor.allow2_bobby_gaming_remaining
sensor.allow2_bobby_internet_remaining
sensor.allow2_sarah_screen_time_quota

# Binary Sensors (status flags)
binary_sensor.allow2_bobby_banned
binary_sensor.allow2_sarah_quota_exhausted

# Switches (device control)
switch.allow2_xbox_access
switch.allow2_tv_access
```

### Entity Naming Best Practices
- Use `snake_case` (lowercase with underscores)
- Start with domain: `allow2_`
- Include child name or ID
- Include activity type
- Be descriptive but concise

---

## 9. Configuration Keys

Configuration options use `snake_case`:

```python
# In config_flow.py
CONF_API_KEY = "api_key"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_POLL_INTERVAL = "poll_interval"

# User data schema
{
    vol.Required(CONF_API_KEY): str,
    vol.Required(CONF_DEVICE_ID): str,
    vol.Optional(CONF_DEVICE_NAME, default="Home Assistant"): str,
    vol.Optional(CONF_POLL_INTERVAL, default=300): int,
}
```

---

## 10. Translation Keys

Translation strings in `strings.json` and `en.json`:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Allow2 Setup",
        "description": "Enter your Allow2 API credentials",
        "data": {
          "api_key": "API Key",
          "device_id": "Device ID",
          "device_name": "Device Name"
        }
      }
    },
    "error": {
      "invalid_auth": "Invalid API key or device ID",
      "cannot_connect": "Cannot connect to Allow2 API"
    }
  }
}
```

---

## 11. Python Module Structure

```python
# custom_components/allow2/__init__.py
"""The Allow2 integration."""

DOMAIN = "allow2"
PLATFORMS = ["sensor", "binary_sensor"]

# custom_components/allow2/const.py
"""Constants for the Allow2 integration."""

DOMAIN = "allow2"
CONF_API_KEY = "api_key"
CONF_DEVICE_ID = "device_id"
DEFAULT_POLL_INTERVAL = 300

# custom_components/allow2/api.py
"""Allow2 API client."""

class Allow2ApiClient:
    """Allow2 API client implementation."""

    async def check_quota(self, child_id: int, activity: str) -> dict:
        """Check quota for a child."""
        pass
```

---

## 12. Comparison: Naming Across Ecosystem

| Component | allow2homeassistant | allow2automate-homeassistant |
|-----------|---------------------|------------------------------|
| **Technology** | HA Custom Integration | Plugin for allow2automate |
| **Domain** | `allow2` | N/A (not HA integration) |
| **Repository** | `allow2/homeassistant` | `allow2/automate` (under plugins/) |
| **Service Calls** | `allow2.check_quota` | Via allow2automate API |
| **Entities** | `sensor.allow2_*` | None (external control) |
| **Installation** | HACS | Bundled with allow2automate |

---

## 13. HACS Configuration

```json
{
  "name": "Allow2 Parental Controls",
  "content_in_root": false,
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

### HACS Repository Structure
```
allow2/homeassistant/
├── custom_components/
│   └── allow2/              # Integration code here
├── README.md                # Shown in HACS
├── hacs.json               # HACS configuration
├── LICENSE
└── .github/
    └── workflows/
        └── validate.yml     # HACS validation
```

---

## 14. Common Patterns from Official Integrations

### Examples for Reference

| Integration | Domain | Repository | Display Name |
|-------------|--------|------------|--------------|
| Google Assistant | `google_assistant` | `home-assistant/core` | "Google Assistant" |
| Philips Hue | `hue` | `home-assistant/core` | "Philips Hue" |
| Z-Wave JS | `zwave_js` | `home-assistant/core` | "Z-Wave JS" |
| HACS | `hacs` | `hacs/integration` | "HACS" |

### Pattern We Follow
```
Domain:     allow2                 (short, matches brand)
Name:       "Allow2"               (brand presentation)
Repository: allow2/homeassistant   (clear, organized)
HACS Name:  "Allow2 Parental Controls"  (descriptive)
```

---

## 15. Checklist for Naming Consistency

Before publishing, verify:

- [ ] `manifest.json` has `"domain": "allow2"`
- [ ] `manifest.json` has `"name": "Allow2"`
- [ ] Directory is `custom_components/allow2/`
- [ ] Repository is `allow2/homeassistant` or `allow2-homeassistant`
- [ ] `hacs.json` has `"name": "Allow2 Parental Controls"`
- [ ] All service calls use `allow2.*` prefix
- [ ] All entities use `allow2_` prefix
- [ ] All constants use `UPPERCASE_SNAKE_CASE`
- [ ] All config keys use `lowercase_snake_case`
- [ ] Documentation references correct domain/names

---

## Summary

| Type | Value | Notes |
|------|-------|-------|
| **Domain** | `allow2` | Technical identifier, cannot change |
| **Display Name** | `"Allow2"` | User-facing in HA UI |
| **Repository** | `allow2/homeassistant` | GitHub repo name |
| **HACS Name** | `"Allow2 Parental Controls"` | Discovery in HACS store |
| **Service Prefix** | `allow2.*` | e.g., `allow2.check_quota` |
| **Entity Prefix** | `allow2_` | e.g., `sensor.allow2_bobby_gaming` |

---

## References

- [Home Assistant Integration Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- [Home Assistant Integration File Structure](https://developers.home-assistant.io/docs/creating_integration_file_structure/)
- [HACS Integration Publishing](https://hacs.xyz/docs/publish/integration/)
- [Home Assistant Entities and Domains](https://www.home-assistant.io/docs/configuration/entities_domains/)
- [Home Assistant Brands](https://developers.home-assistant.io/docs/creating_integration_brand/)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-15
**Status:** Official naming convention for allow2homeassistant integration
