# Changelog

All notable changes to the Allow2 Home Assistant Integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Service calls to start/stop activity timers
- Custom activity support
- Day type sensors (school day, weekend, holiday)
- Options flow for runtime configuration changes

## [1.0.0] - 2025-01-15

### Added
- Initial release of Allow2 Home Assistant Integration
- Multi-architecture support (armhf, armv7, aarch64, amd64, i386)
- Automatic installation of Allow2 custom component to Home Assistant
- Device pairing with Allow2 service using credentials
- Binary sensors for activity allowances per child:
  - `binary_sensor.<child>_internet_allowed`
  - `binary_sensor.<child>_gaming_allowed`
  - `binary_sensor.<child>_social_media_allowed`
  - `binary_sensor.<child>_television_allowed`
  - `binary_sensor.<child>_screen_time_allowed`
  - `binary_sensor.<child>_messaging_allowed`
- Duration sensors for remaining time per activity:
  - `sensor.<child>_internet_remaining`
  - `sensor.<child>_gaming_remaining`
  - `sensor.<child>_social_media_remaining`
  - `sensor.<child>_television_remaining`
  - `sensor.<child>_screen_time_remaining`
  - `sensor.<child>_messaging_remaining`
- Configurable update interval for status checks
- Health check endpoint for container monitoring
- English translations for configuration options
- Automatic file verification on startup
- Periodic monitoring and reinstallation if files are missing
- Comprehensive entity attributes including:
  - Child ID and name
  - Activity ID and name
  - Banned status
  - Time block allowance status
  - Remaining seconds

### Configuration Options
- `log_level` - Set logging verbosity (debug, info, warning, error, critical)
- `update_interval` - Interval in seconds for health checks (60-3600)
- `copy_on_start` - Enable/disable automatic integration file installation

### Technical Details
- Based on Home Assistant official Python 3.12 Alpine base images
- Uses aiohttp for async API communication
- Implements Home Assistant DataUpdateCoordinator for efficient polling
- Config flow support for UI-based setup
- Watchdog support for automatic restart on failure

### Security
- Implements Allow2's secure device pairing model
- Parent credentials used only during initial pairing
- Only pairing tokens stored locally
- All API communication over HTTPS/TLS

[Unreleased]: https://github.com/Allow2/allow2homeassistant/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Allow2/allow2homeassistant/releases/tag/v1.0.0
