"""Data update coordinator for FMI Weather Warnings."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import async_timeout
import feedparser

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_AREA, DEFAULT_SCAN_INTERVAL, DOMAIN, FMI_RSS_FEED

_LOGGER = logging.getLogger(__name__)


class FMIWeatherWarningsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching FMI weather warnings data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.area = entry.data.get(CONF_AREA, "").lower()
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from FMI RSS feed."""
        try:
            async with async_timeout.timeout(30):
                session = async_get_clientsession(self.hass)
                response = await session.get(FMI_RSS_FEED)
                
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                
                content = await response.text()
                
                # Parse RSS feed
                feed = await self.hass.async_add_executor_job(
                    feedparser.parse, content
                )
                
                if not feed or not feed.entries:
                    _LOGGER.debug("No warnings found in feed")
                    return {"warnings": [], "active_warnings": 0}
                
                warnings = []
                for entry in feed.entries:
                    warning = self._parse_entry(entry)
                    
                    # Filter by area if specified
                    if self.area:
                        area_desc = warning.get("area", "").lower()
                        if self.area not in area_desc:
                            continue
                    
                    warnings.append(warning)
                
                return {
                    "warnings": warnings,
                    "active_warnings": len(warnings),
                }
                
        except Exception as err:
            _LOGGER.error("Error fetching FMI weather warnings: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _parse_entry(self, entry: Any) -> dict[str, Any]:
        """Parse a single RSS entry into a warning dictionary."""
        warning = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", ""),
        }
        
        # Parse CAP elements if available
        if hasattr(entry, "cap_event"):
            warning["event"] = entry.cap_event
        
        if hasattr(entry, "cap_headline"):
            warning["headline"] = entry.cap_headline
        
        if hasattr(entry, "cap_description"):
            warning["description"] = entry.cap_description
        
        if hasattr(entry, "cap_instruction"):
            warning["instruction"] = entry.cap_instruction
        
        if hasattr(entry, "cap_severity"):
            warning["severity"] = entry.cap_severity
        
        if hasattr(entry, "cap_certainty"):
            warning["certainty"] = entry.cap_certainty
        
        if hasattr(entry, "cap_urgency"):
            warning["urgency"] = entry.cap_urgency
        
        if hasattr(entry, "cap_effective"):
            warning["effective"] = entry.cap_effective
        
        if hasattr(entry, "cap_expires"):
            warning["expires"] = entry.cap_expires
        
        if hasattr(entry, "cap_areadesc"):
            warning["area"] = entry.cap_areadesc
        
        if hasattr(entry, "cap_sender"):
            warning["sender"] = entry.cap_sender
        
        # Try to extract area from summary if not in CAP fields
        if "area" not in warning and "summary" in warning:
            # Sometimes the area is mentioned in the summary
            warning["area"] = ""
        
        return warning
