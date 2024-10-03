from urllib.parse import urlparse
from ..const import CONF_ZONES_URL

import aiohttp
import os

async def validate_url(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False
    except aiohttp.ClientError:
        return False

    return True


async def validate_data(user_input) -> dict:
    """
    Validate the data entered by the user.

    Args:
        user_input: The data entered by the user.

    Returns:
        A dictionary containing the errors.
    """
    errors = {}

    # check if the URL is valid
    for uri in user_input[CONF_ZONES_URL]:
        if uri.startswith("http://") or uri.startswith("https://"):
            parsed = urlparse(uri)
            if not parsed.scheme or not parsed.netloc:
                errors["zones_url"] = "invalid_url"
            else:
                # confirm that it is reachable
                if not await validate_url(uri):
                    errors["zones_url"] = "unreachable_url"

            # confirm that the entities are valid
            if not user_input["registered_entities"]:
                errors["registered_entities"] = "no_entities"

    return errors
