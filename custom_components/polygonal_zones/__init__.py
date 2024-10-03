"""The polygonal_zones integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_ZONES_URL, DATA_ZONES, DATA_ZONES_URL, DOMAIN, PLATFORM

PLATFORMS: list[Platform] = [Platform.DEVICE_TRACKER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up polygonal_zones from a config entry."""
    if entry.entry_id in hass.data:
        return True

    await hass.config_entries.async_forward_entry_setups(entry, [PLATFORM])
    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    unload_ok = True

    # Unload the platforms
    if not await hass.config_entries.async_forward_entry_unload(entry, PLATFORM):
        unload_ok = False

    if entry.entry_id in hass.data:
        del hass.data[DOMAIN][entry.entry_id]

    return unload_ok
