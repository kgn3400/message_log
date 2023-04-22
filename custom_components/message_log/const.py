"""Constants for Message log integration."""
from logging import Logger, getLogger

DOMAIN = "message_log"
DOMAIN_NAME = "Message log"
LOGGER: Logger = getLogger(__name__)

CONF_REMOVE_MESSAGE_AFTER_HOURS: str = "remove_message_after_hours"
CONF_DEFAULT_ICON: str = "default_icon"
CONF_SCROLL_MESSAGES_EVERY_MINUTES: str = "scroll_messages_every_minutes"
CONF_SCROLL_THROUGH_LAST_MESSAGES_COUNT: str = "scroll_through_last_messages_count"
CONF_MARKDOWN_MESSAGE_LIST_COUNT: str = "markdown_message_list_count"
CONF_ORDER_BY_MESSAGE_LEVEL: str = "order_by_message_level"
