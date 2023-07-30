"""define the sensors which listen to single QCell inverter properties."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api_poller import ApiPoller
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py
    inverter_api = hass.data[DOMAIN][entry.entry_id]
    coordinator = ApiPoller(hass, inverter_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        QCellsSensorReader(coordinator, idx, entry.data["sn"])
        for idx, _ in enumerate(coordinator.data["Data"])
    )


class QCellsSensorReader(CoordinatorEntity, SensorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, idx, sn) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx
        self._attr_unique_id = f"{sn}_{idx:03}"
        self._attr_name = f"QCells Sensor {idx:03} for Inverter SN: {sn}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["Data"][self.idx]
        self.async_write_ha_state()

    # async def async_turn_on(self, **kwargs):
    #    """Turn the light on.
    #
    #    Example method how to request data updates.
    #    """
    #    # Do the turning on.
    #    # ...
    #
    #    # Update the data
    #    await self.coordinator.async_request_refresh()
