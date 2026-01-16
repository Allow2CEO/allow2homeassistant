# Allow2 Home Assistant Integration - Configuration Guide

This document describes the device pairing UI flow for configuring the Allow2 integration with Home Assistant.

## Overview

The Allow2 integration uses a device pairing approach rather than API key entry. This means your Home Assistant instance becomes a registered device on your Allow2 account, similar to how phones or tablets are paired.

## Pairing Flow for Users

### Step 1: Add Integration

1. Go to **Settings** > **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Allow2"**
4. Select the Allow2 integration from the list

### Step 2: Enter Credentials

The config flow presents a form with the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| **Email** | Yes | Your Allow2 parent account email address |
| **Password** | Yes | Your Allow2 account password |
| **Device Token** | No | Override the default device token (advanced users only). Default: `mtG8xbFR1cuJkuXn` |
| **Device Name** | No | How this Home Assistant instance appears in your Allow2 account. Default: `Home Assistant` |

**Note:** The Device Token and Device Name fields are optional. Most users should leave these at their default values.

### Step 3: Pairing Process

When you submit the form, the integration performs the following steps:

1. **Connects** to the Allow2 API using your email and password
2. **Pairs** this Home Assistant instance as a device to your Allow2 account
3. **Retrieves** your list of children from your Allow2 account
4. **Stores** the pairing tokens securely in Home Assistant's configuration

If pairing is successful, you will see a confirmation message.

### Step 4: Configuration Complete

After successful pairing:

- Your children appear as options for use in automations and scripts
- The integration can check activity quotas for each child
- Usage is logged to your Allow2 account automatically
- You can create automations based on whether activities are allowed or blocked

## Child Configuration

### Finding Child IDs

After integration setup, you need to know each child's ID for automations.

**Method 1: Check Logs**
1. Go to **Settings** → **System** → **Logs**
2. Search for "allow2"
3. Look for entry:
   ```
   [custom_components.allow2] Found children:
   - ID: 12345, Name: Johnny, Age: 10
   - ID: 67890, Name: Sarah, Age: 8
   ```

**Method 2: Test Service Call**
1. Go to **Developer Tools** → **Services**
2. Call `allow2.check_quota` with a test child ID
3. If wrong ID, error message will show available IDs

**Method 3: Allow2 Web Portal**
1. Log in to https://allow2.com
2. Go to **Children**
3. Click on child profile
4. Child ID shown in URL or profile details

### Mapping Children to Devices

Create a helper in Home Assistant to map children to their devices:

**Option 1: Input Select Helper (UI)**

1. Go to **Settings** → **Devices & Services** → **Helpers**
2. Click **+ Create Helper**
3. Choose **Dropdown**
4. Configure:
   ```
   Name: Xbox Current User
   Options:
     - Johnny (12345)
     - Sarah (67890)
     - Not in use
   ```

**Option 2: YAML Configuration**

```yaml
# configuration.yaml
input_select:
  xbox_current_user:
    name: Xbox Current User
    options:
      - "Johnny (12345)"
      - "Sarah (67890)"
      - "Not in use"
    initial: "Not in use"

  computer_current_user:
    name: Computer Current User
    options:
      - "Johnny (12345)"
      - "Sarah (67890)"
      - "Not in use"
    initial: "Not in use"
```

**Use in Automations:**
```yaml
automation:
  - alias: "Enforce Xbox Quota"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    condition:
      - condition: not
        conditions:
          - condition: state
            entity_id: input_select.xbox_current_user
            state: "Not in use"
    action:
      - service: allow2.check_quota
        data:
          child_id: >
            {% if is_state('input_select.xbox_current_user', 'Johnny (12345)') %}
              12345
            {% elif is_state('input_select.xbox_current_user', 'Sarah (67890)') %}
              67890
            {% endif %}
          activity: "gaming"
          device_id: "xbox"
        response_variable: quota
```

### Shared vs. Personal Devices

**Personal Devices** (one child per device):
- Use fixed child_id in automation
- Simpler automation logic
- Example: Johnny's tablet, Sarah's laptop

**Shared Devices** (multiple children use same device):
- Use input_select helper to track current user
- More complex automation logic
- Example: Family Xbox, living room TV

## Activity Configuration

### Defining Activities

Activities must match your Allow2 account configuration:

1. **Log in to Allow2 Web Portal**
2. **Go to Activities Section**
3. **Review Configured Activities**:
   - Default activities: gaming, internet, television, social
   - Custom activities: any you've created
4. **Use Activity Name in Lowercase**:
   - Allow2: "Gaming" → HA: `"gaming"`
   - Allow2: "Screen Time" → HA: `"screen_time"`

