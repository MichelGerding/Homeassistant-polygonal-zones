"""Config flow for Polygonal zones integrations."""

import logging
from types import MappingProxyType
from typing import Any

from voluptuous import Schema, Required

from homeassistant.config_entries import (
    ConfigEntry,
    OptionsFlow,
    ConfigFlow as EntryConfigFlow,
)
from homeassistant.data_entry_flow import FlowResult, callback
from homeassistant.helpers import selector
from .const import DOMAIN
from .utils import validate_data

_LOGGER = logging.getLogger(__name__)


def build_create_flow(
    defaults: dict[str, Any] | MappingProxyType[str, Any] | None = None
) -> Schema:
    return Schema(
        {
            Required(
                "zone_urls",
                default=defaults.get("zone_urls", ["http://localhost:8000/zones.json"]),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    multiple=True,
                )
            ),
            Required(
                "prioritize_zone_files",
                default=defaults.get("prioritize_zone_files", False),
            ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
            Required(
                "registered_entities",
                default=defaults.get("registered_entities", []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["device_tracker"], multiple=True)
            ),
        }
    )


def build_options_flow(
    defaults: dict[str, Any] | MappingProxyType[str, Any] | None = None
) -> Schema:
    return Schema(
        {
            Required(
                "zone_urls",
                default=defaults.get("zone_urls", ["http://localhost:8000/zones.json"]),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    multiple=True,
                )
            ),
            Required(
                "prioritize_zone_files",
                default=defaults.get("prioritize_zone_files", False),
            ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
        }
    )


class ConfigFlow(EntryConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # validate the input data. If it is valid, create the entry
            errors = await validate_data(user_input, self.hass)
            if not errors:
                return self.async_create_entry(  # noqa
                    title="Polygonal Zones", data=user_input
                )

        user_input = user_input or {}

        return self.async_show_form(  # noqa
            step_id="user",
            data_schema=build_create_flow(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}

        if user_input is not None:
            errors = await validate_data(user_input, self.hass)
            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input
                )
                return self.async_create_entry(title="", data=user_input)  # noqa

        return self.async_show_form(  # noqa
            step_id="init",
            data_schema=build_options_flow(self.config_entry.data),
            errors=errors,
        )
