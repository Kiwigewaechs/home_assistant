"""Handle the option flow and allow reconfiguring the integration."""

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, OptionsFlow
from homeassistant.data_entry_flow import FlowResult

from .api import CannotConnect, InvalidAuth, validate_input
from .const import MIN_POLLING_INTERVAL


class OptionsFlowHandler(OptionsFlow):
    """Implement the options reset flow."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the Options flow handler and therefore allows to change options in the integration.

        :param config_entry: the config entry which was already set for the integration within homeassistant.
        """
        # super().__init__()
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the flow which is triggered when trying to change options via the GUI.

        :param user_input: A dictionary which contains the options which are set via the GUI.
                           It is set to none by default when the GUI did not yet deliver something.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                # _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=self.config_entry.data.get("title"), data=user_input
                )

        data_scheme = vol.Schema(
            {
                vol.Required("host", default=self.config_entry.data.get("host")): str,
                vol.Required(
                    "password", default=self.config_entry.data.get("password")
                ): str,
                vol.Required(
                    "interval", default=self.config_entry.data.get("interval")
                ): vol.All(int, vol.Range(min=MIN_POLLING_INTERVAL)),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=data_scheme, errors=errors
        )
