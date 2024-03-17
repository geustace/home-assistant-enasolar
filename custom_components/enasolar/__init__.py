"""Implements the enasolar component."""

from datetime import timedelta
import logging
import async_timeout

import pyenasolar

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryNotReady,
)

from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the config entry."""
    host = entry.data[CONF_HOST]
    enasolar = pyenasolar.EnaSolar()
    try:
        await enasolar.interogate_inverter(host)
        if not enasolar.serial_no:
            raise ConfigEntryNotReady
    except Exception as conerr:
        raise ConfigEntryNotReady(
            f"Connection to EnaSolar Inverter '{host}' failed ({conerr})"
        ) from conerr

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = enasolar

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok

async def options_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
