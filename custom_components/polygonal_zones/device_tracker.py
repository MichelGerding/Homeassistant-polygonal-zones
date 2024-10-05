"""Sensor for the polygonal_zones integration."""

import logging
from collections.abc import Callable, Coroutine
from typing import Any

import pandas as pd

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import generate_entity_id

from .const import (CONF_PRIORITIZE_ZONE_FILES, CONF_REGISTERED_ENTITIES,
                    CONF_ZONES_URL, DOMAIN)
from .utils import event_should_trigger, get_locations_zone
from .utils.zones import get_zones

_LOGGER = logging.getLogger(__name__)


async def custom_async_reload_zones(
    entity: "PolygonalZoneEntity", call: ServiceCall
) -> None:
    """Reload the zones of the entity."""
    await entity.async_reload_zones()

    if call.return_response:
        zones_clone = entity.zones.copy()
        zones_clone["geometry"] = zones_clone["geometry"].apply(
            lambda polygon: list(polygon.exterior.coords)
        )
        return zones_clone[["name", "priority", "geometry"]].to_dict(orient="records")
    return None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the entities from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.
        async_add_entities: A callable to add the entities.

    Returns:
        None

    """
    zone_uris = entry.data.get(CONF_ZONES_URL)
    zone_uris = [
        zone_uri for zone_uri in zone_uris if zone_uri is not None and zone_uri != ""
    ]

    # create the entities
    entities = []

    for entity_id in entry.data.get(CONF_REGISTERED_ENTITIES, []):
        entitiy_name = entity_id.split(".")[-1]
        base_id = generate_entity_id(
            "device_tracker.polygonal_zones_{}", entitiy_name, hass=hass
        )

        entity = PolygonalZoneEntity(
            entity_id,
            entry.entry_id,
            zone_uris,
            base_id,
            entry.data.get(CONF_PRIORITIZE_ZONE_FILES),
        )
        entities.append(entity)

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        "reload_zones",
        {},
        custom_async_reload_zones,
        supports_response=SupportsResponse.OPTIONAL,
    )

    async_add_entities(entities, True)
    hass.data[DOMAIN][entry.entry_id] = entities


class PolygonalZoneEntity(TrackerEntity):
    """Representation of a polygonal zone entity."""

    _zones: pd.DataFrame = pd.DataFrame([])
    _unsub: callable = None

    _attr_location_name: str = None
    _attr_latitude: float = None
    _attr_longitude: float = None
    _attr_gps_accuracy: float = None

    def __init__(
        self,
        tracked_entity_id,
        config_entry_id,
        zone_urls,
        unique_id,
        prioritized_zone_files,
    ):
        """Initialize the entity."""
        self._config_entry_id = config_entry_id
        self._entity_id = tracked_entity_id
        self._zones_urls = zone_urls
        self._prioritize_zone_files = prioritized_zone_files

        self.entity_id = unique_id
        self._attr_unique_id = unique_id
        self._attr_source_type = SourceType.GPS

    async def async_added_to_hass(self):
        """Run when the entity is added to homeassistant.

        This function registers the listener and sets the initial known state.
        If the entities state is None, it will stay in the unknown state.
        """
        self._zones = await get_zones(
            self._zones_urls, self.hass, self._prioritize_zone_files
        )
        self._unsub = self.hass.bus.async_listen(
            "state_changed", self._handle_state_change_builder()
        )

        await self._update_state()

    async def async_update_config(self, config_entry: ConfigEntry):
        """Update the configuration of the entity."""
        self._zones_urls = config_entry.data.get(CONF_ZONES_URL)
        self._prioritize_zone_files = config_entry.data.get(CONF_PRIORITIZE_ZONE_FILES)

        self._zones = await get_zones(
            self._zones_urls, self.hass, self._prioritize_zone_files
        )

        await self._update_state()

    async def async_will_remove_from_hass(self):
        """Handle cleanup when the entity is removed."""
        if self._unsub:
            self._unsub()

    def update_location(self, latitude, longitude, gps_accuracy) -> None:
        """Update the location of the entity.

        this function should only be called when either the latitude, longitude or gps accuracy changes.

        Args:
            latitude: The latitude of the tracked entity.
            longitude: The longitude of the tracked entity.
            gps_accuracy: The accuracy of the entity.

        """

        zone = get_locations_zone(latitude, longitude, gps_accuracy, self._zones)
        _LOGGER.info(
            "State of entity '%s' changed. new zone: %s", self._attr_unique_id, zone
        )
        self._attr_location_name = zone["name"] if zone is not None else "away"
        self._attr_extra_state_attributes = {
            "source_entity": self._entity_id,
            "latitude": latitude,
            "longitude": longitude,
            "gps_accuracy": gps_accuracy,
        }

    def _handle_state_change_builder(
        self,
    ) -> Callable[[Any], Coroutine[Any, Any, None]]:
        """Create a callback for the state updates.

        This listener will check if it should operate on the event and then update the state.
        """

        async def func(event: Any) -> None:
            # check if it is the entity we should listen to.
            if event_should_trigger(event, self._entity_id):
                await self._update_state()

        return func

    async def _update_state(self):
        entity_state = self.hass.states.get(self._entity_id)
        if entity_state is not None and all(
            key in entity_state.attributes
            for key in ["latitude", "longitude", "gps_accuracy"]
        ):
            self.update_location(
                entity_state.attributes["latitude"],
                entity_state.attributes["longitude"],
                entity_state.attributes["gps_accuracy"],
            )

            self.async_write_ha_state()

    async def async_reload_zones(self):
        """Reload the zones."""
        self._zones = await get_zones(
            self._zones_urls, self.hass, self._prioritize_zone_files
        )
        _LOGGER.info("Reloaded zones of entity: %s", self._attr_unique_id)
        await self._update_state()

    @property
    def zones(self):
        """The loaded zones."""
        return self._zones

    @property
    def source_type(self) -> SourceType | str:
        """The source type for the location service."""
        return self._attr_source_type

    @property
    def location_name(self) -> str:
        """Name of the zone the entity is in."""
        return self._attr_location_name

    @property
    def device_info(self) -> dict[str, Any]:
        """Information about the polygonal_zones device."""
        return {
            "identifiers": {("polygonal_zones", self._config_entry_id)},
            "name": "Polygonal Zones",
            "manufacturer": "Michel Gerding",
        }

    @property
    def should_poll(self):
        """Return False because entity will be updated via callback."""
        return False
