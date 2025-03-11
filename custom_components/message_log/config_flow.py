"""Config flow for Pypi updates integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    IconSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)
from homeassistant.util.uuid import random_uuid_hex

from .const import (
    CONF_DEFAULT_ICON,
    CONF_LISTEN_TO_TIMER_TRIGGER,
    CONF_MARKDOWN_MESSAGE_LIST_COUNT,
    CONF_ORDER_BY_MESSAGE_LEVEL,
    CONF_REMOVE_MESSAGE_AFTER_HOURS,
    CONF_RESTART_TIMER,
    CONF_SCROLL_MESSAGES_EVERY_MINUTES,
    CONF_SCROLL_THROUGH_LAST_MESSAGES_COUNT,
    DOMAIN,
    DOMAIN_NAME,
)

CONFIG_OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_REMOVE_MESSAGE_AFTER_HOURS,
            default=24,
        ): NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=696,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )
        ),
        vol.Required(
            CONF_SCROLL_MESSAGES_EVERY_MINUTES,
            default=0.5,
        ): NumberSelector(
            NumberSelectorConfig(
                min=0.5,
                max=696,
                step=1,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="minutes",
            )
        ),
        vol.Optional(
            CONF_LISTEN_TO_TIMER_TRIGGER,
        ): EntitySelector(
            EntitySelectorConfig(integration="timer", multiple=False),
        ),
        vol.Optional(
            CONF_RESTART_TIMER,
            default=True,
        ): BooleanSelector(),
        vol.Required(
            CONF_SCROLL_THROUGH_LAST_MESSAGES_COUNT,
            default=5,
        ): NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=696,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="count",
            )
        ),
        vol.Required(
            CONF_MARKDOWN_MESSAGE_LIST_COUNT,
            default=10,
        ): NumberSelector(
            NumberSelectorConfig(
                min=2,
                max=100,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="count",
            )
        ),
        vol.Required(
            CONF_DEFAULT_ICON,
            default="mdi:message-badge-outline",
        ): IconSelector(),
        vol.Required(
            CONF_ORDER_BY_MESSAGE_LEVEL,
            default=True,
        ): cv.boolean,
    }
)


# ------------------------------------------------------------------
async def config_schema_handler(
    handler: SchemaCommonFlowHandler,
) -> vol.Schema:
    """Return schema for the sensor config step."""

    if handler.parent_handler.unique_id is None:
        await handler.parent_handler.async_set_unique_id(random_uuid_hex())
        handler.parent_handler._abort_if_unique_id_configured()  # noqa: SLF001

    return CONFIG_OPTIONS_SCHEMA


CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(config_schema_handler),
}
OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(CONFIG_OPTIONS_SCHEMA),
}


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""

        return cast(str, DOMAIN_NAME)
