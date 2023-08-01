"""The QCells Inverter integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import QCellsInverterConnector
from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up QCells Inverter from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    api = QCellsInverterConnector(entry.data["host"], entry.data["password"], hass)
    authentication = await api.IsAuthenticated()
    if not authentication["authenticated"]:
        raise ConfigEntryAuthFailed
    hass.data[DOMAIN][entry.entry_id] = api

    # update listener which reacts on updates in the option flow:
    entry.async_on_unload(entry.add_update_listener(qcells_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def qcells_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Trigger that when an entry was updated by the options flow."""
    entry.data = entry.data | entry.options
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
