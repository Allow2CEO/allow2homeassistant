# Allow2 Home Assistant Integration - Documentation

## Introduction

The Allow2 Home Assistant integration connects your smart home to the [Allow2](https://allow2.com) parental control platform. This enables you to create powerful automations that respond to your children's screen time quotas, activity permissions, and time-based restrictions.

### What is Allow2?

Allow2 is a cross-platform parental control service that helps families manage screen time across all devices. Parents set daily quotas and time restrictions, while children learn to manage their own time responsibly.

### Why Integrate with Home Assistant?

By bringing Allow2 into Home Assistant, you can:

- **Automate device control** - Turn off gaming consoles, smart TVs, or computers when quotas are reached
- **Create visual indicators** - Light up a smart bulb to show remaining time status
- **Send notifications** - Alert children (and parents) when screen time is running low
- **Track usage patterns** - Log activity status changes for analysis
- **Enforce boundaries** - Automatically lock devices during homework time or bedtime

---

## Installation

### Prerequisites

- Home Assistant version 2024.1 or newer
- An active Allow2 parent account
- At least one child configured in your Allow2 account
- Network access to `api.allow2.com`

### Method 1: HACS (Recommended)

[HACS](https://hacs.xyz/) (Home Assistant Community Store) is the easiest way to install custom integrations.

1. Ensure HACS is installed in your Home Assistant instance
2. Open HACS from the sidebar
3. Click on "Integrations"
4. Click the three-dot menu in the top right corner
5. Select "Custom repositories"
6. Enter the repository URL: `https://github.com/Allow2/allow2homeassistant`
7. Select "Integration" as the category
8. Click "Add"
9. Search for "Allow2" in HACS
10. Click "Download"
11. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [GitHub releases page](https://github.com/Allow2/allow2homeassistant/releases)
2. Extract the downloaded archive
3. Copy the `custom_components/allow2` folder to your Home Assistant configuration directory:
   ```
   /config/custom_components/allow2/
   ```
4. Restart Home Assistant

### Verifying Installation

After restarting, verify the integration is loaded:

1. Go to **Settings** > **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for "Allow2"

If "Allow2" appears in the search results, the installation was successful.

---

## Configuration

### Initial Setup

1. Navigate to **Settings** > **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for and select **"Allow2"**
4. Enter your Allow2 credentials:

| Field | Required | Description |
|-------|----------|-------------|
| Email | Yes | Your Allow2 parent account email |
| Password | Yes | Your Allow2 account password |
| Device Token | No | Advanced: Override the default device token |
| Device Name | No | How this Home Assistant appears in Allow2 (default: "Home Assistant") |

5. Click **Submit**
6. The integration will pair with your Allow2 account and discover your children

### What Happens During Pairing

When you submit your credentials:

1. The integration securely connects to Allow2's API
2. Your Home Assistant instance is registered as a paired device
3. A unique pairing token is generated and stored locally
4. Your credentials are **immediately discarded** (never stored)
5. The list of children from your account is retrieved
6. Sensors are created for each child and activity type

### Post-Setup Options

After initial setup, you can configure additional options:

1. Go to **Settings** > **Devices & Services**
2. Find the Allow2 integration
3. Click **"Configure"**

Available options:
- View pairing status
- See connected children
- Update device name

---

## Entities

The integration creates two types of entities for each child and activity combination.

### Binary Sensors

Binary sensors indicate whether an activity is currently **allowed** or **not allowed**.

**Entity ID Pattern:** `binary_sensor.<child_name>_<activity>_allowed`

**Examples:**
- `binary_sensor.alex_gaming_allowed`
- `binary_sensor.emma_internet_allowed`
- `binary_sensor.alex_television_allowed`

**States:**
- `on` - Activity is allowed (has quota remaining and not in restricted time)
- `off` - Activity is not allowed (quota exhausted, banned, or time-restricted)

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `child_id` | integer | Allow2 child ID |
| `child_name` | string | Child's name |
| `activity_id` | integer | Allow2 activity ID |
| `activity_name` | string | Activity name |
| `banned` | boolean | Whether activity is permanently banned |
| `time_block_allowed` | boolean | Whether current time block allows activity |
| `remaining_seconds` | integer | Remaining quota in seconds |

### Sensors

Sensors show the **remaining time** for each activity in seconds.

**Entity ID Pattern:** `sensor.<child_name>_<activity>_remaining`

**Examples:**
- `sensor.alex_gaming_remaining`
- `sensor.emma_screen_time_remaining`
- `sensor.alex_social_media_remaining`

**Unit:** Seconds

**Device Class:** Duration

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `child_id` | integer | Allow2 child ID |
| `child_name` | string | Child's name |
| `activity_id` | integer | Allow2 activity ID |
| `activity_name` | string | Activity name |
| `allowed` | boolean | Whether activity is currently allowed |
| `banned` | boolean | Whether activity is permanently banned |
| `time_block_allowed` | boolean | Whether current time block allows activity |

### Activities Created

For each child, the following activities are monitored:

| Activity ID | Name | Entity Suffix |
|-------------|------|---------------|
| 1 | Internet | `internet` |
| 2 | Gaming | `gaming` |
| 3 | Social Media | `social_media` |
| 4 | Television | `television` |
| 5 | Screen Time | `screen_time` |
| 6 | Messaging | `messaging` |

---

## Usage Examples

### Basic Automations

#### Turn Off Smart TV When Screen Time Ends

```yaml
automation:
  - alias: "Turn off TV when Alex's TV time ends"
    trigger:
      - platform: state
        entity_id: binary_sensor.alex_television_allowed
        to: "off"
    action:
      - service: media_player.turn_off
        target:
          entity_id: media_player.living_room_tv
      - service: notify.mobile_app_alex_phone
        data:
          message: "TV time is over! The TV has been turned off."
```

#### Lock Gaming PC When Gaming Quota Exhausted

```yaml
automation:
  - alias: "Lock gaming PC when quota reached"
    trigger:
      - platform: state
        entity_id: binary_sensor.emma_gaming_allowed
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.emma_gaming_pc
```

### Time-Based Warnings

#### 15-Minute Warning

```yaml
automation:
  - alias: "Warn Alex about low gaming time"
    trigger:
      - platform: numeric_state
        entity_id: sensor.alex_gaming_remaining
        below: 900  # 15 minutes = 900 seconds
    condition:
      - condition: numeric_state
        entity_id: sensor.alex_gaming_remaining
        above: 0
    action:
      - service: tts.speak
        target:
          entity_id: media_player.alex_room_speaker
        data:
          message: "Alex, you have {{ (states('sensor.alex_gaming_remaining') | int / 60) | round(0) }} minutes of gaming time left."
```

#### Color-Coded Status Light

```yaml
automation:
  - alias: "Update Emma's status light based on screen time"
    trigger:
      - platform: state
        entity_id: sensor.emma_screen_time_remaining
    action:
      - choose:
          - conditions:
              - condition: numeric_state
                entity_id: sensor.emma_screen_time_remaining
                above: 1800  # More than 30 minutes
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.emma_desk_lamp
                data:
                  color_name: green
          - conditions:
              - condition: numeric_state
                entity_id: sensor.emma_screen_time_remaining
                above: 600  # 10-30 minutes
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.emma_desk_lamp
                data:
                  color_name: yellow
          - conditions:
              - condition: numeric_state
                entity_id: sensor.emma_screen_time_remaining
                above: 0  # Less than 10 minutes
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.emma_desk_lamp
                data:
                  color_name: red
        default:
          - service: light.turn_off
            target:
              entity_id: light.emma_desk_lamp
```

### Dashboard Cards

#### Lovelace Entity Card

```yaml
type: entities
title: Alex's Screen Time
entities:
  - entity: binary_sensor.alex_gaming_allowed
    name: Gaming Allowed
  - entity: sensor.alex_gaming_remaining
    name: Gaming Time Left
    format: duration
  - entity: binary_sensor.alex_internet_allowed
    name: Internet Allowed
  - entity: sensor.alex_internet_remaining
    name: Internet Time Left
    format: duration
```

#### Conditional Card (Show Only When Activity Blocked)

```yaml
type: conditional
conditions:
  - entity: binary_sensor.alex_gaming_allowed
    state: "off"
card:
  type: markdown
  content: >
    ## Gaming Blocked
    Alex's gaming time has ended for today.
```

---

## Troubleshooting

### Common Issues

#### "auth_failed" Error

**Cause:** Invalid email or password

**Solution:**
1. Verify your Allow2 credentials by logging into [allow2.com](https://allow2.com)
2. Reset your password if necessary
3. Re-add the integration with correct credentials

#### "cannot_connect" Error

**Cause:** Network connectivity issues

**Solution:**
1. Check your internet connection
2. Verify Home Assistant can reach `api.allow2.com`
3. Check if Allow2's service is operational
4. Look for firewall rules blocking outbound HTTPS

#### Sensors Show "Unknown" or "Unavailable"

**Cause:** API communication issue or invalid pairing

**Solution:**
1. Check Home Assistant logs for detailed error messages
2. Remove and re-add the integration
3. Ensure your Allow2 subscription is active

#### No Children Appearing

**Cause:** No children configured in Allow2 account

**Solution:**
1. Log into your Allow2 account
2. Add children through the Allow2 app or website
3. Remove and re-add the Home Assistant integration

### Viewing Logs

To see detailed logs for the Allow2 integration:

1. Add to your `configuration.yaml`:
   ```yaml
   logger:
     default: warning
     logs:
       custom_components.allow2: debug
   ```
2. Restart Home Assistant
3. View logs in **Settings** > **System** > **Logs**

### Re-pairing

If you need to re-pair (e.g., after changing your Allow2 password):

1. Go to **Settings** > **Devices & Services**
2. Find the Allow2 integration
3. Click the three-dot menu
4. Select **Delete**
5. Add the integration again with your new credentials

---

## Frequently Asked Questions

### Is my password stored?

No. Your password is only used during the initial pairing process. The integration stores only the pairing tokens, never your credentials.

### How often does the integration update?

The integration polls the Allow2 API periodically to check for quota changes. The default polling interval is designed to balance responsiveness with API rate limits.

### Can I use this with multiple Allow2 accounts?

Each integration instance connects to one Allow2 account. If you have multiple accounts, you would need to add the integration multiple times (not recommended).

### Does this work with Allow2 Free accounts?

Yes, the integration works with all Allow2 account types. Feature availability depends on your Allow2 subscription level.

### Why don't I see all activities?

The integration monitors the six standard Allow2 activities. Custom activities defined in your Allow2 account may not appear.

### Can I start/stop time through Home Assistant?

Currently, the integration is read-only. It can check quotas and activity status but cannot modify Allow2 settings or start/stop timers.

### What happens if Allow2's servers are down?

Sensors will show "unavailable" until connectivity is restored. Automations triggered by state changes will not fire during outages.

### Is this an official Allow2 integration?

This is a community-developed integration that uses Allow2's public API. It is designed to work seamlessly with the Allow2 platform.

---

## Technical Details

### API Communication

- **Base URL:** `https://api.allow2.com`
- **Authentication:** Device pairing tokens (not API keys)
- **Protocol:** HTTPS with TLS encryption
- **Data Format:** JSON

### Polling Behavior

- The integration uses Home Assistant's `DataUpdateCoordinator` for efficient polling
- Each child has a separate coordinator to isolate failures
- Polling respects Allow2's rate limits

### Security Model

- Uses Allow2's consumer device pairing model
- Credentials are used once during pairing and immediately discarded
- Only pairing tokens (`userId`, `pairId`, `pairToken`) are stored
- All communication uses encrypted HTTPS

For more technical details, see the [API Integration Guide](docs/API_INTEGRATION.md).
