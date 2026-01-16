# Allow2 Home Assistant Integration - Installation Guide

## Prerequisites

Before installing **allow2homeassistant**, ensure you have:

1. **Home Assistant** installed and running
   - Version 2023.1 or newer
   - Accessible via web interface

2. **Allow2 Parent Account**
   - Sign up at https://allow2.com
   - Set up at least one child profile
   - Configure quotas and activities
   - Know your login credentials (email and password)

3. **(Optional) HACS Installed**
   - For easier installation and updates
   - Install from https://hacs.xyz

## Installation Methods

### Method 1: HACS Installation (Recommended)

HACS (Home Assistant Community Store) provides the easiest installation and update process.

#### Step 1: Add Custom Repository

1. Open Home Assistant
2. Go to **HACS** → **Integrations**
3. Click the **⋮** menu (three dots) in the top right
4. Select **Custom repositories**
5. Add repository URL:
   ```
   https://github.com/allow2/allow2homeassistant
   ```
6. Select category: **Integration**
7. Click **Add**

#### Step 2: Install Integration

1. In HACS, search for **"Allow2"**
2. Click **Allow2 Parental Controls**
3. Click **Download**
4. Select the latest version
5. Wait for download to complete

#### Step 3: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart**
3. Wait for Home Assistant to restart (1-2 minutes)

#### Step 4: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"Allow2"**
4. Click **Allow2 Parental Controls**
5. Follow configuration steps (see Configuration section below)

### Method 2: Manual Installation

For users without HACS or who prefer manual installation.

#### Step 1: Download Integration

**Option A: Download Release**
1. Visit https://github.com/allow2/allow2homeassistant/releases
2. Download the latest `allow2.zip` file
3. Extract the ZIP file

**Option B: Clone Repository**
```bash
cd /tmp
git clone https://github.com/allow2/allow2homeassistant.git
cd allow2homeassistant
```

#### Step 2: Copy Files to Home Assistant

**Linux/Docker**:
```bash
# Find your Home Assistant config directory
# Usually /config or ~/.homeassistant

# Copy integration files
cp -r custom_components/allow2 /config/custom_components/

# Verify files exist
ls /config/custom_components/allow2/
# Should show: __init__.py, manifest.json, config_flow.py, etc.
```

**Windows**:
```powershell
# Navigate to Home Assistant config directory
cd C:\Users\YourUser\AppData\Roaming\.homeassistant

# Create custom_components directory if it doesn't exist
mkdir custom_components

# Copy allow2 folder to custom_components
Copy-Item -Recurse -Path "C:\Downloads\allow2" -Destination "custom_components\"
```

**Home Assistant OS**:
1. Use **Samba share** or **File Editor** add-on
2. Navigate to `/config/custom_components/`
3. Create `allow2` folder
4. Upload all files from the integration

#### Step 3: Verify Installation

Check that files are in the correct location:
```
/config/
└── custom_components/
    └── allow2/
        ├── __init__.py
        ├── manifest.json
        ├── config_flow.py
        ├── const.py
        ├── api.py
        ├── coordinator.py
        ├── services.py
        ├── strings.json
        └── translations/
            └── en.json
```

#### Step 4: Restart Home Assistant

Follow same steps as HACS installation (Settings → System → Restart).

#### Step 5: Add Integration

Follow same steps as HACS installation (Settings → Devices & Services → Add Integration).

## Configuration

### Step 1: Start Configuration Flow

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"Allow2"**
4. Click **Allow2 Parental Controls**

### Step 2: Enter Credentials

The configuration UI will prompt for:

**Required:**
- **Email**: Your Allow2 parent account email address
- **Password**: Your Allow2 account password

**Optional:**
- **Device Token**: Override the default device token (advanced users only)
  - Default: `mtG8xbFR1cuJkuXn`
- **Device Name**: How this Home Assistant instance appears in your Allow2 account
  - Default: `Home Assistant`

Example configuration:
```
Email: parent@example.com
Password: ********
Device Name: Home Assistant (leave default)
```

> **Note:** Your email and password are only used during the initial pairing process. They are NOT stored after pairing is complete. Only the pairing tokens are retained.

### Step 3: Device Pairing

The integration will:
1. Connect to Allow2 API using your credentials
2. Pair this Home Assistant instance as a device to your account
3. Retrieve your list of children
4. Store the pairing tokens securely
5. Display success message

If pairing fails, check:
- Email and password are correct
- Internet connection is working
- Allow2 service is available (status.allow2.com)

### Step 4: Integration Added

Once validated, you'll see:
```
✓ Allow2 Parental Controls
  Configured via Configuration Flow
  2 children found
```

## Verify Installation

### Check Integration Status

1. Go to **Settings** → **Devices & Services**
2. Find **Allow2 Parental Controls**
3. Click on it to see details:
   - API connection status
   - Number of children
   - Last update time

### Test Service

Open **Developer Tools** → **Services**:

```yaml
service: allow2.check_quota
data:
  child_id: 12345  # Replace with your child's ID
  activity: "gaming"
  device_id: "test"
```

Click **Call Service**. You should see a response like:
```yaml
allowed: true
remaining_minutes: 120
activities:
  gaming:
    remaining: 7200
```

### Check Logs

Go to **Settings** → **System** → **Logs**

Search for "allow2". You should see:
```
[custom_components.allow2] Allow2 integration initialized
[custom_components.allow2] Connected to Allow2 API successfully
[custom_components.allow2] Found 2 children
```

No errors should be present.

