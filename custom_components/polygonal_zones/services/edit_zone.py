"""definition file for the edit zone action."""

import json
from pathlib import Path

from homeassistant.core import HomeAssistant, ServiceCall

from custom_components.polygonal_zones.services.errors import ZoneDoesNotExists, ZoneFileNotEditable
from ..utils.general import load_data
from ..utils.local_zones import save_zones
from . import get_entities_from_device_id, get_zone_idx


def edit_zone_action_builder(hass: HomeAssistant):
    """Builder for the edit zone action."""

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

        # get the name and data to edit
        old_name = call.data.get("zone_name")
        new_zone = json.loads(call.data.get("zone"))

        idx = get_zone_idx(old_name, existing_zones)
        if idx is None:
            raise ZoneDoesNotExists(f'The zone with name "{old_name}" does not exists')

        # replace the zone and save it
        del existing_zones["features"][idx]
        existing_zones["features"].append(new_zone)

        new_content = json.dumps(
            {"type": "FeatureCollection", "features": existing_zones["features"]}
        )
        await save_zones(new_content, filepath, hass)

    return add_new_zone
