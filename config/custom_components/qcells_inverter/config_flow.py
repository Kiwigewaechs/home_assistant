"""Config flow for QCells Inverter integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import CannotConnect, InvalidAuth, validate_input
from .const import DOMAIN, MIN_POLLING_INTERVAL
from .options_flow import OptionsFlowHandler

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("password"): str,
        vol.Required("interval"): vol.All(int, vol.Range(min=MIN_POLLING_INTERVAL)),
    }
)


class QCellsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for QCells Inverter."""

    VERSION = 1

    async def check_for_authentication(self, user_input: dict[str, Any]):
        """Check for authentication by polling data and return valid data if possible.

        :param user_input: The user_input from a form; type is a dictionary.
        """
        errors: dict[str, str] = {}
        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        return info, errors

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            info, errors = await self.check_for_authentication(user_input)
            if not errors:
                return self.async_create_entry(
                    title=info["title"], data=user_input | info["data"]
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        _LOGGER.debug("Trying to reauthenticate QCells integration")
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        errors: dict[str, str] = {}
        if user_input is not None:
            info, errors = await self.check_for_authentication(user_input)
            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.reauth_entry,
                    title=info["title"],
                    data=user_input | info["data"],
                )
                await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")
                # return self.async_create_entry(
                #     title=info["title"], data=user_input | info["data"]
                # )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