## Getting Child IDs

You need child IDs to use the integration. There are two ways to get them:

### Method 1: From Allow2 Web Portal

1. Log in to https://allow2.com
2. Go to **Children** section
3. Click on a child's profile
4. Look for **Child ID** in profile details (e.g., "12345")

### Method 2: From Home Assistant Logs

After adding the integration:

1. Go to **Settings** → **System** → **Logs**
2. Search for "allow2"
3. Look for log entry:
   ```
   [allow2] Found children: [{'id': 12345, 'name': 'Johnny'}, {'id': 67890, 'name': 'Sarah'}]
   ```

Keep these IDs handy - you'll need them for automations.

## Updating the Integration

### HACS Updates

HACS will notify you when updates are available:

1. Go to **HACS** → **Integrations**
2. Look for **Allow2 Parental Controls** with update badge
3. Click **Update**
4. Restart Home Assistant

### Manual Updates

1. Download new version from GitHub releases
2. Overwrite files in `/config/custom_components/allow2/`
3. Restart Home Assistant
4. Check logs for successful update

## Troubleshooting

### Integration Not Found After Installation

**Problem**: Can't find "Allow2" when adding integration.

**Solutions**:
1. Verify files are in `/config/custom_components/allow2/`
2. Check file permissions (should be readable by Home Assistant)
3. Restart Home Assistant again
4. Clear browser cache and refresh
5. Check logs for loading errors

### Invalid Credentials

**Problem**: "Invalid credentials" or "auth_failed" error during setup.

**Solutions**:
1. Verify email and password are correct
2. Check for extra spaces or characters
3. Try logging in to https://allow2.com to verify credentials work
4. Reset password if forgotten
5. Verify Allow2 account is active

### Connection Timeout

**Problem**: "Could not connect to Allow2 API" error.

**Solutions**:
1. Check internet connection
2. Verify Home Assistant can reach external sites
3. Check firewall rules
4. Try again later (may be temporary service issue)
5. Check Allow2 service status at status.allow2.com

### Integration Loads but Services Don't Work

**Problem**: Integration installed but `allow2.check_quota` fails.

**Solutions**:
1. Check child ID is correct (numeric, not name)
2. Verify activity name is valid (lowercase, no spaces)
3. Check logs for specific error messages
4. Try reinitializing integration (remove and re-add)

### No Children Found

**Problem**: "No children found" during setup.

**Solutions**:
1. Verify children exist in Allow2 web portal
2. Ensure your account has child profiles configured
3. Try refreshing integration (reload)
4. Check Allow2 account has active subscription

## Uninstalling

To remove the integration:

### HACS Uninstall

1. Go to **HACS** → **Integrations**
2. Find **Allow2 Parental Controls**
3. Click **⋮** menu
4. Select **Remove**
5. Go to **Settings** → **Devices & Services**
6. Find **Allow2 Parental Controls**
7. Click **⋮** menu
8. Select **Remove**
9. Restart Home Assistant

### Manual Uninstall

1. Go to **Settings** → **Devices & Services**
2. Find **Allow2 Parental Controls**
3. Click **⋮** menu
4. Select **Remove**
5. Remove files:
   ```bash
   rm -rf /config/custom_components/allow2/
   ```
6. Restart Home Assistant

## Security Notes

### Credential Security

- **Credentials are NOT stored** - Email and password are only used during initial pairing
- **Only tokens are retained** - `userId`, `pairId`, and `pairToken` are stored securely
- **Re-pair if compromised** - If you suspect tokens are compromised, remove and re-add the integration
- **Change Allow2 password** if needed - This will invalidate existing pairings

### Network Security

- Integration communicates only with Allow2 API (api.allow2.com)
- All communication over HTTPS
- No third-party services contacted
- Local caching reduces API exposure

### Access Control

- Only Home Assistant admins can configure
- Services require Home Assistant authentication
- No web interface exposes child data

## Next Steps

Now that the integration is installed:

1. **Configure Automations**: See [Use Cases](USE_CASES.md) for examples
2. **Set Up Devices**: Configure which devices to control
3. **Test Thoroughly**: Verify quota checking works as expected
4. **Monitor Logs**: Watch for any errors during first week

## Getting Help

If you encounter issues:

1. **Check Logs**: Settings → System → Logs (filter by "allow2")
2. **Review Documentation**: See other guides in this folder
3. **GitHub Issues**: Report bugs at https://github.com/allow2/allow2homeassistant/issues
4. **Community Forums**: Ask questions on Home Assistant forums
5. **Allow2 Support**: Contact Allow2 support for API issues

## Advanced Configuration

### Multiple Home Assistant Instances

If you have multiple Home Assistant instances:

1. Use unique device names for each instance (e.g., "Home Assistant - Main", "Home Assistant - Vacation Home")
2. All instances can pair with the same Allow2 account
3. Each instance creates its own set of sensors

### Multiple Allow2 Accounts (Multi-Parent Households)

Currently not supported. Future feature may allow:
- Multiple Allow2 accounts
- Separate configurations per parent
- Merged child lists

### Custom API Endpoint

For testing or private Allow2 servers:

**Not yet supported in config flow.**

Future versions may allow custom API endpoint configuration via YAML:
```yaml
# configuration.yaml (future feature)
allow2:
  api_url: "https://custom-allow2-api.example.com"
```

### Debug Logging

Enable detailed logging for troubleshooting:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.allow2: debug
```

Restart Home Assistant to see detailed logs in Settings → System → Logs.
