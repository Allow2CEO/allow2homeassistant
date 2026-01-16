# Allow2 Home Assistant Integration - Overview

## Purpose

The **allow2homeassistant** integration enables parents to enforce digital wellbeing and parental controls on their Home Assistant smart home devices using the Allow2 service.

## What is Allow2?

Allow2 (https://allow2.com) is a parental control service that helps parents manage their children's screen time and device usage across multiple platforms. It provides:

- **Quota Management**: Set daily/weekly time limits for different activities
- **Activity Tracking**: Log and monitor device usage
- **Flexible Scheduling**: Different rules for weekdays/weekends
- **Multiple Children**: Separate profiles and limits for each child
- **Cloud-Based**: Centralized control accessible from anywhere
- **Ban Windows**: Block device usage during specific times (homework, dinner, bedtime)

## Why This Integration?

Home Assistant is increasingly used to control entertainment and computing devices that children use:

- **Media Centers**: Kodi, Plex, Xbox, PlayStation
- **TVs and Displays**: Smart TVs, streaming devices
- **Gaming Consoles**: Xbox, PlayStation, Nintendo Switch
- **Smart Plugs**: Control power to computers, TVs, gaming systems
- **Media Players**: Sonos, Chromecast, Apple TV

Without parental controls, these devices can be used unrestricted. This integration brings Allow2's proven parental control system directly into Home Assistant.

## Target Audience

### Primary Users: Tech-Savvy Parents
Parents who:
- Already use Home Assistant for home automation
- Want parental controls for HA-connected devices
- Prefer open-source, self-hosted solutions
- Are comfortable writing Home Assistant automations
- Don't need to control devices outside Home Assistant

### NOT for:
- Parents who need to control multiple platforms (Windows, macOS, phones) - use **allow2automate-homeassistant** instead
- Parents who want a simple GUI without YAML - use **allow2automate** parent app instead
- Users unfamiliar with Home Assistant automations

## Key Use Cases

### 1. Gaming Console Control
Enforce time limits on Xbox, PlayStation, or Nintendo Switch:
```yaml
# Check quota every 5 minutes while gaming
# Turn off console when time is up
```

### 2. TV/Media Center Time Limits
Control access to Kodi, Plex, smart TVs:
```yaml
# Monitor media player usage
# Pause/stop playback when quota exhausted
```

### 3. Computer Access via Smart Plugs
Control desktop computers through power:
```yaml
# Check quota before allowing computer to power on
# Cut power when time limit reached
```

### 4. Internet Access Control
Manage router or access point settings:
```yaml
# Enable/disable WiFi access for specific devices
# Block internet during homework time
```

### 5. Multi-Child Household
Different limits for different children:
```yaml
# Johnny: 2 hours gaming on weekdays
# Sarah: 3 hours total screen time
# Separate tracking and enforcement
```

## How It Works

### Workflow

1. **Parent Sets Limits**: Configure daily quotas in Allow2 web/mobile app
2. **HA Monitors Usage**: Home Assistant automations check device state
3. **Integration Checks Quota**: Calls Allow2 API to verify remaining time
4. **Logs Usage**: Records device usage to Allow2 cloud
5. **Enforces Limits**: Turns off devices when quota exhausted
6. **Notifies Users**: Sends notifications to child's device

### Example Flow

```
Child turns on Xbox
  ↓
HA detects Xbox is "playing"
  ↓
Automation triggers every 5 minutes
  ↓
allow2.check_quota service called
  ↓
Allow2 API returns: "20 minutes remaining"
  ↓
Continue monitoring
  ↓
[After 20 minutes]
  ↓
Allow2 API returns: "Quota exhausted"
  ↓
HA turns off Xbox
  ↓
Sends notification to child
```

## Advantages Over External Solutions

### vs. allow2automate-homeassistant

**Advantages of allow2homeassistant:**
- No additional software to install and maintain
- Native Home Assistant integration
- Deeper integration with HA's automation engine
- Lower latency (no external communication)
- Works offline (cached quota data)
- More flexible automation possibilities

**Disadvantages:**
- Requires Home Assistant knowledge
- Only controls HA-connected devices
- No GUI for parent configuration
- Steeper learning curve

### vs. Router-Based Parental Controls

**Advantages:**
- More granular control (specific devices, not just internet)
- Activity-based tracking (gaming vs. homework)
- Integration with physical device state
- Can't be bypassed with VPN
- Works with wired and wireless devices

## Real-World Benefits

### For Parents
- **Peace of Mind**: Automated enforcement of agreed-upon limits
- **Consistency**: Rules apply even when parents aren't home
- **Visibility**: See exactly how children spend screen time
- **Flexibility**: Adjust limits remotely via Allow2 app
- **Teaching Tool**: Help children self-regulate digital usage

### For Children
- **Clear Boundaries**: Know exactly how much time they have
- **Fairness**: Objective, consistent rule enforcement
- **Transparency**: See their own usage and remaining time
- **Motivation**: Can earn extra time through good behavior (Allow2 feature)

## Privacy and Security

### Data Collection
The integration shares with Allow2:
- Child ID (not personal information)
- Activity type (e.g., "gaming", "television")
- Duration of usage
- Device identifier (generic, e.g., "xbox")

### Data NOT Collected
- Content watched/played
- Websites visited (if controlling computer)
- Personal messages or communications
- Location data
- Specific media titles

### Security
- Pairing tokens stored securely in Home Assistant (credentials are NOT stored)
- Communication over HTTPS
- No personal child information sent to Allow2
- Optional local quota caching

## Comparison with Similar Solutions

| Feature | allow2homeassistant | Screen Time Apps | Router Parental Controls |
|---------|---------------------|------------------|--------------------------|
| **Platform** | Home Assistant | iOS/Android | Network level |
| **Granularity** | Per-device | Per-app | Per-device (network) |
| **Activity Types** | Customizable | Pre-defined | Internet only |
| **Offline Work** | Cached quotas | No | Yes |
| **Bypass Potential** | Low (physical control) | Medium (app disable) | Medium (VPN) |
| **Setup Complexity** | High | Low | Medium |
| **Flexibility** | Very High | Low | Medium |

## Future Possibilities

With native Home Assistant integration, future features could include:

- **Sensors**: Expose quota data as HA sensors for dashboards
- **Services**: Additional services for logging activities, checking status
- **Events**: Fire HA events when quotas exhausted or updated
- **Lovelace Cards**: Custom UI cards for quota visualization
- **Blueprints**: Pre-built automation templates
- **Voice Assistants**: "Alexa, how much gaming time does Johnny have left?"

## Next Steps

Ready to get started? Check out:
- [Installation Guide](INSTALLATION.md) - Install the integration
- [Configuration Guide](CONFIGURATION.md) - Pair with your Allow2 account
- [Use Cases](USE_CASES.md) - Real-world automation examples
