"""module root for the services for the polygonal zones integration."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from ..const import DOMAIN
from ..device_tracker import PolygonalZoneEntity
from .add_new_zone import add_new_zone_action_builder
from .delete_zone import delete_zone_action_builder
from .edit_zone import edit_zone_action_builder
from .replace_all_zones import replace_all_zones_action_builder

__all__ = [
    "add_new_zone_action_builder",
    "delete_zone_action_builder",
    "edit_zone_action_builder",
    "replace_all_zones_action_builder",
]

def get_zone_idx(name: str, existing_zones: dict[str, any]) -> int | None:
    """Get the index of the zone in the features list of a GeoJSON dict.

    Args:
        name: The name to get the index of
        existing_zones: A GeoJSON dict of the existing zones to search in.

    Returns:
         int | None: the index if the name is found. otherwise None

    """
    for idx, zone in enumerate(existing_zones["features"]):
        if zone["properties"]["name"] == name:
            return idx
    return None


def zone_already_defined(name: str, existing_zones: dict[str, any]) -> bool:
    """Check if a zone has already been defined.

    Args:
        name: The name of the zone to check for
        existing_zones: a GeoJSON dict of the existing zones to check in

    Returns:
         boolean: true if the zone already exists. false if it doesn't

    """
    for zone in existing_zones["features"]:
        if zone["properties"]["name"] == name:
            return True

    return False


def get_entities_from_device_id(
    device_id: str, hass: HomeAssistant
) -> list["PolygonalZoneEntity"]:
    """Get the entities from the provided device_id."""
    device_entry = dr.async_get(hass)
    device = device_entry.async_get(device_id)
    entry_id = device.primary_config_entry
    return hass.data[DOMAIN][entry_id]
