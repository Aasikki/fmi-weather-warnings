"""Config flow for FMI Weather Warnings integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_AREA, DOMAIN

_LOGGER = logging.getLogger(__name__)


class FMIWeatherWarningsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FMI Weather Warnings."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Create a unique ID based on the area (or use default if no area)
            area = user_input.get(CONF_AREA, "all_finland")
            await self.async_set_unique_id(f"fmi_warnings_{area.lower().replace(' ', '_')}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"FMI Weather Warnings{' - ' + user_input.get(CONF_AREA, '') if user_input.get(CONF_AREA) else ''}",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_AREA, default=""): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "area_help": "Optional: Enter a location name to filter warnings (e.g., 'Helsinki', 'Lapland'). Leave empty for all warnings."
            },
        )
