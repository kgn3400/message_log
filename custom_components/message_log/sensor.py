"""Sensor for Message log."""

from __future__ import annotations

from homeassistant.components.sensor import (  # SensorDeviceClass,; SensorEntityDescription,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .component_api import ComponentApi
from .const import DOMAIN
from .entity import ComponentEntity


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor setup."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    component_api: ComponentApi = hass.data[DOMAIN][entry.entry_id]["component_api"]

    sensors = []

    sensors.append(MessageLastSensor(coordinator, entry, component_api))
    sensors.append(MessageScrollSensor(coordinator, entry, component_api))

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class MessageLastSensor(ComponentEntity, SensorEntity):
    """Sensor class for Last Message."""

    # ------------------------------------------------------
    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        component_api: ComponentApi,
    ) -> None:
        """Last Message sensor."""

        super().__init__(coordinator, entry)

        self.component_api = component_api
        self.coordinator = coordinator

        self._name = "Last message"
        self._unique_id = "last_message"

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name."""

        return self._name

    # ------------------------------------------------------
    @property
    def icon(self) -> str:
        """Icon."""

        return self.component_api.message_last_icon

    # ------------------------------------------------------
    @property
    def native_value(self) -> str:
        """Native value."""

        return self.component_api.message_last

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes."""

        attr: dict = {}

        if self.component_api.message_level_last:
            attr["message_level_last"] = self.component_api.message_level_last

        if self.component_api.highest_message_level:
            attr["highest__message_level"] = self.component_api.highest_message_level

        if self.component_api.markdown:
            attr["markdown"] = self.component_api.markdown

        if self.component_api.markdown_message_list:
            attr["markdown_list"] = self.component_api.markdown_message_list

        if self.component_api.markdown_message_settings:
            attr["markdown_settings"] = self.component_api.markdown_message_settings

        return attr

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id.

        Returns:
            str: Unique  id

        """
        return self._unique_id

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


# ------------------------------------------------------
# ------------------------------------------------------
class MessageScrollSensor(ComponentEntity, SensorEntity):
    """Sensor class for Message scroll."""

    # ------------------------------------------------------
    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        component_api: ComponentApi,
    ) -> None:
        """Scroll Message sensor."""

        super().__init__(coordinator, entry)

        self.component_api = component_api
        self.coordinator = coordinator

        self._name = "Scroll message"
        self._unique_id = "scroll_message"

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name."""

        return self._name

    # ------------------------------------------------------
    @property
    def icon(self) -> str:
        """Icon."""

        return self.component_api.message_scroll_icon

    # ------------------------------------------------------
    @property
    def native_value(self) -> str:
        """Native value."""

        return self.component_api.message_scroll

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes."""

        return {}

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id.

        Returns:
            str: Unique  id

        """
        return self._unique_id

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
