"""Constants for the Allow2 integration."""
from typing import Final

DOMAIN: Final = "allow2"

# API Endpoints
API_BASE_URL: Final = "https://api.allow2.com"
API_PAIR_ENDPOINT: Final = "/api/pairDevice"
API_CHECK_ENDPOINT: Final = "/serviceapi/check"

# Default device token for Home Assistant (vid=21588)
DEFAULT_DEVICE_TOKEN: Final = "mtG8xbFR1cuJkuXn"
DEFAULT_DEVICE_NAME: Final = "Home Assistant"

# Configuration keys
CONF_USER_ID: Final = "user_id"
CONF_PAIR_ID: Final = "pair_id"
CONF_PAIR_TOKEN: Final = "pair_token"
CONF_DEVICE_TOKEN: Final = "device_token"
CONF_DEVICE_NAME: Final = "device_name"
CONF_TIMEZONE: Final = "timezone"
CONF_CHILDREN: Final = "children"

# Activity IDs (Allow2 standard activities)
ACTIVITY_INTERNET: Final = 1
ACTIVITY_GAMING: Final = 2
ACTIVITY_SOCIAL_MEDIA: Final = 3
ACTIVITY_TELEVISION: Final = 4
ACTIVITY_SCREEN_TIME: Final = 5
ACTIVITY_MESSAGING: Final = 6

ACTIVITIES: Final = {
    ACTIVITY_INTERNET: "Internet",
    ACTIVITY_GAMING: "Gaming",
    ACTIVITY_SOCIAL_MEDIA: "Social Media",
    ACTIVITY_TELEVISION: "Television",
    ACTIVITY_SCREEN_TIME: "Screen Time",
    ACTIVITY_MESSAGING: "Messaging",
}

# Error messages
ERROR_AUTH_FAILED: Final = "auth_failed"
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
ERROR_UNKNOWN: Final = "unknown"
ERROR_INVALID_RESPONSE: Final = "invalid_response"
ERROR_ALREADY_PAIRED: Final = "already_paired"

# Timeout for API requests (seconds)
API_TIMEOUT: Final = 30
