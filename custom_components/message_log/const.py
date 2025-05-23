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
CONF_RESTART_TIMER = "restart_timer"
CONF_LISTEN_TO_TIMER_TRIGGER = "listen_to_timer_trigger"

TRANSLATION_KEY = DOMAIN
TRANSLATE_EXTRA = "options.step.extra.data"
TRANSLATION_KEY_MISSING_TIMER_ENTITY = "missing_timer_entity"

STORAGE_VERSION = 1
STORAGE_KEY = DOMAIN

EVENT_NEW_LOG_ENTRY = "new_log_entry"
EVENT_NEW_NOTIFY_LOG_ENTRY = "new_notify_log_entry"

SOURCE_NOTIFY = "Notify"
SOURCE_SERVICE = "Service"
