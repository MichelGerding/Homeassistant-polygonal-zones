"""Helper functions to handle local zones."""

import json
from pathlib import Path

import pandas as pd
from shapely import to_geojson

from homeassistant.core import HomeAssistant

from .zones import get_zones


def zones_to_geojson(zones: pd.DataFrame):
    """Convert the zones to GeoJSON."""
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": zone.name,
                        "priority": zone.priority,
                    },
                    "geometry": json.loads(to_geojson(zone.geometry)),
                }
                for zone in zones.itertuples()
            ],
        }
    )


async def download_zones(
    source_uris: list[str], dest_uri: Path, prioritize: bool, hass: HomeAssistant
):
    """Download the zones in sources_uris to."""
    zones = await get_zones(source_uris, hass, prioritize)
    geo_json = zones_to_geojson(zones)

    dest_uri.parent.mkdir(parents=True, exist_ok=True)

    await save_zones(geo_json, dest_uri, hass)


async def save_zones(geojson: str, destination: Path, hass: HomeAssistant):
    """Save the GeoJSON string to a file. This will overwrite the entire file.

    Args:
        geojson: The GeoJSON string to save
        destination: Path of the file to save the GeoJSON string in
        hass: The homeassistant instance.

    """

    file = await hass.async_add_executor_job(open, destination, "w")
    file.write(geojson)
    file.close()
