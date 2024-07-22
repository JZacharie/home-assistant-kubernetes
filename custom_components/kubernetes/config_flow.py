from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN  # pylint:disable=unused-import
from .kubernetes_hub import KubernetesHub

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({("host"): str})


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    hub = KubernetesHub(hass)

    await hub.async_start()

    # do single request to validate authentication.
    await hub.list_namespaces_func()()

    return {"title": DOMAIN}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except MissingConfig:
                _LOGGER.error("Missing config file")
                errors["base"] = "missing_config"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.error("Unexpected exception: %s", ex)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


class MissingConfig(exceptions.HomeAssistantError):
    """Error to indicate that the configuration is missing."""
