"""Notify entity for Message log."""

from homeassistant.components.notify import NotifyEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import CommonConfigEntry
from .const import DOMAIN_NAME
from .entity import ComponentEntity
from .message_log_settings import MessageItem


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CommonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor setup."""

    async_add_entities([MessageLogNotifyEntity(hass, entry)])


class MessageLogNotifyEntity(ComponentEntity, NotifyEntity):
    """Implement the notify entity for message log."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        hass: HomeAssistant,
        entry: CommonConfigEntry,
    ) -> None:
        """Initialize the entity."""
        NotifyEntity.__init__(self)
        ComponentEntity.__init__(self, hass, entry)
        self.hass: HomeAssistant = hass
        self.entry: CommonConfigEntry = entry
        self.coordinator: DataUpdateCoordinator = entry.runtime_data.coordinator
        self._attr_unique_id = DOMAIN_NAME
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN_NAME, DOMAIN_NAME)},
            name=DOMAIN_NAME + " Notifier",
        )

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send a message."""
        await self.entry.runtime_data.component_api.async_add_message(
            MessageItem(message)
        )
