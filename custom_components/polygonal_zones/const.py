from voluptuous import Schema, Required
from homeassistant.helpers import selector

DOMAIN = "polygonal_zones"
DATA_ZONES = f"{DOMAIN}_zones"
DATA_ZONES_URL = f"{DOMAIN}_zones_url"

CONF_REGISTERED_ENTITIES = "registered_entities"
CONF_ZONES_URL = "zones_urls"
PLATFORM = "device_tracker"

CONF_SCHEMA = Schema({
    # zones_url: list[str],
    Required(
        CONF_ZONES_URL,
        description="URLs of GeoJSON files containing polygonal zones",
        default=["http://192.168.1.31:8000/zones.json"],
    ): selector.TextSelector(
        selector.TextSelectorConfig(
            multiple=True
        )
    ),



    Required(
        CONF_REGISTERED_ENTITIES,
        description="Entities to be used for location tracking"
    ): selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain=["device_tracker"], multiple=True
        )
    ),
})

# CONF_SCHEMA = vol.Schema(
#     {
#         vol.Required("zones_url"): str,
#         vol.Required("registered_entities"): selector.EntitySelector(
#             selector.EntitySelectorConfig(
#                 domain=["person", "device_tracker"], multiple=True
#             )
#         ),
#     }
# )
