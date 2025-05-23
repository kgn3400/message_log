"""MessageLogSettings."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from homeassistant.core import HomeAssistant

from .const import STORAGE_KEY, STORAGE_VERSION
from .hass_util import EnumExt, StorageJson


# ------------------------------------------------------
# ------------------------------------------------------
class MessageLevel(EnumExt):
    """Message levels."""

    INFO = 10
    ATTENTION = 20
    WARNING = 30
    ERROR = 40

    # ------------------------------------------------------
    @property
    def color(self) -> str:
        """Color."""
        message_level_to_color___: dict = {
            self.INFO.name: "limegreen",
            self.ATTENTION.name: "deepskyblue",
            self.WARNING.name: "orange",
            self.ERROR.name: "orangered",
        }

        return message_level_to_color___[self.name]


# ------------------------------------------------------
# ------------------------------------------------------
class MessageListShow(EnumExt):
    """Message list show."""

    INFO = 10
    ATTENTION = 20
    WARNING = 30
    ERROR = 40
    ALL = 100


# ------------------------------------------------------
# ------------------------------------------------------
class MessageListOrderBy(EnumExt):
    """Message list show."""

    ADDED_AT = 10
    MESSAGE_LEVEL = 20


# ------------------------------------------------------
# ------------------------------------------------------
@dataclass
class MessageItem:
    """Message item."""

    # ------------------------------------------------------------------

    def __init__(
        self,
        message: str,
        message_level: MessageLevel | str = MessageLevel.INFO,
        icon: str = "mdi:message-badge-outline",
        remove_after: float = 24,
        notify: bool = False,
        added_at: datetime | None = None,
        source: str = "",
    ) -> None:
        """Message data."""
        tmp_message_level: MessageLevel = MessageLevel.INFO

        if isinstance(message_level, str):
            try:
                tmp_message_level = MessageLevel[message_level.upper()]
            except KeyError:
                tmp_message_level = MessageLevel.INFO

        self.message: str = message
        self.message_level: MessageLevel = tmp_message_level
        self.icon: str = icon
        self.remove_after: datetime = datetime.now(UTC) + timedelta(hours=remove_after)
        self.notify: bool = notify

        if added_at is None:
            self.added_at: datetime = datetime.now().astimezone(UTC)
        else:
            self.added_at: datetime = added_at

        self.source: str = source

    # ------------------------------------------------------
    @property
    def message_level_color(self) -> str:
        """Message level color."""
        return self.message_level.color


# ------------------------------------------------------
# ------------------------------------------------------
@dataclass
class MessageItemAttr:
    """Message item attribute."""

    # ------------------------------------------------------------------

    def __init__(
        self,
        message: str,
        message_level: MessageLevel = MessageLevel.INFO,
        icon: str = "mdi:message-badge-outline",
        notify: bool = False,
        added_at: datetime | None = None,
        source: str = "",
    ) -> None:
        """Message data."""

        self.message: str = message
        self.message_level: str = message_level.name.capitalize()
        self.icon: str = icon
        self.notify: bool = notify

        if added_at is None:
            self.added_at: datetime = datetime.now().isoformat()
        else:
            self.added_at: datetime = added_at.isoformat()

        self.source: str = source

    # ------------------------------------------------------
    @property
    def message_level_color(self) -> str:
        """Message level color."""
        return self.message_level.color


# ------------------------------------------------------
# ------------------------------------------------------
@dataclass
class MessageLogSettings(StorageJson):
    """MessageLogSettings."""

    # ------------------------------------------------------
    def __init__(self, hass: HomeAssistant, orderby_message_level: bool = True) -> None:
        """Message log settings."""

        super().__init__(hass, STORAGE_KEY, STORAGE_VERSION)

        self.highest_message_level: MessageLevel = MessageLevel.INFO
        self.message_list: list[MessageItem] = []
        self.message_list_show: MessageListShow = MessageListShow.ALL
        self.message_list_orderby: MessageListOrderBy = (
            MessageListOrderBy.MESSAGE_LEVEL
            if orderby_message_level
            else MessageListOrderBy.ADDED_AT
        )

    # ------------------------------------------------------
    def set_highest_message_level(self) -> None:
        """Check for highest message level."""
        self.highest_message_level = MessageLevel.INFO

        for item in self.message_list:
            if item.message_level > self.highest_message_level:
                self.highest_message_level = item.message_level

                if self.highest_message_level == MessageLevel.ERROR:
                    break

    # ------------------------------------------------------
    @property
    def highest_message_level_color(self) -> str:
        """Highest message level color."""
        return self.highest_message_level.color
