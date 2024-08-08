""" Sensor for the polygonal_zones integration. """

import logging
from typing import Optional

import pandas as pd
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from shapely.geometry import Point

from .const import CONF_REGISTERED_ENTITIES, DATA_ZONES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    """
    Set up the entities from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.
        async_add_entities: A callable to add the entities.

    Returns:
        None
    """
    # create the entities
    entities = []
    for entity_id in entry.data.get(CONF_REGISTERED_ENTITIES, []):
        entities.append(PolygonalZoneEntity(entity_id, entry.entry_id))

    async_add_entities(entities, True)


def get_locations_zone(lat: float, lon: float, acc: float, zones: pd.DataFrame) -> Optional[pd.Series]:
    """
    Determine the closest zone to the given GPS coordinates.

    Args:
        lat: The latitude of the GPS coordinates.
        lon: The longitude of the GPS coordinates.
        acc: The accuracy of the GPS coordinates in meters.
        zones: A pandas DataFrame containing the zones, with a "geometry" column
            of Polygon objects.

    Returns:
        The closest zone if found, otherwise `None`.
    """
    gps_point = Point(lon, lat)
    buffer = gps_point.buffer(acc / 111320)

    # Get the zones we might be in
    posible_zones = zones[buffer.intersects(zones["geometry"])]

    # if we have 1 or 0 possible zones we will return.
    if posible_zones.empty:
        return None
    if len(posible_zones) == 1:
        return posible_zones.iloc[0]

    # get the distances to the potential zones
    distances = posible_zones["geometry"].apply(lambda zone, point=gps_point: point.distance(zone))
    closest_zone_index = distances.idxmin()
    return zones.loc[closest_zone_index]


class PolygonalZoneEntity(SensorEntity):
    """Representation of a polygonal zone entity."""

    _zones: pd.DataFrame = pd.DataFrame([])
    _unsub: callable = None

    _state: str = "unknown"

    def __init__(self, entity_id, config_entry_id):
        """Initialize the entity."""
        self._config_entry_id = config_entry_id
        self._entity_id = entity_id

        self._attr_name = f"Polygonal Zone Tracker: {entity_id}"
        self._attr_unique_id = f"polygonal_zone_{entity_id.replace(".", "_")}"

    async def async_added_to_hass(self):
        """Run when the entity is added to homeassistant.

        This function registers the listener and sets the initial known state.
        If the entities state is None, it will stay in the unknown state.
        """
        self._zones = self.hass.data[self.entry_id][DATA_ZONES]
        self._unsub = self.hass.bus.async_listen("state_changed", self._handle_state_change_builder())

        entity_state = self.hass.states.get(self._entity_id)
        if entity_state is None:
            return

        self.update_location(
            entity_state.attributes["latitude"],
            entity_state.attributes["longitude"],
            entity_state.attributes["gps_accuracy"],
        )

    async def async_will_remove_from_hass(self):
        """Handle cleanup when the entity is removed."""
        self._unsub()

    def update_location(self, latitude, longitude, gps_accuracy):
        zone = get_locations_zone(latitude, longitude, gps_accuracy, self._zones)
        if zone is None:
            zone = {"name": "away"}

        self._state = zone["name"]

    def _handle_state_change_builder(self):
        """Create a callback for the state updates.

        This listener will check if it should operate on the event and then update the state.
        """

        async def func(event):
            # check if we it is the entity we should listen to.
            if event.data["entity_id"] != self._entity_id:
                return
            # extract the states from the event
            old_state = event.data["old_state"].attributes
            new_state = event.data["new_state"].attributes

            # check if one or more of the important data has been updated
            if old_state["latitude"] != new_state["latitude"] or old_state["longitude"] != new_state["longitude"] or \
                    old_state["gps_accuracy"] != new_state["gps_accuracy"]:
                # Extract necessary information
                latitude = new_state["latitude"]
                longitude = new_state["longitude"]
                gps_accuracy = new_state["gps_accuracy"]

                # Determine the current zone
                self.update_location(latitude, longitude, gps_accuracy)
                self.async_write_ha_state()

        return func

    @property
    def device_info(self):
        return {
            "identifiers": {("polygonal_zones", self._config_entry_id)},
            "name": "Polygonal Zones",
            "manufacturer": "Michel Gerding",
        }

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def should_poll(self):
        """Return False because entity will be updated via callback."""
        return False
