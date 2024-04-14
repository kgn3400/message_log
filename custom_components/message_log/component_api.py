"""Component api."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_MARKDOWN_MESSAGE_LIST_COUNT,
    CONF_ORDER_BY_MESSAGE_LEVEL,
    CONF_REMOVE_MESSAGE_AFTER_HOURS,
    CONF_SCROLL_THROUGH_LAST_MESSAGES_COUNT,
    DOMAIN,
)
from .message_log_settings import (
    MessageItem,
    MessageLevel,
    MessageListOrderBy,
    MessageListShow,
    MessageLogSettings,
)


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
        self.markdown_message_settings: str = ""
        self.message_list_sorted: list[MessageItem] = []
        self.settings: MessageLogSettings = MessageLogSettings(
            self.entry.options.get(CONF_ORDER_BY_MESSAGE_LEVEL, True)
        )
        self.settings.read_settings(hass.config.path(STORAGE_DIR, DOMAIN))

    # ------------------------------------------------------------------
    def relative_time(self, date_time: datetime) -> str:
        """Relative time."""

        now = datetime.now()
        diff = now - date_time

        if diff < timedelta(seconds=10):
            return "lige nu"
        elif diff < timedelta(minutes=1):
            return f"for {diff.seconds} sekund siden"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"for {minutes} minut{'ter' if minutes != 1 else ''} siden"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"for {hours} time{'r' if hours != 1 else ''} siden"
        elif diff < timedelta(weeks=1):
            days = diff.days
            return f"for {days} dag{'e' if days != 1 else ''} siden"

        weeks = diff.days // 7
        return f"for {weeks} uge{'r' if weeks != 1 else ''} siden"

    # ------------------------------------------------------------------
    async def async_remove_messages_service(self, call: ServiceCall) -> None:
        """Remove nessage service."""
        if "message_level" in call.data:
            tmp_message_level: MessageLevel = MessageLevel[
                call.data.get("message_level", "INFO").upper()
            ]

            for index, item in reversed(list(enumerate(self.settings.message_list))):
                if item.message_level == tmp_message_level:
                    del self.settings.message_list[index]
        else:
            self.settings.message_list.clear()

        self.settings.set_highest_message_level()
        self.settings.write_settings()
        await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_add_message_service(self, call: ServiceCall) -> None:
        """Message log add service."""

        tmp_dict = call.data.copy()

        if "remove_after" not in tmp_dict:
            tmp_dict["remove_after"] = self.entry.options.get(
                CONF_REMOVE_MESSAGE_AFTER_HOURS, 24
            )

        if "added_at" in tmp_dict:
            tmp_dict["added_at"] = datetime.strptime(
                tmp_dict["added_at"],
                # 2023-04-13 22:00:00
                "%Y-%m-%d %H:%M:%S",
            )

            # Hvorfor er denne bid kun nødvendig i udviklings miløet ??
            # timezonex = pytz.timezone(self.hass.config.time_zone)
            # tmp_off = timezonex.localize(tmp_dict["added_at"]).utcoffset()
            # tmp_dict["added_at"] -= timedelta(seconds=tmp_off.total_seconds())

        self.settings.message_list.insert(0, MessageItem(**tmp_dict))
        self.settings.set_highest_message_level()
        self.settings.write_settings()
        await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_messagelist_orderby_service(self, call: ServiceCall) -> None:
        """Message list orderby."""

        if call.data.get("orderby") is None:
            self.settings.message_list_orderby = MessageListOrderBy(
                self.settings.message_list_orderby.succ(True)
            )
        else:
            self.settings.message_list_orderby = MessageListOrderBy[
                call.data.get("orderby", "MESSAGE_LEVEL").upper()
            ]

            if len(self.settings.message_list) > 1:
                self.scroll_message_pos = -1

        self.settings.write_settings()
        await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_messagelist_show_service(self, call: ServiceCall) -> None:
        """Message list show."""

        if call.data.get("show") is None:
            self.settings.message_list_show = MessageListShow(
                self.settings.message_list_show.succ(True)
            )
        else:
            self.settings.message_list_orderby = MessageListOrderBy[
                call.data.get("show", "ALL").upper()
            ]

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
            self.settings.set_highest_message_level()
            self.settings.write_settings()

    # ------------------------------------------------------------------
    def update_markdown(self) -> None:
        """Update markdown."""
        self.create_sorted_message_list(self.settings.message_list_orderby)
        self.create_markdown_latest_and_scroll()

        self.create_sorted_message_list(
            self.settings.message_list_orderby, self.settings.message_list_show
        )
        self.create_markdown_message_list()
        self.create_markdown_message_settings()

        self.message_list_sorted.clear()

    # ------------------------------------------------------------------
    def create_markdown_latest_and_scroll(self) -> None:
        """Markdown latest and scroll."""
        # Latest message
        if len(self.settings.message_list) > 0:
            item: MessageItem = self.settings.message_list[0]

            self.markdown = (
                f'## <font color={self.settings.highest_message_level_color}>  <ha-icon icon="mdi:message-outline"></ha-icon></font> Besked\n'
                f'-  <font color={item.message_level_color}>  <ha-icon icon="{item.icon}"></ha-icon></font> <font size=3>Sidste besked: **{item.message}**</font>\n'
                f"Modtaget {self.relative_time(item.added_at)}.\n\n"
            )

            # Scroll message
            if len(self.message_list_sorted) > 1:
                while (
                    self.settings.message_list[0].added_at
                    == self.message_list_sorted[self.scroll_message_pos].added_at
                ):
                    self.update_scroll_message_pos()

                item: MessageItem = self.message_list_sorted[self.scroll_message_pos]
                self.markdown += (
                    f'- <font color={item.message_level_color}>  <ha-icon icon="{item.icon}"></ha-icon></font> Beskeder: **{item.message}**\n'
                    f"Modtaget {self.relative_time(item.added_at)}. "
                )
        else:
            self.markdown = f'## <font color={MessageLevel.INFO.color}>  <ha-icon icon="mdi:message-outline"></ha-icon></font> Besked\n'

    # ------------------------------------------------------------------
    def create_markdown_message_list(self) -> None:
        """Markdown message list."""
        # Create markdown list
        if len(self.message_list_sorted) > 0:
            count_pos: int = 1
            self.markdown_message_list = f'## <font color={self.settings.highest_message_level_color}>  <ha-icon icon="mdi:message-outline"></ha-icon></font> Beskeder\n'

            for item in self.message_list_sorted:
                if count_pos > self.entry.options.get(
                    CONF_MARKDOWN_MESSAGE_LIST_COUNT, 10
                ):
                    break

                self.markdown_message_list += (
                    f'- <font color={item.message_level_color}>  <ha-icon icon="{item.icon}"></ha-icon></font> **{item.message}**\n'
                    f"Modtaget {self.relative_time(item.added_at)}.\n"
                )
                count_pos += 1
        else:
            self.markdown_message_list = f'## <font color={MessageLevel.INFO.color}>  <ha-icon icon="mdi:message-outline"></ha-icon></font> Besked\n'

    # ------------------------------------------------------------------
    def create_markdown_message_settings(self) -> None:
        """Create markdown for settings."""
        orderby: str = (
            "Modtaget"
            if self.settings.message_list_orderby == MessageListOrderBy.ADDED_AT
            else "Relevans"
        )

        match self.settings.message_list_show:
            case MessageListShow.ALL:
                show: str = "Alt"
            case MessageListShow.INFO:
                show: str = "Info"
            case MessageListShow.ATTENTION:
                show: str = "Vigtigt"
            case MessageListShow.WARNING:
                show: str = "Advarsel"
            case MessageListShow.ERROR:
                show: str = "Fejl"

        self.markdown_message_settings = (
            "|Opsætning| |\n"
            "| --- | ----------- |\n"
            f"| Sortering | : {orderby} |\n"
            f"| Vis | : {show} |"
        )

    # ------------------------------------------------------------------
    def create_sorted_message_list(
        self,
        orderby: MessageListOrderBy = MessageListOrderBy.MESSAGE_LEVEL,
        show: MessageListShow = MessageListShow.ALL,
    ) -> None:
        """Create sorted message list."""
        self.message_list_sorted.clear()

        if orderby == MessageListOrderBy.MESSAGE_LEVEL:
            for message_level in reversed(MessageLevel):
                self.message_list_sorted.extend(
                    [
                        x
                        for x in self.settings.message_list
                        if x.message_level == message_level
                        and (
                            show == MessageListShow.ALL
                            or x.message_level.name == show.name
                        )
                    ]
                )

        else:
            self.message_list_sorted.extend(
                [
                    x
                    for x in self.settings.message_list
                    if show == MessageListShow.ALL or x.message_level.name == show.name
                ]
            )

    # ------------------------------------------------------------------
    def update_scroll_message_pos(self) -> None:
        """Update scroll message pos."""
        if len(self.settings.message_list) > 1:
            self.scroll_message_pos += 1

            if self.scroll_message_pos >= len(
                self.settings.message_list
            ) or self.scroll_message_pos >= self.entry.options.get(
                CONF_SCROLL_THROUGH_LAST_MESSAGES_COUNT, 5
            ):
                self.scroll_message_pos = 0
        else:
            self.scroll_message_pos = 0

    # ------------------------------------------------------------------
    def get_message(self, num: int = 0) -> str:
        """Get Message."""
        return (
            self.settings.message_list[num].message
            if len(self.settings.message_list) > num
            else ""
        )

    # ------------------------------------------------------------------
    @property
    def message_last(self) -> str:
        """Message last."""
        return self.get_message(0)

    # ------------------------------------------------------------------
    @property
    def message_last_icon(self) -> str:
        """Message last icon."""
        if len(self.settings.message_list) > 0:
            return self.settings.message_list[0].icon

        return "mdi:message-off-outline"

    # ------------------------------------------------------------------
    @property
    def message_level_last(self) -> str:
        """Message level last."""
        return (
            self.settings.message_list[0].message_level.name.capitalize()
            if len(self.settings.message_list) > 0
            else ""
        )

    # ------------------------------------------------------------------
    @property
    def message_level_color_last(self) -> str:
        """Message level color last."""
        return (
            self.settings.message_list[0].message_level.color
            if len(self.settings.message_list) > 0
            else MessageLevel.INFO.color
        )

    # ------------------------------------------------------------------
    @property
    def highest_message_level(self) -> str:
        """Highest message level."""
        return self.settings.highest_message_level.name.capitalize()

    # ------------------------------------------------------------------
    @property
    def message_scroll(self) -> str:
        """Get scroll message."""

        if len(self.settings.message_list) > 1:
            return self.settings.message_list[self.scroll_message_pos].message

        return ""

    # ------------------------------------------------------------------
    @property
    def message_scroll_icon(self) -> str:
        """Get scroll message icon."""

        if len(self.settings.message_list) > 1:
            return self.settings.message_list[self.scroll_message_pos].icon

        return "mdi:message-off-outline"
