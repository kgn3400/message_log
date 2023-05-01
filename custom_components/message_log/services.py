"""Services for Message log integration."""
from homeassistant.core import HomeAssistant

from .component_api import ComponentApi
from .const import DOMAIN


async def async_setup_services(
    hass: HomeAssistant, component_api: ComponentApi
) -> None:
    """Set up the services for the Message log integration."""

    hass.services.async_register(DOMAIN, "add", component_api.async_add_message_service)
    hass.services.async_register(
        DOMAIN, "remove", component_api.async_remove_messages_service
    )
    hass.services.async_register(
        DOMAIN, "orderby", component_api.async_messagelist_orderby_service
    )
    hass.services.async_register(
        DOMAIN, "show", component_api.async_messagelist_show_service
    )
