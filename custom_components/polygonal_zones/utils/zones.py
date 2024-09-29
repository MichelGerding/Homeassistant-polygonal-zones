import json
from typing import Optional

import pandas as pd
from shapely.geometry import shape, Point

from .general import load_data


async def get_zones(uri: str) -> pd.DataFrame:
    """
    Get the zones from the geojson file.

    Args:
        uri: The URL to the geojson file.

    Returns:
        A pandas DataFrame containing the zones.
    """
    data = await load_data(uri)
    data = json.loads(data)

    # parse the geojson file into a pandas DataFrame.
    # We only want the relevant information.
    zones = []
    for i, feature in enumerate(data["features"]):
        geometry = shape(feature["geometry"])
        properties = feature["properties"]
        zones.append({"geometry": geometry, **properties})

    return pd.DataFrame(zones)


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
