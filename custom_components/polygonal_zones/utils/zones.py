import json
import numpy as np
import pandas as pd
from shapely.geometry import shape, Point
from shapely.geometry.polygon import Polygon
from typing import Optional

from script.lint_and_test import printc
from .general import load_data


def get_distance(polygon: Polygon, point: Point) -> float:
    """
    Get the distance between a point and a polygon in meters.

    Args:
        polygon: The polygon.
        point: The point.

    Returns:
        The distance between the point and the polygon in meters.
    """
    polygon_centroid = polygon.centroid
    # get the haversine distance between the point and the polygon centroid
    distance = np.linalg.norm(
        [polygon_centroid.x - point.x, polygon_centroid.y - point.y]
    )

    return distance * 111320

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


def get_locations_zone(
    lat: float, lon: float, acc: float, zones: pd.DataFrame
) -> Optional[dict]:
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
        zone = posible_zones.iloc[0]
        distance = get_distance(zone["geometry"], gps_point)
        return {
            "name": zone["name"],
            "distance": distance * 111320,
        }

    # get the distances to the potential zones using the uclidean distance to the cetnroid
    distances = posible_zones["geometry"].apply(lambda x: get_distance(x, gps_point))

    closest_zone_index = distances.idxmin()

    # get the amount of zones that have the same distance
    closest_zones = distances[distances == distances[closest_zone_index]]
    print(closest_zones)
    zone = zones.loc[closest_zone_index]
    distance = distances[closest_zone_index]
    return {
        "name": zone["name"],
        "distance": distance,
    }
