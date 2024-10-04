from urllib.parse import urlparse

import aiohttp
import os

from homeassistant.core import HomeAssistant
from ..const import CONF_ZONES_URL


async def validate_url(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False
    except aiohttp.ClientError:
        return False

    return True


async def validate_data(user_input, hass: HomeAssistant) -> dict:
    """
    Validate the data entered by the user.

    Args:
        user_input: The data entered by the user.

    Returns:
        A dictionary containing the errors.
    """
    errors = {}

    config_dir = hass.config.config_dir

    # check if the URL is valid
    for uri in user_input[CONF_ZONES_URL]:
        if uri.startswith("http://") or uri.startswith("https://"):
            parsed = urlparse(uri)
            if not parsed.scheme or not parsed.netloc:
                errors["zone_urls"] = "invalid_url"
            else:
                # confirm that it is reachable
                if not await validate_url(uri):
                    errors["zone_urls"] = "unreachable_url"
        else:
            if not os.path.exists(f"{config_dir}/{uri}"):
                errors["zone_urls"] = "invalid_path"

            # confirm that the entities are valid
    if "registered_entities" in user_input:
        if not user_input["registered_entities"]:
            errors["registered_entities"] = "no_entities"

    return errors
