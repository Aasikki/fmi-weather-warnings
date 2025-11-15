"""Sensor platform for FMI Weather Warnings."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_AREA,
    ATTR_CERTAINTY,
    ATTR_DESCRIPTION,
    ATTR_EFFECTIVE,
    ATTR_EVENT,
    ATTR_EXPIRES,
    ATTR_HEADLINE,
    ATTR_INSTRUCTION,
    ATTR_SENDER,
    ATTR_SEVERITY,
    ATTR_URGENCY,
    CONF_AREA,
    DOMAIN,
)
from .coordinator import FMIWeatherWarningsCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FMI Weather Warnings sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        [
            FMIWeatherWarningsSensor(coordinator, entry),
        ],
        True,
    )


class FMIWeatherWarningsSensor(CoordinatorEntity, SensorEntity):
    """Representation of FMI Weather Warnings sensor."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:alert"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: FMIWeatherWarningsCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_active_warnings"
        self._attr_name = "Active warnings"
        area = entry.data.get(CONF_AREA, "")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"FMI Weather Warnings{' - ' + area if area else ''}",
            "manufacturer": "Finnish Meteorological Institute",
            "model": "Weather Warnings",
        }

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data.get("active_warnings", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        warnings = self.coordinator.data.get("warnings", [])
        
        attributes = {
            "warnings": [],
        }
        
        for warning in warnings:
            warning_attrs = {}
            
            # Add all available warning attributes
            if "title" in warning:
                warning_attrs["title"] = warning["title"]
            
            if "link" in warning:
                warning_attrs["link"] = warning["link"]
            
            if "published" in warning:
                warning_attrs["published"] = warning["published"]
            
            if "summary" in warning:
                warning_attrs["summary"] = warning["summary"]
            
            if "event" in warning:
                warning_attrs[ATTR_EVENT] = warning["event"]
            
            if "headline" in warning:
                warning_attrs[ATTR_HEADLINE] = warning["headline"]
            
            if "description" in warning:
                warning_attrs[ATTR_DESCRIPTION] = warning["description"]
            
            if "instruction" in warning:
                warning_attrs[ATTR_INSTRUCTION] = warning["instruction"]
            
            if "severity" in warning:
                warning_attrs[ATTR_SEVERITY] = warning["severity"]
            
            if "certainty" in warning:
                warning_attrs[ATTR_CERTAINTY] = warning["certainty"]
            
            if "urgency" in warning:
                warning_attrs[ATTR_URGENCY] = warning["urgency"]
            
            if "effective" in warning:
                warning_attrs[ATTR_EFFECTIVE] = warning["effective"]
            
            if "expires" in warning:
                warning_attrs[ATTR_EXPIRES] = warning["expires"]
            
            if "area" in warning:
                warning_attrs[ATTR_AREA] = warning["area"]
            
            if "sender" in warning:
                warning_attrs[ATTR_SENDER] = warning["sender"]
            
            attributes["warnings"].append(warning_attrs)
        
        return attributes
