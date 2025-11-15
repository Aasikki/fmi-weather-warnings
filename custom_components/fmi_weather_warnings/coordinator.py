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
                all_warnings = []  # Keep track of all warnings for debugging
                
                for entry in feed.entries:
                    warning = self._parse_entry(entry)
                    all_warnings.append(warning)
                    
                    # Filter by area if specified
                    if self.area:
                        area_desc = warning.get("area", "").lower()
                        title_lower = warning.get("title", "").lower()
                        summary_lower = warning.get("summary", "").lower()
                        
                        _LOGGER.debug(f"Checking area filter: configured='{self.area}', warning_area='{area_desc}', title='{warning.get('title', '')}'")
                        
                        # If there's no meaningful content, include the warning
                        # This handles cases where the RSS feed doesn't have proper area fields
                        if not area_desc and not title_lower and not summary_lower:
                            _LOGGER.debug(f"No content found, including warning: {warning.get('title', '')}")
                        else:
                            # Check if the configured area matches in any of the text fields
                            area_found = False
                            search_text = f"{area_desc} {title_lower} {summary_lower}"
                            
                            # Log the search text for debugging (first 200 chars)
                            if search_text.strip():
                                _LOGGER.debug(f"Search text (first 200 chars): '{search_text[:200]}...'")
                            
                            if self.area in search_text:
                                area_found = True
                                _LOGGER.debug(f"Direct match found for '{self.area}'")
                            else:
                                # Try more flexible matching for Finnish place names
                                # Remove common Finnish suffixes/prefixes for matching
                                area_variants = [self.area]
                                
                                # Add variant without common Finnish suffixes
                                for suffix in ['n', 'ssa', 'ssä', 'sta', 'stä', 'an', 'än', 'la', 'lä', 'lla', 'llä', 'lta', 'ltä', 'lle']:
                                    if self.area.endswith(suffix) and len(self.area) > len(suffix) + 2:
                                        variant = self.area[:-len(suffix)]
                                        if variant not in area_variants:
                                            area_variants.append(variant)
                                
                                # Also try adding common suffixes if the base doesn't match
                                for suffix in ['ssa', 'ssä', 'sta', 'stä', 'an', 'än', 'la', 'lä']:
                                    variant = self.area + suffix
                                    if variant not in area_variants:
                                        area_variants.append(variant)
                                
                                _LOGGER.debug(f"Trying area variants: {area_variants}")
                                
                                # Check if any variant matches
                                for variant in area_variants:
                                    if variant in search_text:
                                        area_found = True
                                        _LOGGER.debug(f"Variant match found: '{variant}'")
                                        break
                            
                            if not area_found:
                                _LOGGER.debug(f"Filtered out warning (no area match): {warning.get('title', '')}")
                                continue
                            else:
                                _LOGGER.debug(f"Area match found, including: {warning.get('title', '')}")
                    
                    warnings.append(warning)
                
                _LOGGER.debug(f"Total warnings found: {len(all_warnings)}, after filtering: {len(warnings)}, configured area: '{self.area}'")
                
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
        
        _LOGGER.debug(f"Parsing entry: {warning['title']}")
        
        # Log available CAP attributes for debugging
        cap_attrs = [attr for attr in dir(entry) if attr.startswith('cap_')]
        if cap_attrs:
            _LOGGER.debug(f"Available CAP attributes: {cap_attrs}")
        
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
        
        # Handle area information from multiple sources
        area_info = []
        
        if hasattr(entry, "cap_areadesc"):
            area_info.append(entry.cap_areadesc)
            warning["area"] = entry.cap_areadesc
        
        # Check for other area-related CAP fields
        if hasattr(entry, "cap_area"):
            area_info.append(entry.cap_area)
        
        if hasattr(entry, "cap_geocode"):
            area_info.append(entry.cap_geocode)
        
        if hasattr(entry, "cap_sender"):
            warning["sender"] = entry.cap_sender
        
        # Try to extract area from title or summary if not in CAP fields
        if not area_info:
            # Sometimes the area is mentioned in the title or summary
            title_lower = warning.get("title", "").lower()
            summary_lower = warning.get("summary", "").lower()
            
            # Look for common Finnish location patterns in title/summary
            combined_text = f"{title_lower} {summary_lower}"
            warning["area"] = combined_text
        
        # Combine all area information if we have multiple sources
        if area_info:
            warning["area"] = " ".join(str(area) for area in area_info if area)
        
        return warning
