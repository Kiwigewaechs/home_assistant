"""Handle the connection to the inverter and and perform requests."""
from typing import Any

import requests

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError


class InverterConnector:
    """Connects to the inverter and calls its API."""

    def __init__(self, host: str, password: str, hass: HomeAssistant) -> None:
        """Initialize the connection to the inverter.

        :param host: The url/ip address of the inverter
        :param password: The password needed for the requests.
        :param hass: The home assistant instance
        """
        self.host = host
        self.hass = hass
        self.password = password

    async def IsAuthenticated(self) -> dict:
        """Test if we can authenticate with the host."""
        try:
            result = await self.request_data(10)
        except OSError:
            return {"authenticated": False}
        return {"authenticated": True, "result": result}

    async def request_data(self, timeout: int) -> dict:
        """Return the current state of the inverter by calling it's local API.

        :param timeout: The timeout time used for the request.
        """
        blocking_func = lambda host, data, timeout: requests.post(
            host, data, timeout=timeout
        )
        res = await self.hass.async_add_executor_job(
            blocking_func,
            self.host,
            f"optType=ReadRealTimeData&pwd={self.password}",
            timeout,
        )

        if res.status_code != 200:
            raise OSError
        return res.json()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    hub = InverterConnector(data["host"], data["password"], hass)

    auth_result = await hub.IsAuthenticated()

    if not auth_result["authenticated"]:
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {
        "title": auth_result["result"]["sn"],
        "data": {
            "SW version": auth_result["result"]["ver"],
            "sn": auth_result["result"]["sn"],
        },
    }


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