### Activity to Device Mapping

Map your Home Assistant devices to activity types:

```yaml
# Example mapping concept
Devices → Activities:
  media_player.xbox → "gaming"
  media_player.playstation → "gaming"
  media_player.living_room_tv → "television"
  switch.computer_plug → "internet"
  media_player.youtube_tv → "television"
```

**Implementation in a Script:**

```yaml
script:
  check_device_quota:
    fields:
      entity_id:
        description: "Device entity ID"
        example: "media_player.xbox"
      child_id:
        description: "Child ID"
        example: 12345
    sequence:
      - service: allow2.check_quota
        data:
          child_id: "{{ child_id }}"
          activity: >
            {% set device_activities = {
              'media_player.xbox': 'gaming',
              'media_player.playstation': 'gaming',
              'media_player.living_room_tv': 'television',
              'switch.computer_plug': 'internet'
            } %}
            {{ device_activities.get(entity_id, 'internet') }}
          device_id: "{{ entity_id }}"
        response_variable: quota_response
      - condition: template
        value_template: "{{ not quota_response.allowed }}"
      - service: homeassistant.turn_off
        target:
          entity_id: "{{ entity_id }}"
```

## Device Control Methods

The integration can enforce quotas on any Home Assistant entity that can be turned off:

### Controllable Devices

**Media Players:**
```yaml
media_player.xbox
media_player.playstation
media_player.apple_tv
media_player.chromecast
```

**Switches:**
```yaml
switch.computer_smart_plug
switch.tv_power
switch.gaming_console_outlet
```

**Lights** (for room-based control):
```yaml
light.bedroom  # Turn off bedroom lights to signal bedtime
```

### Control Methods

**Method 1: Generic Turn Off**
```yaml
service: homeassistant.turn_off
target:
  entity_id: media_player.xbox
```

**Method 2: Domain-Specific Service**
```yaml
service: media_player.turn_off
target:
  entity_id: media_player.xbox
```

**Method 3: Media Player Pause** (less disruptive)
```yaml
service: media_player.media_pause
target:
  entity_id: media_player.living_room_tv
```

**Method 4: Smart Plug**
```yaml
service: switch.turn_off
target:
  entity_id: switch.computer_plug
```

## Multi-Child Configuration

### Strategies for Multiple Children

**Strategy 1: Separate Automations** (Simpler, more explicit)
```yaml
automation:
  - alias: "Xbox Quota - Johnny"
    # ... Johnny's automation

  - alias: "Xbox Quota - Sarah"
    # ... Sarah's automation
```

**Strategy 2: Dynamic Automation** (More complex, less maintenance)
```yaml
automation:
  - alias: "Xbox Quota - Dynamic"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    action:
      - service: allow2.check_quota
        data:
          child_id: >
            {% if is_state('input_select.xbox_current_user', 'Johnny') %}
              12345
            {% elif is_state('input_select.xbox_current_user', 'Sarah') %}
              67890
            {% endif %}
          activity: "gaming"
          device_id: "xbox"
        response_variable: quota
      # ... rest of automation
```

## Notification Configuration

### Setting Up Notifications

**Mobile App Notifications** (recommended):

1. **Install Home Assistant Companion App** on child's device
2. **Use in Automations**:
   ```yaml
   service: notify.mobile_app_johnnys_phone
   data:
     message: "Gaming time is up!"
     title: "Allow2"
   ```

**Alternative Notification Methods:**
- **TTS (Text-to-Speech)**: Announce through smart speakers
- **Persistent Notifications**: Show in HA interface
- **Email**: Send email to child/parent

### Notification Best Practices

**1. Warning Before Cutoff:**
```yaml
- condition: template
  value_template: "{{ quota.remaining_minutes <= 10 and quota.remaining_minutes > 5 }}"
- service: notify.mobile_app
  data:
    message: "Warning: {{ quota.remaining_minutes }} minutes left!"
```

**2. Grace Period:**
```yaml
# Give 2 minutes to save game
- service: notify.mobile_app
  data:
    message: "Time is up. You have 2 minutes to save your game."
- delay: "00:02:00"
- service: media_player.turn_off
```

**3. Parent Notifications:**
```yaml
# Notify parent when quota enforced
- service: notify.mobile_app_parent
  data:
    message: "Johnny's gaming quota enforced. Xbox turned off."
```

## Options Flow

After the initial setup, you can access additional options by:

1. Going to **Settings** > **Devices & Services**
2. Finding the **Allow2** integration
3. Clicking **"Configure"**

Available options include:

