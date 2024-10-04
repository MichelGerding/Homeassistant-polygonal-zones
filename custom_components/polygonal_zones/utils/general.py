import aiohttp

from homeassistant.core import HomeAssistant


async def load_data(uri: str, hass: HomeAssistant) -> str:
    if uri.startswith("http") or uri.startswith("https"):
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                return await response.text()
    else:
        config_dir = hass.config.config_dir
        file = await hass.async_add_executor_job(open, f"{config_dir}/{uri}", "r")
        data = file.read()
        file.close()
        return data


def event_should_trigger(event, entity_id) -> bool:
    """
    Decide if the event should trigger the sensor.

    Args:
        event: The event to check.
        entity_id: The entity id to check.

    Returns:
        True if the event should trigger the sensor, False otherwise.
    """
    # check if it is the entity we should listen to.
    if event.data["entity_id"] != entity_id:
        return False

    old_state = event.data["old_state"].attributes
    new_state = event.data["new_state"].attributes

    # check if one or more of the important data has been updated
    return (
        old_state["latitude"] != new_state["latitude"]
        or old_state["longitude"] != new_state["longitude"]
        or old_state["gps_accuracy"] != new_state["gps_accuracy"]
    )
