from voluptuous import Schema, Required

from homeassistant.helpers import selector

DOMAIN = "polygonal_zones"
DATA_ZONES = f"{DOMAIN}_zones"
DATA_ZONES_URL = f"{DOMAIN}_zones_url"

CONF_PRIORITIZE_ZONE_FILES = "prioritize_zone_files"
CONF_REGISTERED_ENTITIES = "registered_entities"
CONF_ZONES_URL = "zone_urls"
CONF_ENSURE_UNIQUE_ENTITIES = "ensure_unique_entities"
PLATFORM = "device_tracker"

CONF_SCHEMA = Schema({
    # zones_url: list[str],
    Required(
        "zone_urls",
        default=["http://192.168.1.31:8000/zones.json"],
    ): selector.TextSelector(
        selector.TextSelectorConfig(
            multiple=True,
        )
    ),

    Required(
        "prioritize_zone_files",
        default=False
    ): selector.BooleanSelector(selector.BooleanSelectorConfig()),

    Required(
        "registered_entities",
    ): selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain=["device_tracker"], multiple=True
        )
    ),
})
