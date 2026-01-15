# Allow2 Home Assistant Integration - Configuration Guide

## Overview

The **allow2homeassistant** integration is configured primarily through Home Assistant's Configuration Flow UI. This guide covers initial setup, service usage, and advanced configuration options.

## Initial Setup

### Getting an Allow2 API Key

Before configuring the integration, obtain your API key from Allow2:

1. **Log in to Allow2**
   - Visit https://allow2.com
   - Sign in with your parent account

2. **Navigate to API Settings**
   - Click your profile icon (top right)
   - Select **Settings**
   - Choose **API Access** or **Developer** section

3. **Generate API Key**
   - Click **Generate New API Key**
   - Give it a descriptive name: "Home Assistant"
   - Click **Create**
   - **IMPORTANT**: Copy the key immediately (you won't see it again!)
   - Example key: `ak_1234567890abcdef1234567890abcdef`

4. **Save Key Securely**
   - Store in password manager
   - You'll enter it in Home Assistant's config flow

### Configuration Flow Setup

1. **Add Integration**
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**
   - Search for "Allow2"
   - Click **Allow2 Parental Controls**

2. **Enter Configuration**

   **API Key** (Required):
   ```
   ak_1234567890abcdef1234567890abcdef
   ```

   **Update Interval** (Optional, default: 30 minutes):
   - How often to refresh child list from Allow2
   - Range: 15-120 minutes
   - Recommendation: 30 minutes (default)
   ```
   30
   ```

   **Cache Duration** (Optional, default: 5 minutes):
   - How long to cache quota responses locally
   - Range: 1-60 minutes
   - Recommendation: 5 minutes for active enforcement
   ```
   5
   ```

3. **Validate**
   - Integration tests connection to Allow2 API
   - Fetches list of children
   - Shows success or error message

4. **Complete**
   - Click **Finish**
   - Integration is now active

## Service Configuration

### Available Services

The integration provides two main services:

#### 1. `allow2.check_quota`

Check if a child has quota remaining for an activity.

**Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `child_id` | integer | Yes | Child's Allow2 ID | `12345` |
| `activity` | string | Yes | Activity type | `"gaming"` |
| `device_id` | string | No | Device identifier | `"xbox"` |

**Activity Types**:
- `"gaming"` - Video games
- `"internet"` - General internet/computer use
- `"television"` - TV watching
- `"social"` - Social media
- `"school"` - Educational activities
- `"custom"` - Custom activity defined in Allow2

**Response Structure**:
```yaml
allowed: true  # or false
remaining_minutes: 45
reason: null  # Or explanation if not allowed
activities:
  gaming:
    remaining: 2700  # seconds
    daily_quota: 7200
    used: 4500
```

**Example Usage**:
```yaml
service: allow2.check_quota
data:
  child_id: 12345
  activity: "gaming"
  device_id: "xbox_living_room"
response_variable: quota_response
```

#### 2. `allow2.log_activity`

Manually log activity time to Allow2.

**Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `child_id` | integer | Yes | Child's Allow2 ID | `12345` |
| `activity` | string | Yes | Activity type | `"gaming"` |
| `device_id` | string | No | Device identifier | `"xbox"` |
| `duration` | integer | Yes | Seconds of usage | `300` |

**Example Usage**:
```yaml
service: allow2.log_activity
data:
  child_id: 12345
  activity: "television"
  device_id: "living_room_tv"
  duration: 1800  # 30 minutes
```

**When to Use**:
- Usually **not needed** - quota checking automatically logs usage
- Manual logging for offline activities
- Bulk logging after periods without connectivity

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

**Option 1: Input Select Helper**

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

**Use in Automations**:
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
   - Allow2: "Screen Time" → HA: `"screen time"` or `"screen_time"`

### Activity to Device Mapping

Map your Home Assistant devices to activity types:

```yaml
# Example mapping (not actual configuration)
Devices → Activities:
  media_player.xbox → "gaming"
  media_player.playstation → "gaming"
  media_player.living_room_tv → "television"
  switch.computer_plug → "internet"
  media_player.youtube_tv → "television"
  media_player.netflix → "television"
```

**Implementation in Automations**:

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

## Device Configuration

### Identifying Controllable Devices

The integration can enforce quotas on any Home Assistant entity that can be turned off:

**Media Players**:
```yaml
media_player.xbox
media_player.playstation
media_player.apple_tv
media_player.chromecast
media_player.plex
```

**Switches**:
```yaml
switch.computer_smart_plug
switch.tv_power
switch.gaming_console_outlet
```

**Lights** (for room-based control):
```yaml
light.bedroom  # Turn off bedroom lights to signal bedtime
```

**Covers** (creative uses):
```yaml
cover.bedroom_blinds  # Close blinds during "no screen time" periods
```

### Device Control Methods

**Method 1: Turn Off Service**
```yaml
service: homeassistant.turn_off
target:
  entity_id: media_player.xbox
```

**Method 2: Specific Service**
```yaml
service: media_player.turn_off
target:
  entity_id: media_player.xbox
```

**Method 3: Media Player Pause** (less disruptive):
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

## Automation Configuration

### Basic Automation Pattern

Standard automation structure for quota enforcement:

```yaml
automation:
  - alias: "Enforce [Device] Quota for [Child]"
    description: "Check quota and turn off device when exhausted"

    # When to check
    trigger:
      - platform: time_pattern
        minutes: "/5"  # Every 5 minutes

    # Only check when device is in use
    condition:
      - condition: state
        entity_id: [device_entity]
        state: [active_state]  # "playing", "on", etc.

    # Check quota and enforce
    action:
      - service: allow2.check_quota
        data:
          child_id: [child_id]
          activity: "[activity_type]"
          device_id: "[device_name]"
        response_variable: quota

      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              # Turn off device
              - service: homeassistant.turn_off
                target:
                  entity_id: [device_entity]

              # Notify child
              - service: notify.mobile_app_[device]
                data:
                  message: "Time's up! [Device] has been turned off."
                  title: "Allow2 Parental Controls"
```

### Example: Complete Xbox Automation

```yaml
automation:
  - alias: "Enforce Xbox Quota for Johnny"
    description: "Monitor Johnny's gaming time and enforce limits"
    mode: single

    trigger:
      # Check every 5 minutes
      - platform: time_pattern
        minutes: "/5"

    condition:
      # Only when Xbox is playing
      - condition: state
        entity_id: media_player.xbox
        state: "playing"

      # Only when Johnny is the current user
      - condition: state
        entity_id: input_select.xbox_current_user
        state: "Johnny (12345)"

    action:
      # Check quota
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "gaming"
          device_id: "xbox_living_room"
        response_variable: quota

      # Log remaining time (optional, for debugging)
      - service: system_log.write
        data:
          message: >
            Johnny has {{ quota.remaining_minutes }} minutes of gaming left
          level: info

      # Warn when 10 minutes remain
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and quota.remaining_minutes <= 10 }}
            sequence:
              - service: notify.mobile_app_johnnys_phone
                data:
                  message: "Warning: Only {{ quota.remaining_minutes }} minutes of gaming time left!"
                  title: "Allow2 - Time Running Low"

      # Enforce quota
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              # Turn off Xbox
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox

              # Send notification
              - service: notify.mobile_app_johnnys_phone
                data:
                  message: "Gaming time is up! Xbox has been turned off."
                  title: "Allow2 Parental Controls"

              # Reset user selection
              - service: input_select.select_option
                target:
                  entity_id: input_select.xbox_current_user
                data:
                  option: "Not in use"

              # Optional: Send notification to parent
              - service: notify.mobile_app_dads_phone
                data:
                  message: "Johnny's gaming quota exhausted. Xbox turned off."
                  title: "Allow2 - Quota Enforced"
```

## Advanced Configuration

### YAML Configuration (Advanced)

While the integration is configured via UI, some advanced options can be set in `configuration.yaml`:

```yaml
# configuration.yaml
allow2:
  # These override config flow settings
  cache_duration: 300  # 5 minutes (seconds)
  update_interval: 1800  # 30 minutes (seconds)

  # Advanced settings
  api_timeout: 10  # API request timeout (seconds)
  max_retries: 3  # Number of retry attempts
  retry_delay: 5  # Delay between retries (seconds)

  # Fail-safe mode
  fail_open: true  # Allow usage if API unavailable (default: true)
```

**fail_open Explanation**:
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
2. Find **Allow2 Parental Controls**
3. Click **⋮** menu
4. Select **Reload**

This reloads:
- API connection
- Child list
- Cached data

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

### Shared vs. Personal Devices

**Personal Devices** (one child per device):
- Use fixed child_id in automation
- Simpler automation logic
- Example: Johnny's tablet, Sarah's laptop

**Shared Devices** (multiple children use same device):
- Use input_select helper to track current user
- More complex automation logic
- Example: Family Xbox, living room TV

## Notification Configuration

### Setting Up Notifications

**Mobile App Notifications** (recommended):

1. **Install Home Assistant Companion App** on child's device
2. **Configure in Home Assistant**:
   ```yaml
   # Automatically configured by app
   notify:
     - name: johnnys_phone
       platform: mobile_app
       # ...
   ```

3. **Use in Automations**:
   ```yaml
   service: notify.mobile_app_johnnys_phone
   data:
     message: "Gaming time is up!"
     title: "Allow2"
   ```

**Alternative Notification Methods**:
- **TTS (Text-to-Speech)**: Announce through smart speakers
- **Persistent Notifications**: Show in HA interface
- **Email**: Send email to child/parent
- **SMS**: Send SMS via Twilio integration

### Notification Best Practices

1. **Warning Before Cutoff**:
   ```yaml
   # Warn at 10 minutes remaining
   - condition: template
     value_template: "{{ quota.remaining_minutes <= 10 and quota.remaining_minutes > 5 }}"
   - service: notify.mobile_app
     data:
       message: "Warning: {{ quota.remaining_minutes }} minutes left!"
   ```

2. **Grace Period**:
   ```yaml
   # Give 2 minutes to save game
   - service: notify.mobile_app
     data:
       message: "Time is up. You have 2 minutes to save your game."
   - delay: "00:02:00"
   - service: media_player.turn_off
   ```

3. **Parent Notifications**:
   ```yaml
   # Notify parent when quota enforced
   - service: notify.mobile_app_parent
     data:
       message: "Johnny's gaming quota enforced. Xbox turned off."
   ```

## Reconfiguration

### Changing API Key

To update the Allow2 API key:

1. Go to **Settings** → **Devices & Services**
2. Find **Allow2 Parental Controls**
3. Click **Configure**
4. Enter new API key
5. Click **Submit**

### Adjusting Settings

To change update interval or cache duration:

1. Follow same steps as changing API key
2. Modify desired settings
3. Click **Submit**
4. Settings take effect immediately

## Next Steps

Now that configuration is complete:

1. **Create Automations**: See [Use Cases](USE_CASES.md) for examples
2. **Test Thoroughly**: Verify quota checking works
3. **Monitor Performance**: Check logs for errors
4. **Adjust as Needed**: Fine-tune check intervals and notifications

For technical details about API communication, see [API Integration](API_INTEGRATION.md).
