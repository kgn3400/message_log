"""Config flow for Pypi updates integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)
from homeassistant.helpers.selector import (
    BooleanSelector,
    IconSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

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

#  from homeassistant import config_entries
from .fix_entity_selector import EntitySelector, EntitySelectorConfig


# ------------------------------------------------------------------
async def _validate_input(
    hass: HomeAssistant, user_input: dict[str, Any], errors: dict[str, str]
) -> bool:
    """Validate the user input."""

    #      errors["base"] = "missing_pypi_package"

    return True


# ------------------------------------------------------------------
def _create_form(
    user_input: dict[str, Any],
) -> vol.Schema:
    """Create a form for step/option."""

    return vol.Schema(
        {
            vol.Required(
                CONF_REMOVE_MESSAGE_AFTER_HOURS,
                default=user_input.get(CONF_REMOVE_MESSAGE_AFTER_HOURS, 24),
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
                default=user_input.get(CONF_SCROLL_MESSAGES_EVERY_MINUTES, 0.5),
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
                default=user_input.get(CONF_LISTEN_TO_TIMER_TRIGGER, ""),
            ): EntitySelector(
                EntitySelectorConfig(integration="timer", multiple=False),
            ),
            vol.Optional(
                CONF_RESTART_TIMER,
                default=user_input.get(CONF_RESTART_TIMER, False),
            ): BooleanSelector(),
            vol.Required(
                CONF_SCROLL_THROUGH_LAST_MESSAGES_COUNT,
                default=user_input.get(CONF_SCROLL_THROUGH_LAST_MESSAGES_COUNT, 5),
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
                default=user_input.get(CONF_MARKDOWN_MESSAGE_LIST_COUNT, 10),
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
                default=user_input.get(CONF_DEFAULT_ICON, "mdi:message-badge-outline"),
            ): IconSelector(),
            vol.Required(
                CONF_ORDER_BY_MESSAGE_LEVEL,
                default=user_input.get(CONF_ORDER_BY_MESSAGE_LEVEL, True),
            ): cv.boolean,
        }
    )


CONFIG_OPTIONS = {
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
        default=False,
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

CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(
        vol.Schema(
            {
                **CONFIG_OPTIONS,
            }
        ),
    ),
}
OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(
        vol.Schema(
            {
                **CONFIG_OPTIONS,
            }
        ),
    ),
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
