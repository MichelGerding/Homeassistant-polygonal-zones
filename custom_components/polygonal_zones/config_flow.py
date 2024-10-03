"""Config flow for Polygonal zones integrations."""

import logging

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_SCHEMA, DOMAIN
from .utils import validate_data

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # validate the input data. If it is valid, create the entry
            errors = await validate_data(user_input)

            if not errors:
                return self.async_create_entry(title="polygonal_zones", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=CONF_SCHEMA,
            errors=errors,
        )
