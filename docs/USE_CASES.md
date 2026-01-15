# Allow2 Home Assistant Integration - Use Cases

## Real-World Use Cases with Complete Examples

This document provides practical, copy-paste-ready examples for common parental control scenarios.

## Table of Contents

1. [Gaming Console Control](#1-gaming-console-control)
2. [TV and Media Center Limits](#2-tv-and-media-center-limits)
3. [Computer Access via Smart Plugs](#3-computer-access-via-smart-plugs)
4. [Bedtime Enforcement](#4-bedtime-enforcement)
5. [Homework Time Protection](#5-homework-time-protection)
6. [Multi-Child Management](#6-multi-child-management)
7. [Progressive Warnings](#7-progressive-warnings)
8. [Reward System Integration](#8-reward-system-integration)
9. [Internet Access Control](#9-internet-access-control)
10. [Weekend vs. Weekday Rules](#10-weekend-vs-weekday-rules)

---

## 1. Gaming Console Control

### Scenario
Johnny (age 10) has an Xbox in the living room. You want to:
- Limit gaming to 2 hours per day on weekdays
- Limit gaming to 4 hours per day on weekends
- Warn him when he has 15 minutes remaining
- Automatically turn off Xbox when time is up
- Send notifications to his tablet

### Allow2 Configuration
(Set in Allow2 web portal)
```
Child: Johnny (ID: 12345)
Activity: Gaming
Weekday Quota: 2 hours (7200 seconds)
Weekend Quota: 4 hours (14400 seconds)
```

### Home Assistant Configuration

#### Step 1: Create User Selector Helper

```yaml
# configuration.yaml
input_select:
  xbox_current_user:
    name: Xbox Current User
    options:
      - "Not in use"
      - "Johnny"
      - "Sarah"
      - "Parent"
    initial: "Not in use"
```

#### Step 2: Create Automation

```yaml
# automations.yaml
automation:
  - alias: "Gaming Quota - Xbox - Johnny"
    description: "Enforce Johnny's gaming time limits on Xbox"
    mode: single

    trigger:
      # Check every 5 minutes while Xbox is in use
      - platform: time_pattern
        minutes: "/5"

    condition:
      # Only when Xbox is playing
      - condition: state
        entity_id: media_player.xbox
        state: "playing"
      # Only when Johnny is using it
      - condition: state
        entity_id: input_select.xbox_current_user
        state: "Johnny"

    action:
      # Check quota with Allow2
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "gaming"
          device_id: "xbox_living_room"
        response_variable: quota

      # Warn at 15 minutes remaining
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and
                     quota.remaining_minutes <= 15 and
                     quota.remaining_minutes > 10 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Warning: You have {{ quota.remaining_minutes }} minutes of gaming time left!"
                  title: "Allow2 - Time Running Low"
              - service: tts.google_translate_say
                target:
                  entity_id: media_player.living_room_speaker
                data:
                  message: "Johnny, you have {{ quota.remaining_minutes }} minutes of gaming time remaining."

      # Warn at 5 minutes remaining
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and
                     quota.remaining_minutes <= 5 and
                     quota.remaining_minutes > 0 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "URGENT: Only {{ quota.remaining_minutes }} minutes left. Save your game!"
                  title: "Allow2 - Final Warning"
                  data:
                    ttl: 0
                    priority: high

      # Enforce quota when exhausted
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              # Give grace period to save game
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Gaming time is up! You have 2 minutes to save your game."
                  title: "Allow2 - Time's Up"

              - delay: "00:02:00"

              # Turn off Xbox
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox

              # Final notification
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Xbox has been turned off. Great gaming session!"
                  title: "Allow2"

              # Reset user selector
              - service: input_select.select_option
                target:
                  entity_id: input_select.xbox_current_user
                data:
                  option: "Not in use"

              # Notify parents
              - service: notify.mobile_app_parents
                data:
                  message: "Johnny's gaming quota enforced ({{ quota.reason }}). Xbox turned off."
                  title: "Allow2 - Quota Enforced"
```

#### Step 3: Track Xbox Usage Start

```yaml
automation:
  - alias: "Xbox - Detect User Started Playing"
    description: "Prompt to select user when Xbox starts playing"

    trigger:
      - platform: state
        entity_id: media_player.xbox
        to: "playing"
        from:
          - "idle"
          - "off"
          - "standby"

    condition:
      - condition: state
        entity_id: input_select.xbox_current_user
        state: "Not in use"

    action:
      # Send notification to parents to set user
      - service: notify.mobile_app_parents
        data:
          message: "Xbox started. Who is playing?"
          title: "Allow2 - Select User"
          data:
            actions:
              - action: "XBOX_USER_JOHNNY"
                title: "Johnny"
              - action: "XBOX_USER_SARAH"
                title: "Sarah"
              - action: "XBOX_USER_PARENT"
                title: "Parent (no limit)"

  - alias: "Xbox - Set User from Notification"
    description: "Handle user selection from notification"

    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "XBOX_USER_JOHNNY"
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "XBOX_USER_SARAH"
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "XBOX_USER_PARENT"

    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.xbox_current_user
        data:
          option: >
            {% if trigger.event.data.action == 'XBOX_USER_JOHNNY' %}
              Johnny
            {% elif trigger.event.data.action == 'XBOX_USER_SARAH' %}
              Sarah
            {% else %}
              Parent
            {% endif %}
```

---

## 2. TV and Media Center Limits

### Scenario
Sarah (age 8) watches TV in her bedroom. You want to:
- Limit TV time to 1 hour on school nights
- Limit TV time to 3 hours on weekends
- Block TV during homework time (4pm-6pm on weekdays)
- Warn when time is running low

### Allow2 Configuration
```
Child: Sarah (ID: 67890)
Activity: Television
Weekday Quota: 1 hour (3600 seconds)
Weekend Quota: 3 hours (10800 seconds)
Ban Windows: Mon-Fri 4:00pm-6:00pm (homework time)
```

### Home Assistant Configuration

```yaml
automation:
  - alias: "TV Quota - Sarah's Bedroom TV"
    description: "Enforce Sarah's TV time limits"
    mode: single

    trigger:
      # Check every 3 minutes (more frequent for TV)
      - platform: time_pattern
        minutes: "/3"

    condition:
      # Only when TV is on
      - condition: state
        entity_id: media_player.sarahs_bedroom_tv
        state: "on"

    action:
      - service: allow2.check_quota
        data:
          child_id: 67890
          activity: "television"
          device_id: "sarah_bedroom_tv"
        response_variable: quota

      # Log for debugging
      - service: system_log.write
        data:
          message: >
            Sarah TV quota: allowed={{ quota.allowed }},
            remaining={{ quota.remaining_minutes }}min,
            reason={{ quota.reason }}
          level: debug

      # Warn at 10 minutes
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and quota.remaining_minutes <= 10 }}
            sequence:
              - service: notify.mobile_app_sarahs_tablet
                data:
                  message: "{{ quota.remaining_minutes }} minutes of TV time left!"
                  title: "Allow2 - Time Warning"

      # Enforce quota or ban window
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              # Pause instead of turning off (less jarring)
              - service: media_player.media_pause
                target:
                  entity_id: media_player.sarahs_bedroom_tv

              - delay: "00:00:30"

              # If still on, turn off
              - condition: state
                entity_id: media_player.sarahs_bedroom_tv
                state: "playing"

              - service: media_player.turn_off
                target:
                  entity_id: media_player.sarahs_bedroom_tv

              # Notify with reason
              - service: notify.mobile_app_sarahs_tablet
                data:
                  message: >
                    TV turned off: {{ quota.reason or "Time limit reached" }}
                  title: "Allow2"

  - alias: "TV - Block During Homework Time"
    description: "Prevent TV from turning on during homework time"

    trigger:
      - platform: state
        entity_id: media_player.sarahs_bedroom_tv
        to: "on"

    condition:
      # During homework time (4pm-6pm Mon-Fri)
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
      # Check quota (will return ban window status)
      - service: allow2.check_quota
        data:
          child_id: 67890
          activity: "television"
          device_id: "sarah_bedroom_tv"
        response_variable: quota

      - condition: template
        value_template: "{{ not quota.allowed }}"

      # Turn off immediately
      - service: media_player.turn_off
        target:
          entity_id: media_player.sarahs_bedroom_tv

      # Explain why
      - service: notify.mobile_app_sarahs_tablet
        data:
          message: "It's homework time! TV is not allowed until 6pm."
          title: "Allow2"
```

---

## 3. Computer Access via Smart Plugs

### Scenario
Johnny's desktop computer is plugged into a smart plug. You want to:
- Limit computer time to 3 hours per day
- Prevent computer from being turned on during ban windows
- Warn before cutting power to allow saving work
- Log activity automatically

### Allow2 Configuration
```
Child: Johnny (ID: 12345)
Activity: Internet
Daily Quota: 3 hours (10800 seconds)
Ban Windows: Daily 9:00pm-7:00am (bedtime)
```

### Home Assistant Configuration

```yaml
automation:
  - alias: "Computer Quota - Johnny's Desktop"
    description: "Enforce computer time limits via smart plug"
    mode: single

    trigger:
      - platform: time_pattern
        minutes: "/5"

    condition:
      # Only when computer is on
      - condition: state
        entity_id: switch.johnnys_computer_plug
        state: "on"

    action:
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "internet"
          device_id: "johnny_desktop"
        response_variable: quota

      # Warn at 20 minutes
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and quota.remaining_minutes == 20 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Warning: 20 minutes of computer time left. Save your work!"
                  title: "Allow2"

      # Final warning at 5 minutes
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and quota.remaining_minutes == 5 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "URGENT: 5 minutes left! Computer will shut down soon!"
                  title: "Allow2 - Final Warning"
                  data:
                    ttl: 0
                    priority: high

      # Enforce quota
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              # Give time to save work
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Time is up! You have 3 minutes to save and shut down."
                  title: "Allow2 - Time's Up"

              - delay: "00:03:00"

              # Cut power
              - service: switch.turn_off
                target:
                  entity_id: switch.johnnys_computer_plug

              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Computer has been powered off."
                  title: "Allow2"

  - alias: "Computer - Prevent Startup During Ban Window"
    description: "Block computer from turning on outside allowed hours"

    trigger:
      - platform: state
        entity_id: switch.johnnys_computer_plug
        to: "on"

    action:
      # Check quota (includes ban window check)
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "internet"
          device_id: "johnny_desktop"
        response_variable: quota

      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              # Turn off immediately
              - service: switch.turn_off
                target:
                  entity_id: switch.johnnys_computer_plug

              # Explain why
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: >
                    Computer blocked: {{ quota.reason or "Outside allowed hours" }}
                  title: "Allow2"
```

---

## 4. Bedtime Enforcement

### Scenario
All devices should turn off at bedtime, regardless of quota remaining.

### Allow2 Configuration
```
All Children:
Ban Windows: Daily 9:00pm-7:00am (bedtime)
```

### Home Assistant Configuration

```yaml
automation:
  - alias: "Bedtime - Turn Off All Devices"
    description: "Enforce bedtime by turning off all entertainment devices"

    trigger:
      # 5 minutes before bedtime
      - platform: time
        at: "20:55:00"
      # At bedtime
      - platform: time
        at: "21:00:00"

    action:
      # 5-minute warning
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.at == '20:55:00' }}"
            sequence:
              - service: notify.mobile_app_kids
                data:
                  message: "Bedtime in 5 minutes! Start wrapping up."
                  title: "Allow2 - Bedtime Soon"

              - service: tts.google_translate_say
                target:
                  entity_id:
                    - media_player.johnnys_room_speaker
                    - media_player.sarahs_room_speaker
                data:
                  message: "Bedtime is in 5 minutes. Please finish up and get ready for bed."

      # Bedtime enforcement
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.at == '21:00:00' }}"
            sequence:
              # Turn off all devices
              - service: homeassistant.turn_off
                target:
                  entity_id:
                    - media_player.xbox
                    - media_player.johnnys_bedroom_tv
                    - media_player.sarahs_bedroom_tv
                    - switch.johnnys_computer_plug
                    - switch.sarahs_tablet_charger  # Also cuts power after full charge

              # Notify children
              - service: notify.mobile_app_kids
                data:
                  message: "Bedtime! All devices have been turned off. Good night!"
                  title: "Allow2 - Bedtime"

              # Optional: Dim bedroom lights
              - service: light.turn_on
                target:
                  entity_id:
                    - light.johnnys_room
                    - light.sarahs_room
                data:
                  brightness_pct: 30

  - alias: "Bedtime - Prevent Device Startup"
    description: "Prevent devices from being turned on during bedtime hours"

    trigger:
      - platform: state
        entity_id:
          - media_player.xbox
          - media_player.johnnys_bedroom_tv
          - media_player.sarahs_bedroom_tv
          - switch.johnnys_computer_plug
        to: "on"

    condition:
      # During bedtime (9pm-7am)
      - condition: time
        after: "21:00:00"
        before: "07:00:00"

    action:
      # Turn off immediately
      - service: homeassistant.turn_off
        target:
          entity_id: "{{ trigger.entity_id }}"

      # Scold gently
      - service: notify.mobile_app_kids
        data:
          message: "It's bedtime! {{ trigger.to_state.name }} has been turned off."
          title: "Allow2"
```

---

## 5. Homework Time Protection

### Scenario
During homework hours (4pm-6pm weekdays), all entertainment devices should be off.

### Home Assistant Configuration

```yaml
automation:
  - alias: "Homework Time - Block Entertainment"
    description: "Turn off and block entertainment during homework hours"

    trigger:
      # Start of homework time
      - platform: time
        at: "16:00:00"
      # During homework time (check every 10 minutes)
      - platform: time_pattern
        minutes: "/10"

    condition:
      # Only on weekdays
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
      # Only during homework hours
      - condition: time
        after: "16:00:00"
        before: "18:00:00"

    action:
      # Turn off all entertainment devices
      - service: homeassistant.turn_off
        target:
          entity_id:
            - media_player.xbox
            - media_player.playstation
            - media_player.living_room_tv
            - media_player.johnnys_bedroom_tv

      # Notify children
      - service: notify.mobile_app_kids
        data:
          message: "It's homework time! Entertainment devices have been turned off until 6pm."
          title: "Allow2 - Homework Time"

  - alias: "Homework Time - Prevent Device Startup"
    description: "Block devices from turning on during homework hours"

    trigger:
      - platform: state
        entity_id:
          - media_player.xbox
          - media_player.playstation
          - media_player.living_room_tv
        to:
          - "on"
          - "playing"

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
          entity_id: "{{ trigger.entity_id }}"

      - service: notify.mobile_app_kids
        data:
          message: "Homework time! {{ trigger.to_state.attributes.friendly_name }} blocked until 6pm."
          title: "Allow2"

  - alias: "Homework Time - End Announcement"
    description: "Announce when homework time is over"

    trigger:
      - platform: time
        at: "18:00:00"

    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri

    action:
      - service: notify.mobile_app_kids
        data:
          message: "Homework time is over! Entertainment devices are now available (within your daily limits)."
          title: "Allow2"

      - service: tts.google_translate_say
        target:
          entity_id: media_player.living_room_speaker
        data:
          message: "Homework time is over. You can now use your devices within your daily time limits."
```

---

## 6. Multi-Child Management

### Scenario
Johnny and Sarah share the living room TV and Xbox. Track each child's usage separately.

### Home Assistant Configuration

```yaml
# Create user selectors for each device
input_select:
  living_room_tv_user:
    name: Living Room TV User
    options:
      - "Not in use"
      - "Johnny (12345)"
      - "Sarah (67890)"
      - "Parent"
    initial: "Not in use"

  xbox_user:
    name: Xbox User
    options:
      - "Not in use"
      - "Johnny (12345)"
      - "Sarah (67890)"
      - "Parent"
    initial: "Not in use"

automation:
  - alias: "Multi-Child - TV Quota Enforcement"
    description: "Enforce quotas for whichever child is using TV"
    mode: single

    trigger:
      - platform: time_pattern
        minutes: "/5"

    condition:
      # TV is on
      - condition: state
        entity_id: media_player.living_room_tv
        state: "on"
      # A child is selected (not parent or not in use)
      - condition: template
        value_template: >
          {{ not is_state('input_select.living_room_tv_user', 'Not in use') and
             not is_state('input_select.living_room_tv_user', 'Parent') }}

    action:
      # Extract child ID from selection
      - variables:
          child_id_str: >
            {{ states('input_select.living_room_tv_user') }}
          child_id: >
            {{ child_id_str.split('(')[1].split(')')[0] | int }}
          child_name: >
            {{ child_id_str.split(' (')[0] }}

      # Check quota for selected child
      - service: allow2.check_quota
        data:
          child_id: "{{ child_id }}"
          activity: "television"
          device_id: "living_room_tv"
        response_variable: quota

      # Warn at 10 minutes
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and quota.remaining_minutes <= 10 }}
            sequence:
              - service: notify.mobile_app_kids
                data:
                  message: "{{ child_name }}: {{ quota.remaining_minutes }} minutes of TV time left!"
                  title: "Allow2"

      # Enforce quota
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              - service: media_player.turn_off
                target:
                  entity_id: media_player.living_room_tv

              - service: notify.mobile_app_kids
                data:
                  message: "{{ child_name }}'s TV time is up!"
                  title: "Allow2"

              - service: input_select.select_option
                target:
                  entity_id: input_select.living_room_tv_user
                data:
                  option: "Not in use"

  - alias: "Multi-Child - Prompt User Selection"
    description: "Ask who is using device when it turns on"

    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
        to: "on"

    condition:
      - condition: state
        entity_id: input_select.living_room_tv_user
        state: "Not in use"

    action:
      - service: notify.mobile_app_parents
        data:
          message: "Living room TV turned on. Who is watching?"
          title: "Allow2 - Select User"
          data:
            actions:
              - action: "TV_USER_JOHNNY"
                title: "Johnny"
              - action: "TV_USER_SARAH"
                title: "Sarah"
              - action: "TV_USER_PARENT"
                title: "Parent"

  - alias: "Multi-Child - Handle User Selection"
    description: "Set user based on notification action"

    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "TV_USER_JOHNNY"
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "TV_USER_SARAH"
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "TV_USER_PARENT"

    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.living_room_tv_user
        data:
          option: >
            {% if trigger.event.data.action == 'TV_USER_JOHNNY' %}
              Johnny (12345)
            {% elif trigger.event.data.action == 'TV_USER_SARAH' %}
              Sarah (67890)
            {% else %}
              Parent
            {% endif %}
```

---

## 7. Progressive Warnings

### Scenario
Give multiple warnings as time runs out, with increasing urgency.

### Home Assistant Configuration

```yaml
automation:
  - alias: "Progressive Warnings - Gaming"
    description: "Multiple warnings with increasing urgency"
    mode: single

    trigger:
      - platform: time_pattern
        minutes: "/1"  # Check every minute for precise warnings

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
        response_variable: quota

      # 30-minute warning (informational)
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and
                     quota.remaining_minutes <= 30 and
                     quota.remaining_minutes > 29 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "You have 30 minutes of gaming time left today."
                  title: "Allow2"

      # 15-minute warning (caution)
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and
                     quota.remaining_minutes <= 15 and
                     quota.remaining_minutes > 14 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Warning: 15 minutes of gaming time remaining."
                  title: "Allow2 - Time Warning"
                  data:
                    priority: default

              - service: tts.google_translate_say
                target:
                  entity_id: media_player.living_room_speaker
                data:
                  message: "15 minutes of gaming time remaining."

      # 5-minute warning (urgent)
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and
                     quota.remaining_minutes <= 5 and
                     quota.remaining_minutes > 4 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "URGENT: Only 5 minutes left! Save your game NOW!"
                  title: "Allow2 - Final Warning"
                  data:
                    priority: high
                    ttl: 0

              - service: tts.google_translate_say
                target:
                  entity_id: media_player.living_room_speaker
                data:
                  message: "Attention! You have 5 minutes to save your game and finish up."

      # 1-minute warning (critical)
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and
                     quota.remaining_minutes <= 1 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "CRITICAL: Less than 1 minute! Save immediately!"
                  title: "Allow2 - LAST WARNING"
                  data:
                    priority: high
                    ttl: 0
                    channel: alarm_stream

              - service: tts.google_translate_say
                target:
                  entity_id: media_player.living_room_speaker
                data:
                  message: "Critical warning! Less than one minute remaining. The Xbox will turn off shortly."

      # Enforce quota
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox

              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Time's up! Xbox has been turned off."
                  title: "Allow2"
```

---

## 8. Reward System Integration

### Scenario
Grant bonus time for completing chores or good behavior.

**Note**: This requires manual quota adjustment in Allow2 web portal. The integration can't directly modify quotas, but can provide UI for parents.

### Home Assistant Configuration

```yaml
# Create script for parents to grant bonus time
script:
  grant_bonus_time:
    fields:
      child_name:
        description: "Child's name"
        example: "Johnny"
      activity:
        description: "Activity type"
        example: "gaming"
      bonus_minutes:
        description: "Minutes to grant"
        example: 30
    sequence:
      - service: notify.mobile_app_parents
        data:
          message: >
            Grant {{ bonus_minutes }} minutes of {{ activity }} to {{ child_name }}?
            You must do this manually in the Allow2 app.
          title: "Allow2 - Bonus Time Request"
          data:
            actions:
              - action: "OPEN_ALLOW2_APP"
                title: "Open Allow2"

      - service: persistent_notification.create
        data:
          title: "Grant Bonus Time"
          message: >
            To grant {{ bonus_minutes }} minutes of {{ activity }} to {{ child_name }}:
            1. Open Allow2 app
            2. Select {{ child_name }}
            3. Tap "Grant Bonus Time"
            4. Enter {{ bonus_minutes }} minutes
          notification_id: "bonus_time_reminder"

# Chore completion tracking
input_boolean:
  johnny_chores_done:
    name: Johnny Chores Done Today
    initial: off

automation:
  - alias: "Reward - Chores Completed Notification"
    description: "Notify parent when child completes chores"

    trigger:
      - platform: state
        entity_id: input_boolean.johnny_chores_done
        to: "on"

    action:
      - service: notify.mobile_app_parents
        data:
          message: "Johnny marked his chores as complete. Grant bonus gaming time?"
          title: "Allow2 - Chore Completion"
          data:
            actions:
              - action: "GRANT_BONUS_30"
                title: "Grant 30 min"
              - action: "GRANT_BONUS_60"
                title: "Grant 60 min"
              - action: "DENY_BONUS"
                title: "Deny"

  - alias: "Reward - Handle Bonus Decision"
    description: "Process parent's decision on bonus time"

    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "GRANT_BONUS_30"
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "GRANT_BONUS_60"
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "DENY_BONUS"

    action:
      - choose:
          # Grant 30 minutes
          - conditions:
              - condition: template
                value_template: >
                  {{ trigger.event.data.action == 'GRANT_BONUS_30' }}
            sequence:
              - service: script.grant_bonus_time
                data:
                  child_name: "Johnny"
                  activity: "gaming"
                  bonus_minutes: 30

              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Great job on your chores! You earned 30 bonus minutes of gaming time!"
                  title: "Allow2 - Bonus Time!"

          # Grant 60 minutes
          - conditions:
              - condition: template
                value_template: >
                  {{ trigger.event.data.action == 'GRANT_BONUS_60' }}
            sequence:
              - service: script.grant_bonus_time
                data:
                  child_name: "Johnny"
                  activity: "gaming"
                  bonus_minutes: 60

              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Excellent work! You earned 1 hour of bonus gaming time!"
                  title: "Allow2 - Bonus Time!"

          # Deny bonus
          - conditions:
              - condition: template
                value_template: >
                  {{ trigger.event.data.action == 'DENY_BONUS' }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Your chores were approved, but no bonus time granted today."
                  title: "Allow2"

  - alias: "Reward - Reset Chore Tracking Daily"
    description: "Reset chore completion at midnight"

    trigger:
      - platform: time
        at: "00:00:00"

    action:
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.johnny_chores_done
```

---

## 9. Internet Access Control

### Scenario
Control internet access by managing router or WiFi access point.

**Prerequisites**:
- Router/AP integration in Home Assistant (e.g., UniFi, pfSense, OpenWRT)
- Ability to enable/disable device network access

### Home Assistant Configuration

```yaml
automation:
  - alias: "Internet Quota - Johnny's Devices"
    description: "Enforce internet quota by controlling network access"
    mode: single

    trigger:
      - platform: time_pattern
        minutes: "/5"

    condition:
      # Check if any of Johnny's devices are online
      - condition: or
        conditions:
          - condition: state
            entity_id: device_tracker.johnnys_laptop
            state: "home"
          - condition: state
            entity_id: device_tracker.johnnys_tablet
            state: "home"

    action:
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "internet"
          device_id: "johnnys_devices"
        response_variable: quota

      # Warn at 15 minutes
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ quota.allowed and quota.remaining_minutes <= 15 }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Warning: {{ quota.remaining_minutes }} minutes of internet time left!"
                  title: "Allow2"

      # Enforce quota by blocking internet
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              # UniFi example: Block devices
              - service: unifi.block_client
                data:
                  mac_address:
                    - "AA:BB:CC:DD:EE:FF"  # Johnny's laptop
                    - "11:22:33:44:55:66"  # Johnny's tablet

              # pfSense example: Enable firewall rule blocking Johnny's IPs
              # - service: pfsense.enable_rule
              #   data:
              #     rule_id: "block_johnny"

              # Notify
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Internet time is up! Network access has been disabled."
                  title: "Allow2"

              - service: notify.mobile_app_parents
                data:
                  message: "Johnny's internet quota enforced. Devices blocked."
                  title: "Allow2"

  - alias: "Internet Quota - Restore Access"
    description: "Re-enable internet access when new day starts or quota resets"

    trigger:
      # Check at midnight (quota may reset)
      - platform: time
        at: "00:00:00"

    action:
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "internet"
          device_id: "johnnys_devices"
        response_variable: quota

      - choose:
          - conditions:
              - condition: template
                value_template: "{{ quota.allowed }}"
            sequence:
              # UniFi: Unblock devices
              - service: unifi.unblock_client
                data:
                  mac_address:
                    - "AA:BB:CC:DD:EE:FF"
                    - "11:22:33:44:55:66"

              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Good morning! Internet access has been restored. You have {{ quota.remaining_minutes }} minutes today."
                  title: "Allow2"
```

---

## 10. Weekend vs. Weekday Rules

### Scenario
Different quotas for weekdays vs. weekends, configured in Allow2.

**Allow2 handles this automatically** - just configure different weekday/weekend quotas in the Allow2 web portal. Your Home Assistant automations don't need to change.

### Allow2 Configuration
```
Child: Johnny
Activity: Gaming

Weekday (Mon-Fri):
  Daily Quota: 2 hours
  Ban Window: 4pm-6pm (homework)

Weekend (Sat-Sun):
  Daily Quota: 4 hours
  No ban windows
```

### Home Assistant Configuration

```yaml
# Single automation works for both weekdays and weekends
# Allow2 API returns correct quota based on current day
automation:
  - alias: "Gaming Quota - Handles Weekdays and Weekends"
    description: "Allow2 automatically handles different quotas"

    trigger:
      - platform: time_pattern
        minutes: "/5"

    condition:
      - condition: state
        entity_id: media_player.xbox
        state: "playing"

    action:
      # Allow2 returns correct quota for current day
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "gaming"
          device_id: "xbox"
        response_variable: quota

      # Log quota for debugging
      - service: system_log.write
        data:
          message: >
            {% set day = now().strftime('%A') %}
            {{ day }}: Johnny has {{ quota.remaining_minutes }} minutes left
          level: debug

      # Standard enforcement (same for all days)
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ not quota.allowed }}"
            sequence:
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox

  # Optional: Show different messages for weekdays vs weekends
  - alias: "Quota Notification - Day-Specific Messages"
    description: "Customize notifications based on day of week"

    trigger:
      - platform: state
        entity_id: media_player.xbox
        to: "playing"

    action:
      - service: allow2.check_quota
        data:
          child_id: 12345
          activity: "gaming"
          device_id: "xbox"
        response_variable: quota

      - service: notify.mobile_app_johnnys_tablet
        data:
          message: >
            {% if now().weekday() < 5 %}
              You have {{ quota.remaining_minutes }} minutes of gaming time today (weekday limit).
            {% else %}
              You have {{ quota.remaining_minutes }} minutes of gaming time today (weekend limit).
            {% endif %}
          title: "Allow2"
```

---

## Troubleshooting Common Issues

### Issue: Automation Not Triggering

**Check**:
1. Device state is correct (`playing`, `on`, etc.)
2. Time pattern is firing (check automation traces)
3. Conditions are being met

**Debug**:
```yaml
# Add logging to see what's happening
- service: system_log.write
  data:
    message: >
      Automation triggered:
      Device={{ states('media_player.xbox') }},
      User={{ states('input_select.xbox_current_user') }}
    level: info
```

### Issue: Quota Always Shows "Allowed"

**Check**:
1. Child ID is correct
2. Activity name matches Allow2 configuration (lowercase)
3. Quota is actually set in Allow2 web portal

**Debug**:
```yaml
- service: persistent_notification.create
  data:
    title: "Quota Debug"
    message: >
      Child: {{ child_id }}
      Activity: {{ activity }}
      Allowed: {{ quota.allowed }}
      Remaining: {{ quota.remaining_minutes }}
      Reason: {{ quota.reason }}
```

### Issue: Device Not Turning Off

**Check**:
1. Device actually supports `turn_off` service
2. Device is reachable by Home Assistant
3. No conflicting automations keeping device on

**Test Manually**:
```yaml
# Developer Tools → Services
service: media_player.turn_off
target:
  entity_id: media_player.xbox
```

---

## Advanced Patterns

### Pattern: Shared Usage Logging

Log activity for multiple users sharing one device:

```yaml
automation:
  - alias: "Shared TV - Log Usage for All Users"
    description: "Track which child uses TV and for how long"

    trigger:
      - platform: state
        entity_id: input_select.living_room_tv_user

    condition:
      # User changed from one child to another or to "Not in use"
      - condition: template
        value_template: >
          {{ trigger.from_state.state != trigger.to_state.state }}

    action:
      # Calculate usage duration
      - variables:
          duration_seconds: >
            {{ (now() - trigger.from_state.last_changed).total_seconds() | int }}

      # Log usage for previous user (if was a child)
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ trigger.from_state.state not in ['Not in use', 'Parent'] }}
            sequence:
              - variables:
                  prev_child_id: >
                    {{ trigger.from_state.state.split('(')[1].split(')')[0] | int }}

              - service: allow2.log_activity
                data:
                  child_id: "{{ prev_child_id }}"
                  activity: "television"
                  device_id: "living_room_tv"
                  duration: "{{ duration_seconds }}"
```

### Pattern: Contextual Enforcement

Different enforcement strategies based on context:

```yaml
automation:
  - alias: "Contextual Enforcement - Gaming"
    description: "Different actions based on why quota exhausted"

    trigger:
      - platform: time_pattern
        minutes: "/5"

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
        response_variable: quota

      - choose:
          # Daily quota exhausted
          - conditions:
              - condition: template
                value_template: >
                  {{ not quota.allowed and
                     quota.reason == 'daily quota exhausted' }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "You've used all your gaming time for today. Great gaming!"
                  title: "Allow2 - Daily Limit"
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox

          # Ban window active (e.g., homework time)
          - conditions:
              - condition: template
                value_template: >
                  {{ not quota.allowed and
                     'ban window' in (quota.reason or '') }}
            sequence:
              - service: notify.mobile_app_johnnys_tablet
                data:
                  message: "Gaming is blocked during this time. Xbox has been turned off."
                  title: "Allow2 - Restricted Time"
              - service: media_player.turn_off
                target:
                  entity_id: media_player.xbox
              # Don't send parent notification for ban window (expected)

          # Account issue (unusual)
          - conditions:
              - condition: template
                value_template: >
                  {{ not quota.allowed }}
            sequence:
              - service: notify.mobile_app_parents
                data:
                  message: "Allow2 quota check failed: {{ quota.reason }}"
                  title: "Allow2 - Issue"
              # Don't turn off device in case of errors
```

---

## Next Steps

- Review [API Integration](API_INTEGRATION.md) for technical details
- Check [Configuration Guide](CONFIGURATION.md) for advanced options
- See [Architecture](ARCHITECTURE.md) for system design

For support, visit the GitHub repository or Home Assistant forums.
