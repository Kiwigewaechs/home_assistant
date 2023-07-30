"""Specify the DataUpdateCoordinator used to cyclically poll data from a QCell converter."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import InverterConnector

_LOGGER = logging.getLogger(__name__)


class ApiPoller(DataUpdateCoordinator):
    """Polls the Qcell inverters local api."""

    def __init__(self, hass: HomeAssistant, inverter_api: InverterConnector) -> None:
        """Initialize the poller.

        :param hass: the home assistant instance
        :param inverter_api: Instance of object which knows about the inverters api and may poll it.
        """
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=f"QCellsInverterPoller [{inverter_api.host}]",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=5),
        )
        self.inverter_api = inverter_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            data_dict = await self.inverter_api.request_data(10)
            return data_dict

            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            # async with async_timeout.timeout(10):
            # Grab active context variables to limit data required to be fetched from API
            # Note: using context is not required if there is no need or ability to limit
            # data retrieved from API.
            #    listening_idx = set(self.async_contexts())
            #    return await self.my_api.fetch_data(listening_idx)

        except OSError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #     raise UpdateFailed(f"Error communicating with API: {err}")
