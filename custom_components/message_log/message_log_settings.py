"""MessageLogSettings."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .settings_json import SettingsJson


# ------------------------------------------------------
# ------------------------------------------------------
class InfoLevels(Enum):
    """Info levels."""

    INFO = "Info"
    ATTENTION = "Attention"
    WARNING = "Warning"
    ERROR = "Error"


# ------------------------------------------------------
# ------------------------------------------------------
@dataclass
class MessageItem:
    """Message item."""

    # ------------------------------------------------------------------

    def __init__(
        self,
        message: str,
        info_level: InfoLevels | str = InfoLevels.INFO,
        icon: str = "mdi:message-badge-outline",
        remove_after: float = 24,
        notify: bool = False,
        added_at: datetime | None = None,
    ) -> None:
        """Message data."""
        tmp_info_level: InfoLevels = InfoLevels.INFO

        if isinstance(info_level, str):
            try:
                tmp_info_level = InfoLevels[info_level.upper()]
            except KeyError:
                tmp_info_level = InfoLevels.INFO

        self.message: str = message
        self.info_level: InfoLevels = tmp_info_level
        self.icon: str = icon
        self.remove_after: timedelta = timedelta(hours=remove_after)
        self.notify: bool = notify

        if added_at is None:
            self.added_at: datetime = datetime.now()
        else:
            self.added_at: datetime = added_at

    # ------------------------------------------------------
    @property
    def info_level_color(self) -> str:
        """Info level color."""
        match self.info_level:
            case InfoLevels.INFO:
                return "limegreen"
            case InfoLevels.ATTENTION:
                return "blue"
            case InfoLevels.WARNING:
                return "orange"
            case InfoLevels.ERROR:
                return "orangered"
            case _:
                return "red"


# ------------------------------------------------------
# ------------------------------------------------------
@dataclass
class MessageLogSettings(SettingsJson):
    """MessageLogSettings."""

    # ------------------------------------------------------
    def __init__(self) -> None:
        """Message log settings."""

        super().__init__()

        self.highest_info_level: InfoLevels = InfoLevels.INFO
        self.message_list: list[MessageItem] = []

    # ------------------------------------------------------
    def set_highest_info_level(self) -> None:
        """Check for highest info level."""
        self.highest_info_level = InfoLevels.INFO

        for item in self.message_list:
            if item.info_level == InfoLevels.WARNING:
                self.highest_info_level = item.info_level
            elif item.info_level == InfoLevels.ATTENTION:
                self.highest_info_level = item.info_level
            elif item.info_level == InfoLevels.ERROR:
                self.highest_info_level = item.info_level
                break

    # ------------------------------------------------------
    @property
    def highest_info_level_color(self) -> str:
        """Highest Info level color."""
        match self.highest_info_level:
            case InfoLevels.INFO:
                return "limegreen"
            case InfoLevels.ATTENTION:
                return "blue"
            case InfoLevels.WARNING:
                return "orange"
            case InfoLevels.ERROR:
                return "orangered"
            case _:
                return "red"
