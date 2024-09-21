"""Config flow for Polygonal zones integrations."""

import logging
from urllib.parse import urlparse

import aiohttp
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_SCHEMA, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_data(user_input) -> dict:
    # confirm that the URL is valid
    errors = {}

    parsed = urlparse(user_input["zones_url"])
    if not parsed.scheme or not parsed.netloc:
        errors["zones_url"] = "invalid_url"
    else:
        # confirm that it is reachable
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(user_input["zones_url"]) as response:
                    if response.status != 200:
                        errors["zones_url"] = "unreachable_url"
        except aiohttp.ClientError:
            errors["zones_url"] = "unreachable_url"

    # confirm that the entities are valid
    if not user_input["registered_entities"]:
        errors["registered_entities"] = "no_entities"

    return errors


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # validate the input data. If it is valid, create the entry
            errors = await validate_data(user_input)
            if not errors:
                return self.async_create_entry(
                    title="polygonal_zones",
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=CONF_SCHEMA,
            description_placeholders={"zones_url_label": "Enter the URL to your zones file"},
            errors=errors,
        )
