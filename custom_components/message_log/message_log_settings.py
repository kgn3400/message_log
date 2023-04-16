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
    ) -> None:
        """Message data."""
        tmp_info_level: InfoLevels = InfoLevels.INFO

        if isinstance(info_level, str):
            try:
                tmp_info_level = InfoLevels[info_level.upper()]
            except KeyError:
                tmp_info_level = InfoLevels.INFO

        # if info_level is None or info_level == "":
        #     info_level = "Info"

        # if notify is None or notify == "":
        #     notify = False

        # if icon is None or icon == "":
        #     icon = self.STD_ICON

        self.message: str = message
        self.info_level: InfoLevels = tmp_info_level
        self.icon: str = icon
        self.remove_after: timedelta = timedelta(hours=remove_after)
        self.notify: bool = notify
        self.added_at: datetime = datetime.now()


# ------------------------------------------------------
# ------------------------------------------------------
class MessageLogSettings(SettingsJson):
    """MessageLogSettings."""

    def __init__(self) -> None:
        """Message log settings."""

        super().__init__()

        self.message_list: list[MessageItem] = []
