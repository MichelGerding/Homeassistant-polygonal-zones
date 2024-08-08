"""The Polygonal Zones integration."""

import json
import logging

import aiohttp
import pandas as pd
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from shapely.geometry import shape

from .const import (CONF_REGISTERED_ENTITIES, CONF_ZONES_URL, DATA_ZONES,
                    DOMAIN, PLATFORM)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up My Integration from a config entry."""
    # Ensure the entry is not already set up
    if entry.entry_id in hass.data:
        return True

    # ensure hass.data[DOMAIN][entry.entry_id] exists
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    # Load and store the zones
    zones_url = entry.data.get(CONF_ZONES_URL)
    hass.data[DOMAIN][entry.entry_id][DATA_ZONES] = await get_zones(zones_url)

    # create entity and store the entry
    hass.data[DOMAIN][entry.entry_id] = entry
    await hass.config_entries.async_forward_entry_setups(entry, [PLATFORM])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = True

    # Unload the platforms
    if not await hass.config_entries.async_forward_entry_unload(entry, PLATFORM):
        unload_ok = False

    if entry.entry_id in hass.data:
        del hass.data[DOMAIN][entry.entry_id]

    return unload_ok


async def load_data(uri: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as response:
            return await response.text()


async def get_zones(uri: str) -> pd.DataFrame:
    data = await load_data(uri)
    data = json.loads(data)

    zones = []
    for i, feature in enumerate(data["features"]):
        geometry = shape(feature["geometry"])
        properties = feature["properties"]
        zones.append({"geometry": geometry, **properties})

    return pd.DataFrame(zones)
