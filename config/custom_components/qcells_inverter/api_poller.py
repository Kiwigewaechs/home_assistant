"""Specify the DataUpdateCoordinator used to cyclically poll data from a QCell converter."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import QCellsInverterConnector

_LOGGER = logging.getLogger(__name__)


class ApiPoller(DataUpdateCoordinator):
    """Polls the Qcell inverters local api."""

    def __init__(
        self, hass: HomeAssistant, inverter_api: QCellsInverterConnector, interval: int
    ) -> None:
        """Initialize the poller.

        :param hass: the home assistant instance
        :param interval: the polling interval
        :param inverter_api: Instance of object which knows about the inverters api and may poll it.
        """
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=f"QCellsInverterPoller [{inverter_api.host}]",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=interval),
        )
        self.inverter_api = inverter_api
        self.num_polls = 0
        self.failed_polls = 0
        self.maximally_allowd_fails = 10

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            data_dict = await self.inverter_api.request_data(10)
            self.num_polls += 1
            self.failed_polls = 0
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
            self.failed_polls += 1
            successful_polls = self.num_polls
            self.num_polls = 0

            if self.failed_polls < self.maximally_allowd_fails:
                raise UpdateFailed(
                    f"polling failed after {successful_polls} successful polls."
                ) from OSError
            else:
                # Raising ConfigEntryAuthFailed will cancel future updates
                # and start a config flow with SOURCE_REAUTH (async_step_reauth)
                raise ConfigEntryAuthFailed(f"num of tries: {self.num_polls}") from err
