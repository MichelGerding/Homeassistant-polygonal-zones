"""Sensor for the polygonal_zones integration."""

import logging
from datetime import datetime

import pandas as pd
from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_REGISTERED_ENTITIES, DATA_ZONES, DOMAIN
from .utils import get_locations_zone, event_should_trigger

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        _hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """
    Set up the entities from a config entry.

    Args:
        _hass: The Home Assistant instance.
        entry: The config entry.
        async_add_entities: A callable to add the entities.

    Returns:
        None
    """
    # create the entities
    entities = [
        PolygonalZoneEntity(entity_id, entry.entry_id)
        for entity_id in entry.data.get(CONF_REGISTERED_ENTITIES, [])
    ]

    async_add_entities(entities, True)


class PolygonalZoneEntity(TrackerEntity):
    """Representation of a polygonal zone entity."""

    _zones: pd.DataFrame = pd.DataFrame([])
    _unsub: callable = None

    _attr_location_name: str = None
    _attr_latitude: float = None
    _attr_longitude: float = None
    _attr_gps_accuracy: float = None

    def __init__(self, entity_id, config_entry_id):
        """Initialize the entity."""
        self._config_entry_id = config_entry_id
        self._entity_id = entity_id

        self._attr_name = f"Polygonal Zone Tracker: {entity_id}"
        self._attr_unique_id = f"polygonal_zone_{entity_id.replace(".", "_")}"
        self._attr_source_type = SourceType.GPS

    async def async_added_to_hass(self):
        """Run when the entity is added to homeassistant.

        This function registers the listener and sets the initial known state.
        If the entities state is None, it will stay in the unknown state.
        """
        self._zones = self.hass.data[DOMAIN][self._config_entry_id][DATA_ZONES]
        self._unsub = self.hass.bus.async_listen(
            "state_changed", self._handle_state_change_builder()
        )

        entity_state = self.hass.states.get(self._entity_id)
        if entity_state is not None:
            for key in ["latitude", "longitude", "gps_accuracy"]:
                if key not in entity_state.attributes:
                    _LOGGER.error(
                        "Entity %s does not have the required attributes to be a location entity",
                        self._entity_id,
                    )
                    return

            self._attr_source_type = entity_state.attributes.get("source_type")
            self.update_location(
                entity_state.attributes["latitude"],
                entity_state.attributes["longitude"],
                entity_state.attributes["gps_accuracy"],
            )

    async def async_will_remove_from_hass(self):
        """Handle cleanup when the entity is removed."""
        if self._unsub:
            self._unsub()

    def update_location(self, latitude, longitude, gps_accuracy):
        # self._attr_latitude = latitude
        # self._attr_longitude = longitude
        # self._attr_gps_accuracy = gps_accuracy

        zone = get_locations_zone(latitude, longitude, gps_accuracy, self._zones)
        _LOGGER.info("Zone: %s", zone)
        self._attr_location_name = zone["name"] if zone is not None else "away"
        self._attr_extra_state_attributes = {
            "source_entity": self._entity_id,
            "latitude": latitude,
            "longitude": longitude,
            "gps_accuracy": gps_accuracy,
        }

    def _handle_state_change_builder(self):
        """Create a callback for the state updates.

        This listener will check if it should operate on the event and then update the state.
        """

        async def func(event):
            # check if it is the entity we should listen to.
            _LOGGER.debug("Event: %s", event)
            if event_should_trigger(event, self._entity_id):
                new_state = event.data["new_state"].attributes
                self.update_location(
                    new_state["latitude"],
                    new_state["longitude"],
                    new_state["gps_accuracy"]
                )

                self.async_write_ha_state()

        return func

    @property
    def source_type(self) -> SourceType | str:
        return self._attr_source_type

    @property
    def location_name(self):
        return self._attr_location_name

    @property
    def device_info(self):
        return {
            "identifiers": {("polygonal_zones", self._config_entry_id)},
            "name": "Polygonal Zones",
            "manufacturer": "Michel Gerding",
        }

    @property
    def should_poll(self):
        """Return False because entity will be updated via callback."""
        return False
