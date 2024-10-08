"""Custom errors for the polygonal zones integration."""

from homeassistant.exceptions import HomeAssistantError


class ZoneFileNotEditable(HomeAssistantError):
    """Error to signal that the source zone file for the entities is not editable."""


class ZoneAlreadyExists(HomeAssistantError):
    """Error to signal that the zone already exists in that file."""


class ZoneDoesNotExists(HomeAssistantError):
    """Error to signal that the zone already exists in that file."""