- View current pairing status
- See the list of connected children
- Update the device name
- View connection details

## Credentials Storage

The integration stores the following data securely:

| Stored | Not Stored |
|--------|------------|
| `userId` - Your Allow2 user ID | Email address |
| `pairId` - The device pairing ID | Password |
| `pairToken` - Authentication token | |
| `children` - List of your children | |
| `timezone` - Your configured timezone | |

**Important:** Your email and password are only used during the initial pairing process. They are NOT stored after pairing is complete. Only the pairing tokens are retained.

## Unpairing / Removing the Integration

To unpair your Home Assistant from Allow2:

1. Go to **Settings** > **Devices & Services**
2. Find the **Allow2** integration
3. Click the three-dot menu (...)
4. Select **"Delete"** or **"Remove"**
5. Confirm the removal

When removed:
- The pairing tokens are cleared from Home Assistant
- The device may still appear in your Allow2 account until you remove it there
- All automations using Allow2 services will stop functioning

## Re-pairing

If you need to re-pair your Home Assistant (e.g., after a password change or if tokens become invalid):

1. **Delete** the existing Allow2 integration (see Unpairing section above)
2. **Add** the integration again following the steps in this guide
3. Enter your **current credentials** to establish a new pairing

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `auth_failed` | Invalid email or password | Verify your Allow2 account credentials |
| `cannot_connect` | Network or API issues | Check your internet connection and try again |
| `invalid_response` | Unexpected API response | Try again; contact support if persistent |
| `already_paired` | Device already registered | Use a different device name or check your Allow2 account |

### Getting Help

- Check the [Allow2 documentation](https://allow2.com)
- Review Home Assistant logs for detailed error messages
- Ensure your Allow2 account is active and in good standing

## Activity Types

The integration supports the following Allow2 activity types for quota checking:

| ID | Activity Name |
|----|---------------|
| 1 | Internet |
| 2 | Gaming |
| 3 | Social Media |
| 4 | Television |
| 5 | Screen Time |
| 6 | Messaging |

These activities can be used when creating automations to check if a child is allowed to engage in specific activities.

## Entity Naming Convention

Entities are created with the following naming pattern:

### Binary Sensors (Activity Allowed)
```
binary_sensor.<child_name>_<activity>_allowed
```

**Examples:**
- `binary_sensor.alex_gaming_allowed`
- `binary_sensor.emma_internet_allowed`

### Sensors (Time Remaining)
```
sensor.<child_name>_<activity>_remaining
```

**Examples:**
- `sensor.alex_gaming_remaining`
- `sensor.emma_screen_time_remaining`

## Advanced Configuration

### Custom Device Token

The default device token (`mtG8xbFR1cuJkuXn`) is pre-registered for Home Assistant integration. In rare cases, you may need to use a custom token:

1. Contact Allow2 support to register a custom device token
2. Enter the custom token during integration setup
3. Use the same token for all Home Assistant instances connecting to the same account

### Multiple Home Assistant Instances

If you have multiple Home Assistant instances:

1. Use unique device names for each instance (e.g., "Home Assistant - Main", "Home Assistant - Vacation Home")
2. All instances can pair with the same Allow2 account
3. Each instance creates its own set of sensors

### YAML Configuration (Advanced)

While the integration is configured via UI, some advanced options can be set in `configuration.yaml`:

```yaml
# configuration.yaml
allow2:
  # Cache settings
  cache_duration: 300  # 5 minutes (seconds)
  update_interval: 1800  # 30 minutes (seconds)

  # API settings
  api_timeout: 10  # Request timeout (seconds)
  max_retries: 3  # Retry attempts on failure
  retry_delay: 5  # Delay between retries (seconds)

  # Fail-safe mode
  fail_open: true  # Allow usage if API unavailable (default: true)
```

**fail_open Explanation:**
- `true`: If API fails, allow device usage (fail safely for users)
- `false`: If API fails, block device usage (fail securely)

### Debug Configuration

Enable detailed logging for troubleshooting:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.allow2: debug
    custom_components.allow2.api: debug
    custom_components.allow2.coordinator: debug
```

Restart Home Assistant to apply logging changes.

### Integration Reload

To reload configuration without restarting:

1. Go to **Settings** → **Devices & Services**
2. Find **Allow2**
3. Click **⋮** menu
4. Select **Reload**

This reloads:
- API connection
- Child list
- Cached data

## Related Documentation

- [Main Documentation](../DOCS.md) - Complete usage guide with automation examples
- [API Integration](API_INTEGRATION.md) - Technical API details
- [Changelog](../CHANGELOG.md) - Version history
