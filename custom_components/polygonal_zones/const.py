import voluptuous as vol
from homeassistant.helpers import selector

DOMAIN = "polygonal_zones"
DATA_ZONES = f"{DOMAIN}_zones"
DATA_ZONES_URL = f"{DOMAIN}_zones_url"

CONF_REGISTERED_ENTITIES = "registered_entities"
CONF_ZONES_URL = "zones_url"
PLATFORM = "sensor"

CONF_SCHEMA = vol.Schema(
    {
        vol.Required("zones_url"): str,
        vol.Required("registered_entities"): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["person", "device_tracker"], multiple=True
            )
        ),
    }
)
