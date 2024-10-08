"""The polygonal_zones integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORM
from .services import (
    add_new_zone_action_builder,
    delete_zone_action_builder,
    edit_zone_action_builder,
    replace_all_zones_action_builder,
)

PLATFORMS: list[Platform] = [Platform.DEVICE_TRACKER]


async def async_setup(hass: HomeAssistant, _config: dict) -> bool:
    """Set up the polygonal_zones component."""
    hass.data.setdefault(DOMAIN, {})

    hass.services.async_register(
        DOMAIN,
        "add_zone",
        add_new_zone_action_builder(hass),
    )

    hass.services.async_register(
        DOMAIN,
        "delete_zone",
        delete_zone_action_builder(hass),
    )

    hass.services.async_register(
        DOMAIN,
        "edit_zone",
        edit_zone_action_builder(hass),
    )

    hass.services.async_register(
        DOMAIN,
        "replace_all_zones",
        replace_all_zones_action_builder(hass),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up polygonal_zones from a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        return True

    await hass.config_entries.async_forward_entry_setups(entry, [PLATFORM])
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["device_tracker"]
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload polygonal_zones config entry."""
    entities = hass.data[DOMAIN][entry.entry_id]
    for entity in entities:
        await entity.async_update_config(entry)
