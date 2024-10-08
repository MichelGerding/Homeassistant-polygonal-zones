"""definition file for the add new zone action."""

import json
from pathlib import Path

from homeassistant.core import HomeAssistant, ServiceCall

from .errors import (
    ZoneAlreadyExists,
    ZoneFileNotEditable,
)
from ..utils.general import load_data
from ..utils.local_zones import save_zones
from .helpers import get_entities_from_device_id, zone_already_defined


def add_new_zone_action_builder(hass: HomeAssistant):
    """Builder for the add new zone action."""

    async def add_new_zone(call: ServiceCall):
        """Handle the service action call."""
        device_id = call.data.get("device_id")[0]
        entity = get_entities_from_device_id(device_id, hass)[0]

        if not entity.editable_file:
            raise ZoneFileNotEditable("Zone files of entity are not editable")

        # get the source path for the zones
        filename = entity.zone_urls[0]
        filepath = Path(f"{hass.config.config_dir}/{filename}")
        existing_zones = json.loads(await load_data(str(filename), hass))

        # get the name and data of the new zone
        new_zone = json.loads(call.data.get("zone"))
        new_name = new_zone["properties"]["name"]

        # check if the zone already exists
        if zone_already_defined(new_name, existing_zones):
            raise ZoneAlreadyExists(f'The zone with name "{new_name}" already exists')

        # append the zone and save it
        existing_zones["features"].append(new_zone)
        new_content = json.dumps(
            {"type": "FeatureCollection", "features": existing_zones["features"]}
        )
        await save_zones(new_content, filepath, hass)

    return add_new_zone
