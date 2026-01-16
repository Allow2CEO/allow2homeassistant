"""The Allow2 integration.

Allow2 is a parental control service that manages screen time
and activity allowances for children. This integration uses
device pairing mode to connect Home Assistant with Allow2.

After pairing, you can:
- Check if activities are allowed for specific children
- Get remaining time for activities
- Monitor screen time usage
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import Allow2API, Allow2AuthError, Allow2ConnectionError
from .const import (
    ACTIVITIES,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TOKEN,
    CONF_PAIR_ID,
    CONF_PAIR_TOKEN,
    CONF_USER_ID,
    DEFAULT_DEVICE_NAME,
    DEFAULT_DEVICE_TOKEN,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Update interval for checking quotas
SCAN_INTERVAL = timedelta(minutes=5)


class Allow2DataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching Allow2 data for a specific child."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: Allow2API,
        user_id: int,
        pair_id: int,
        pair_token: str,
        child_id: int,
        child_name: str,
        timezone: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Allow2 {child_name}",
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.user_id = user_id
        self.pair_id = pair_id
        self.pair_token = pair_token
        self.child_id = child_id
        self.child_name = child_name
        self.timezone = timezone

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Allow2."""
        try:
            result = await self.api.check(
                user_id=self.user_id,
                pair_id=self.pair_id,
                pair_token=self.pair_token,
                child_id=self.child_id,
                activities=list(ACTIVITIES.keys()),
                timezone=self.timezone,
                log=False,  # Don't log polling checks
            )
            return {
                "allowed": result.allowed,
                "activities": result.activities,
                "raw": result.raw_response,
            }
        except (Allow2ConnectionError, Allow2AuthError) as err:
            raise UpdateFailed(f"Error fetching Allow2 data: {err}") from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Allow2 from a config entry.

    This creates the API client with stored credentials and
    sets up platforms for monitoring children's activities.
    """
    hass.data.setdefault(DOMAIN, {})

    # Create API client with stored credentials
    session = async_get_clientsession(hass)
    api = Allow2API(
        session=session,
        device_token=entry.data.get(CONF_DEVICE_TOKEN, DEFAULT_DEVICE_TOKEN),
        device_name=entry.data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
    )

    # Get timezone from Home Assistant
    timezone = str(hass.config.time_zone)

    # Create coordinators for each child
    children: list[dict[str, Any]] = entry.data.get("children", [])
    coordinators: dict[int, Allow2DataUpdateCoordinator] = {}

    for child in children:
        child_id = child.get("id")
        child_name = child.get("name", f"Child {child_id}")

        if not child_id:
            continue

        coordinator = Allow2DataUpdateCoordinator(
            hass,
            api=api,
            user_id=entry.data[CONF_USER_ID],
            pair_id=entry.data[CONF_PAIR_ID],
            pair_token=entry.data[CONF_PAIR_TOKEN],
            child_id=child_id,
            child_name=child_name,
            timezone=timezone,
        )

        # Fetch initial data
        await coordinator.async_config_entry_first_refresh()
        coordinators[child_id] = coordinator

    # Store entry data for platforms
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "user_id": entry.data[CONF_USER_ID],
        "pair_id": entry.data[CONF_PAIR_ID],
        "pair_token": entry.data[CONF_PAIR_TOKEN],
        "children": children,
        "coordinators": coordinators,
    }

    _LOGGER.info(
        "Allow2 integration set up for user %d with %d children",
        entry.data[CONF_USER_ID],
        len(children),
    )

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
