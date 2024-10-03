import json
from typing import Optional

import numpy as np
import pandas as pd
from shapely.geometry import shape, Point
from shapely.geometry.polygon import Polygon
from homeassistant.core import HomeAssistant

from .general import load_data


def haversine_distances(point: np.array, coordinates: np.array) -> np.array:
    """
    Calculate Haversine distances from a single point to multiple points.

    Args:
        point: NumPy array of shape (2,) containing [latitude, longitude] of the single point (in degrees)
        coordinates: NumPy array of shape (n, 2) containing latitudes and longitudes of multiple points (in degrees)

    Returns:
        Array of distances in kilometers
    """
    R = 6371000  # Radius of the earth in meters

    lat1, lon1 = np.radians(point)
    lats2, lons2 = np.radians(coordinates).T

    dlat = lats2 - lat1
    dlon = lons2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lats2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


def get_distance_to_exterior_points(polygon: Polygon, point: Point) -> float:
    """
    Get the haversine distance between a point and the closest exterior point of a polygon

    Args:
        polygon: A shapely Polygon object
        point: A shapely Point object

    Returns:
        The distance in kilometers
    """
    polygon_points = np.array(polygon.exterior.coords)
    point_coords = np.array([point.x, point.y])
    distances = haversine_distances(point_coords, polygon_points)
    return min(distances)


def get_distance_to_centroid(polygon: Polygon, point: Point) -> float:
    """
    Get the haversine distance between a point and the centroid of a polygon

    Args:
        polygon: A shapely Polygon object
        point: A shapely Point object

    Returns:
        The distance in kilometers
    """
    polygon_centroid = np.array(polygon.centroid.xy).reshape(1, -1)[0]
    point = np.array([point.x, point.y])

    distance = haversine_distances(point, polygon_centroid)
    return distance


async def get_zones(uris: str, hass: HomeAssistant, prioritize) -> pd.DataFrame:
    """
    Get the zones from the geojson file.

    Args:
        uris: The URL to the geojson file.

    Returns:
        A pandas DataFrame containing the zones.
    """
    zones = []

    for idx, uri in enumerate(uris):
        data = await load_data(uri, hass)
        data = json.loads(data)

        priority = idx if prioritize else 0

        # parse the geojson file into a pandas DataFrame.
        # We only want the relevant information.
        for i, feature in enumerate(data["features"]):
            geometry = shape(feature["geometry"])
            properties = feature["properties"]
            zones.append({"geometry": geometry, "priority": priority, **properties, })

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
        centroid_distance = get_distance_to_centroid(zone["geometry"], gps_point)
        return {
            "name": zone["name"],
            "distance_to_centroid": centroid_distance,
        }

    # filter to the lowest priority zones
    posible_zones = posible_zones[posible_zones["priority"] == posible_zones["priority"].min()]

    # get the distances to the potential zones using the uclidean distance to the cetnroid
    distances = posible_zones["geometry"].apply(lambda x: get_distance_to_exterior_points(x, gps_point))

    closest_zone_index = distances.idxmin()

    # get the amount of zones that have the same distance
    zone = zones.loc[closest_zone_index]
    centroid_distance = get_distance_to_centroid(zone["geometry"], gps_point)
    return {
        "name": zone["name"],
        "distance_to_centroid": centroid_distance,
    }
