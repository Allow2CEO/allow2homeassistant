# Allow2 Home Assistant Integration

[![GitHub Release](https://img.shields.io/github/v/release/Allow2CEO/allow2homeassistant?style=flat-square)](https://github.com/Allow2CEO/allow2homeassistant/releases)
[![License](https://img.shields.io/github/license/Allow2CEO/allow2homeassistant?style=flat-square)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-blue?style=flat-square)](https://www.home-assistant.io/)

A Home Assistant custom integration that brings Allow2 parental controls to your smart home, enabling powerful automations based on your children's screen time quotas and activity permissions.

## Quick Install

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FAllow2CEO%2Fallow2homeassistant)

Or manually add this repository URL to HACS:
```
https://github.com/Allow2CEO/allow2homeassistant
```

## Features

- **Real-time Activity Monitoring** - Track whether activities (Gaming, Internet, TV, etc.) are currently allowed for each child
- **Time Remaining Sensors** - Know exactly how much screen time remains for each activity
- **Multiple Children Support** - Manage all your children from a single integration
- **Automation Ready** - Create powerful automations that respond to Allow2 status changes
- **Secure Device Pairing** - Uses Allow2's secure device pairing model (credentials are never stored)
- **Cloud Polling** - Automatically syncs with your Allow2 account

## Supported Activities

| Activity | Description |
|----------|-------------|
| Internet | General internet browsing |
| Gaming | Video games, consoles, PC games |
| Social Media | Social networking platforms |
| Television | TV watching, streaming services |
| Screen Time | General screen usage |
| Messaging | Chat and messaging apps |

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add `https://github.com/Allow2CEO/allow2homeassistant` with category "Integration"
5. Click "Download" on the Allow2 integration
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/Allow2CEO/allow2homeassistant/releases)
2. Extract and copy the `custom_components/allow2` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

### Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Allow2"**
4. Enter your Allow2 parent account credentials
5. The integration will pair and discover your children automatically

## Example Automations

### Turn off gaming PC when gaming time expires

```yaml
automation:
  - alias: "Disable gaming PC when quota reached"
    trigger:
      - platform: state
        entity_id: binary_sensor.alex_gaming_allowed
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.gaming_pc
```

### Announce remaining screen time

```yaml
automation:
  - alias: "Warn about low screen time"
    trigger:
      - platform: numeric_state
        entity_id: sensor.alex_screen_time_remaining
        below: 600  # 10 minutes
    action:
      - service: tts.speak
        target:
          entity_id: media_player.living_room
        data:
          message: "Alex, you have 10 minutes of screen time remaining"
```

## Documentation

- [Detailed Documentation](DOCS.md) - Full setup guide, configuration options, and usage examples
- [Configuration Guide](docs/CONFIGURATION.md) - Detailed configuration options
- [API Integration](docs/API_INTEGRATION.md) - Technical details about the Allow2 API

## Requirements

- Home Assistant 2024.1 or newer
- An active [Allow2](https://allow2.com) parent account
- Children configured in your Allow2 account

## Support

- **Issues**: [GitHub Issues](https://github.com/Allow2CEO/allow2homeassistant/issues)
- **Allow2 Help**: [Allow2 Support](https://allow2.com/support)
- **Community**: [Home Assistant Community Forum](https://community.home-assistant.io/)

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the main repository.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Credits

- [Allow2](https://allow2.com) - Parental control platform
- [Home Assistant](https://www.home-assistant.io/) - Open source home automation
