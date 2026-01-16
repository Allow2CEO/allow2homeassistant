"""Sensor platform for Allow2 integration.

Provides sensors for remaining time on activities for each child.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ACTIVITIES, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Allow2 sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data.get("coordinators", {})
    children: list[dict[str, Any]] = data.get("children", [])

    entities: list[Allow2RemainingTimeSensor] = []

    for child in children:
        child_id = child.get("id")
        child_name = child.get("name", f"Child {child_id}")

        if not child_id or child_id not in coordinators:
            continue

        coordinator = coordinators[child_id]

        # Create sensors for common activities
        for activity_id, activity_name in ACTIVITIES.items():
            entities.append(
                Allow2RemainingTimeSensor(
                    coordinator=coordinator,
                    child_id=child_id,
                    child_name=child_name,
                    activity_id=activity_id,
                    activity_name=activity_name,
                    entry_id=entry.entry_id,
                )
            )

    async_add_entities(entities)


class Allow2RemainingTimeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for remaining time on an activity."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        child_id: int,
        child_name: str,
        activity_id: int,
        activity_name: str,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._child_id = child_id
        self._child_name = child_name
        self._activity_id = activity_id
        self._activity_name = activity_name

        # Entity attributes
        self._attr_unique_id = f"{entry_id}_{child_id}_{activity_id}_remaining"
        self._attr_name = f"{child_name} {activity_name} Remaining"

    @property
    def native_value(self) -> int | None:
        """Return the remaining time in seconds."""
        if not self.coordinator.data:
            return None

        activities = self.coordinator.data.get("activities", {})
        activity = activities.get(self._activity_id)

        if activity:
            return activity.remaining_seconds

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {
            "child_id": self._child_id,
            "child_name": self._child_name,
            "activity_id": self._activity_id,
            "activity_name": self._activity_name,
        }

        if not self.coordinator.data:
            return attrs

        activities = self.coordinator.data.get("activities", {})
        activity = activities.get(self._activity_id)

        if activity:
            attrs.update({
                "allowed": activity.allowed,
                "banned": activity.banned,
                "time_block_allowed": activity.time_block_allowed,
            })

        return attrs
