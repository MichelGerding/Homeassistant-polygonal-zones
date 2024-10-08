"""The config validation helpers for the polygonal zones integration."""

import os
from urllib.parse import urlparse

import aiohttp

from ..const import CONF_DOWNLOAD_ZONES, CONF_ZONES_URL


async def validate_url(url: str) -> bool:
    """Validate if the url is valid and reachable.

    Args:
        url: The url to check.

    Returns:
        A boolean if the url is reachable and responds with the correct http code.

    """
    try:
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                return False
    except aiohttp.ClientError:
        return False

    return True


async def validate_data(user_input, config_dir) -> dict:
    """Validate the data entered by the user.

    Args:
        user_input: The data entered by the user.
        config_dir: The directory of the homeassistant config.

    Returns:
        A dictionary containing the errors.

    """
    errors = {}

    if len(user_input[CONF_ZONES_URL]) == 0 and not user_input[CONF_DOWNLOAD_ZONES]:
        errors["zone_urls"] = "download_or_no_zones"

    # check if the URL is valid
    for uri in user_input[CONF_ZONES_URL]:
        if uri.startswith(("http://", "https://")):
            parsed = urlparse(uri)
            if not parsed.scheme or not parsed.netloc:
                errors["zone_urls"] = "invalid_url"
            elif not await validate_url(uri):
                errors["zone_urls"] = "unreachable_url"
        elif not os.path.exists(f"{config_dir}/{uri}"):
            errors["zone_urls"] = "invalid_path"

            # confirm that the entities are valid
    if "registered_entities" in user_input:
        if not user_input["registered_entities"]:
            errors["registered_entities"] = "no_entities"

    return errors
