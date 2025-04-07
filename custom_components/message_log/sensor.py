"""Sensor for Message log."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, issue_registry as ir, start
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CommonConfigEntry
from .component_api import ComponentApi
from .const import (
    CONF_LISTEN_TO_TIMER_TRIGGER,
    CONF_MARKDOWN_MESSAGE_LIST_COUNT,
    CONF_RESTART_TIMER,
    CONF_SCROLL_MESSAGES_EVERY_MINUTES,
    DOMAIN,
    DOMAIN_NAME,
    TRANSLATION_KEY,
    TRANSLATION_KEY_MISSING_TIMER_ENTITY,
)
from .entity import ComponentEntity
from .hass_util import TimerTrigger, TimerTriggerErrorEnum
from .message_log_settings import MessageItemAttr


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CommonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor setup."""

    await entry.runtime_data.component_api.settings.async_read_settings()

    sensors = []

    sensors.append(MessageLastSensor(hass, entry))
    sensors.append(MessageScrollSensor(hass, entry))

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class MessageLastSensor(ComponentEntity, SensorEntity):
    """Sensor class for Last Message."""

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: CommonConfigEntry,
    ) -> None:
        """Last Message sensor."""

        super().__init__(entry.runtime_data.coordinator, entry)

        self.component_api: ComponentApi = entry.runtime_data.component_api
        self.hass: HomeAssistant = hass
        self.entry: CommonConfigEntry = entry

        self._name = "Last message"
        self._unique_id = "last_message"
        self.translation_key = TRANSLATION_KEY

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
            attr["last_message_level"] = self.component_api.message_level_last

        if self.component_api.message_source_last:
            attr["last_message_source"] = self.component_api.message_source_last

        if len(self.component_api.settings.message_list) > 0:
            attr["last_message_added_at"] = self.component_api.settings.message_list[
                0
            ].added_at.isoformat()

        if self.component_api.highest_message_level:
            attr["highest_message_level"] = self.component_api.highest_message_level

        if self.component_api.markdown:
            attr["markdown"] = self.component_api.markdown

        if self.component_api.markdown_message_list:
            attr["markdown_message_list"] = self.component_api.markdown_message_list

        if self.component_api.markdown_message_settings:
            attr["markdown_settings"] = self.component_api.markdown_message_settings

        message_list_attr: list[MessageItemAttr] = [
            MessageItemAttr(
                item.message,
                item.message_level,
                item.icon,
                item.notify,
                item.added_at,
            )
            for item in self.component_api.settings.message_list
        ]
        attr["message_list"] = message_list_attr[
            : int(self.entry.options.get(CONF_MARKDOWN_MESSAGE_LIST_COUNT, 10))
        ]

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

        self.hass.bus.async_listen(
            dr.EVENT_DEVICE_REGISTRY_UPDATED,
            self._handle_device_registry_updated,
        )
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------
    @callback
    async def _handle_device_registry_updated(
        self, event: Event[dr.EventDeviceRegistryUpdatedData]
    ) -> None:
        """Handle when device registry updated."""

        if event.data["action"] == "remove":
            await self.component_api.settings.async_remove_settings()


# ------------------------------------------------------
# ------------------------------------------------------
class MessageScrollSensor(ComponentEntity, SensorEntity):
    """Sensor class for Message scroll."""

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: CommonConfigEntry,
    ) -> None:
        """Scroll Message sensor."""

        super().__init__(entry.runtime_data.coordinator, entry)

        self.hass: HomeAssistant = hass
        self.entry: CommonConfigEntry = entry
        self.component_api: ComponentApi = entry.runtime_data.component_api

        # self.refresh_type: RefreshType = RefreshType.NORMAL

        self._name = "Scroll message"
        self._unique_id = "scroll_message"

        self.translation_key = TRANSLATION_KEY

        self.timer_trigger = TimerTrigger(
            self,
            timer_entity=self.entry.options.get(CONF_LISTEN_TO_TIMER_TRIGGER, ""),
            duration=timedelta(
                minutes=self.entry.options.get(CONF_SCROLL_MESSAGES_EVERY_MINUTES, 0.5)
            ),
            callback_trigger=self.async_handle_timer_finished,
            auto_restart=self.entry.options.get(CONF_RESTART_TIMER, ""),
        )
        self.coordinator.update_interval = None

    # ------------------------------------------------------------------
    async def async_handle_timer_finished(self, error: TimerTriggerErrorEnum) -> None:
        """Handle timer finished."""

        if error:
            match error:
                case TimerTriggerErrorEnum.MISSING_TIMER_ENTITY:
                    ir.async_create_issue(
                        self.hass,
                        DOMAIN,
                        DOMAIN_NAME + datetime.now().isoformat(),
                        issue_domain=DOMAIN,
                        is_fixable=False,
                        severity=ir.IssueSeverity.WARNING,
                        translation_key=TRANSLATION_KEY_MISSING_TIMER_ENTITY,
                        translation_placeholders={
                            "timer_entity": self.entry.options.get(
                                CONF_LISTEN_TO_TIMER_TRIGGER, ""
                            ),
                            "entity": self.entity_id,
                        },
                    )
                case _:
                    pass
            return

        await self.coordinator.async_refresh()

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

        self.async_on_remove(start.async_at_started(self.hass, self.async_hass_started))

    # ------------------------------------------------------
    async def async_hass_started(self, _event: Event) -> None:
        """Hass started."""
