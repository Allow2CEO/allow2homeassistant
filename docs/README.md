# Allow2 Home Assistant Integration

A native Home Assistant custom integration that provides parental controls using the Allow2 API.

## Quick Overview

**allow2homeassistant** is a Home Assistant custom integration that runs entirely within Home Assistant to enforce Allow2 parental controls on your smart home devices.

### What Makes This Different?

This integration is the **inverse** of `allow2automate-homeassistant`:

| Aspect | allow2automate-homeassistant | allow2homeassistant |
|--------|------------------------------|---------------------|
| **Architecture** | External agent reaches INTO HA | Native HA integration |
| **Installation** | Requires allow2automate parent app | HACS or manual install |
| **Configuration** | Parent app UI | Home Assistant config flow UI |
| **Device Control** | WebSocket/REST API calls | Native HA service calls |
| **Dependencies** | Requires allow2automate running | Self-contained in HA |
| **Best For** | Multi-platform control (HA + laptops + phones) | Home Assistant-only environments |
| **Complexity** | Parent-friendly UI | Requires HA knowledge |

## When to Use Each?

### Use **allow2automate-homeassistant** when:
- You want to control multiple platforms (Home Assistant + Windows PCs + macOS + phones)
- You prefer a unified parent control UI outside Home Assistant
- You want centralized management of all devices
- You're already using allow2automate for other platforms

### Use **allow2homeassistant** when:
- You ONLY need parental controls for Home Assistant devices
- You prefer native Home Assistant configuration
- You don't want to run additional software (allow2automate)
- You're comfortable with Home Assistant automations and YAML
- You want deeper integration with HA's automation engine

## Key Features

- **Native Home Assistant Integration**: Runs entirely within HA
- **HACS Installable**: Easy installation via Home Assistant Community Store
- **Config Flow UI**: Configure through Home Assistant's UI
- **Allow2 API Integration**: Direct communication with Allow2 cloud service
- **Real-time Quota Checking**: Monitors usage and enforces limits
- **Flexible Device Control**: Works with any HA entity (switches, media players, lights, etc.)
- **Automation Integration**: Trigger automations based on quota status
- **Multiple Children**: Support for multiple child profiles
- **Activity Logging**: Automatic usage logging to Allow2

## Quick Start

```yaml
# Example automation to enforce screen time
automation:
  - alias: "Xbox Time Limit - Johnny"
    trigger:
      - platform: time_pattern
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
          device_id: "xbox"
        response_variable: quota_response
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ quota_response.allowed == false }}"
            sequence:
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox
              - service: notify.mobile_app_johnnys_phone
                data:
                  message: "Gaming time is up! Xbox has been turned off."
```

## Documentation

- [Overview](OVERVIEW.md) - Detailed purpose and use cases
- [Architecture](ARCHITECTURE.md) - Technical design and components
- [Installation](INSTALLATION.md) - How to install and set up
- [Configuration](CONFIGURATION.md) - Configuration options and API setup
- [Use Cases](USE_CASES.md) - Real-world examples and automations
- [API Integration](API_INTEGRATION.md) - How it communicates with Allow2

## Inspiration

This integration is inspired by [allow2nodered](https://www.npmjs.com/package/allow2nodered), which provides similar functionality for Node-RED users. We've adapted that approach for Home Assistant's native integration framework.

## Support

- **Issues**: Report bugs and request features on GitHub
- **Allow2 Platform**: https://allow2.com
- **Home Assistant Community**: Home Assistant forums

## License

MIT License - See LICENSE file for details
