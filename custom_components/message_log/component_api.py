"""Component api."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_MARKDOWN_MESSAGE_LIST_COUNT,
    CONF_REMOVE_MESSAGE_AFTER_HOURS,
    DOMAIN,
)
from .message_log_settings import InfoLevels, MessageItem, MessageLogSettings


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class ComponentApi:
    """Message log interface."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Component api."""
        self.hass = hass
        self.entry: ConfigEntry = entry

        self.coordinator: DataUpdateCoordinator
        self.scroll_message_pos: int = -1
        self.markdown: str = ""
        self.markdown_message_list: str = ""
        self.settings: MessageLogSettings = MessageLogSettings()
        self.settings.read_settings(hass.config.path(STORAGE_DIR, DOMAIN))

    # ------------------------------------------------------------------
    def relative_time(self, date_time: datetime):
        """Relative time."""

        now = datetime.now()
        diff = now - date_time

        if diff < timedelta(seconds=10):
            return "lige nu"
        elif diff < timedelta(minutes=1):
            return f"{diff.seconds} sekund siden"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"{minutes} minut{'ter' if minutes != 1 else ''} siden"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"{hours} time{'r' if hours != 1 else ''} siden"
        elif diff < timedelta(weeks=1):
            days = diff.days
            return f"{days} dag{'e' if days != 1 else ''} siden"
        else:
            weeks = diff.days // 7
            return f"{weeks} uge{'r' if weeks != 1 else ''} siden"

    # ------------------------------------------------------------------
    async def async_remove_messages_service(self, call: ServiceCall) -> None:
        """Remove nessage service."""
        self.settings.message_list.clear()
        self.settings.write_settings()
        await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_add_message_service(self, call: ServiceCall) -> None:
        """Message log add service."""
        tmp_dict = call.data.copy()

        if tmp_dict.get("remove_after", None) is None:
            tmp_dict["remove_after"] = self.entry.options.get(
                CONF_REMOVE_MESSAGE_AFTER_HOURS, 24
            )

        self.settings.message_list.insert(0, MessageItem(**tmp_dict))
        self.settings.write_settings()
        await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_update(self) -> None:
        """Message log Update."""

        self.remove_outdated()
        self.update_scroll_message_pos()
        self.update_markdown()

    # ------------------------------------------------------------------
    def remove_outdated(self) -> None:
        """Remove outdated."""
        save_settings: bool = False

        for index, item in reversed(list(enumerate(self.settings.message_list))):
            if (item.added_at + item.remove_after) < datetime.now():
                save_settings = True
                del self.settings.message_list[index]

        if save_settings:
            self.settings.write_settings()

    # ------------------------------------------------------------------
    def update_markdown(self) -> None:
        """Update markdown."""

        if len(self.settings.message_list) > 0:
            match self.settings.message_list[0].info_level:
                case InfoLevels.INFO:
                    tmp_col: str = "limegreen"
                case InfoLevels.WARNING:
                    tmp_col = "orange"
                case InfoLevels.ERROR:
                    tmp_col = "orangered"
                case _:
                    tmp_col = "blue"

            self.markdown = (
                "## Besked\n"
                f'-  <font color={tmp_col}>  <ha-icon icon="{self.settings.message_list[0].icon}"></ha-icon></font> <font size=3>Sidste besked: **{self.settings.message_list[0].message}**</font>\n'
                f"Modtaget for {self.relative_time(self.settings.message_list[0].added_at)}.\n\n"
            )

            if len(self.settings.message_list) > 1:
                match self.settings.message_list[self.scroll_message_pos].info_level:
                    case InfoLevels.INFO:
                        tmp_col: str = "limegreen"
                    case InfoLevels.WARNING:
                        tmp_col = "orange"
                    case InfoLevels.ERROR:
                        tmp_col = "orangered"
                    case _:
                        tmp_col = "blue"

                self.markdown += (
                    f'- <font color={tmp_col}>  <ha-icon icon="{self.settings.message_list[self.scroll_message_pos].icon}"></ha-icon></font> Beskeder: **{self.settings.message_list[self.scroll_message_pos].message}**\n'
                    f"Modtaget for {self.relative_time(self.settings.message_list[self.scroll_message_pos].added_at)}. "
                )
        else:
            self.markdown = "## Besked\n"

        if len(self.settings.message_list) > 0:
            count_pos: int = 1
            self.markdown_message_list = "## Beskeder\n"

            for item in self.settings.message_list:
                if count_pos > self.entry.options.get(
                    CONF_MARKDOWN_MESSAGE_LIST_COUNT, 10
                ):
                    break

                match item.info_level:
                    case InfoLevels.INFO:
                        tmp_col: str = "limegreen"
                    case InfoLevels.WARNING:
                        tmp_col = "orange"
                    case InfoLevels.ERROR:
                        tmp_col = "orangered"
                    case _:
                        tmp_col = "blue"

                self.markdown_message_list += (
                    f'- <font color={tmp_col}>  <ha-icon icon="{item.icon}"></ha-icon></font> **{item.message}**\n'
                    f"Modtaget for {self.relative_time(item.added_at)}.\n"
                )
                count_pos += 1
        else:
            self.markdown_message_list = "## Beskeder\n"

    # ------------------------------------------------------------------
    def update_scroll_message_pos(self) -> None:
        """Update scroll message pos."""
        if len(self.settings.message_list) > 0:
            self.scroll_message_pos += 1

            if self.scroll_message_pos >= len(self.settings.message_list):
                self.scroll_message_pos = 0
        else:
            self.scroll_message_pos = -1

    # ------------------------------------------------------------------
    def get_message(self, num: int = 0) -> str:
        """Get Message."""
        return (
            self.settings.message_list[num].message
            if len(self.settings.message_list) > num
            else ""
        )

    # ------------------------------------------------------------------
    def get_scroll_message(self, num: int = 0) -> str:
        """Get scroll message."""

        if len(self.settings.message_list) > 0:
            return self.settings.message_list[self.scroll_message_pos].message

        return ""
