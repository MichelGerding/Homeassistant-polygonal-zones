"""definition file for the delete zone action."""

import json
from pathlib import Path

from homeassistant.core import HomeAssistant, ServiceCall
from .helpers import get_entities_from_device_id, get_zone_idx
from .errors import (
    ZoneDoesNotExists,
    ZoneFileNotEditable,
)
from ..utils.general import load_data
from ..utils.local_zones import save_zones


def delete_zone_action_builder(hass: HomeAssistant):
    """Builder for the delete zone action."""

    async def delete_new_zone(call: ServiceCall):
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
        # check if the zone already exists
        new_name = call.data.get("zone_name")
        if idx := get_zone_idx(new_name, existing_zones) is None:
            raise ZoneDoesNotExists(f'The zone with name "{new_name}" does not exists')

        # append the zone and save it
        del existing_zones["features"][idx]
        new_content = json.dumps(
            {"type": "FeatureCollection", "features": existing_zones["features"]}
        )
        await save_zones(new_content, filepath, hass)

    return delete_new_zone
