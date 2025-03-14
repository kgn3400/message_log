"""Device triggers."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, EVENT_NEW_LOG_ENTRY, EVENT_NEW_NOTIFY_LOG_ENTRY
from .message_log_settings import MessageLevel

TRIGGER_TYPES = {
    EVENT_NEW_LOG_ENTRY,
    EVENT_NEW_NOTIFY_LOG_ENTRY,
    EVENT_NEW_LOG_ENTRY + "_info",
    EVENT_NEW_LOG_ENTRY + "_warning",
    EVENT_NEW_LOG_ENTRY + "_error",
    EVENT_NEW_LOG_ENTRY + "_attention",
}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device triggers for trafikmeldinger devices."""
    triggers = []

    base_trigger = {
        # Required fields of TRIGGER_BASE_SCHEMA
        CONF_PLATFORM: "device",
        CONF_DEVICE_ID: device_id,
        CONF_DOMAIN: DOMAIN,
        # Required fields of TRIGGER_SCHEMA
    }
    triggers.append({**base_trigger, CONF_TYPE: EVENT_NEW_NOTIFY_LOG_ENTRY})
    triggers.append({**base_trigger, CONF_TYPE: EVENT_NEW_LOG_ENTRY})

    triggers.extend(
        [
            {**base_trigger, CONF_TYPE: EVENT_NEW_LOG_ENTRY + "_" + item.name.lower()}
            for item in MessageLevel
        ]
    )
    # for item in MessageLevel:
    #     triggers.append(
    #         {**base_trigger, CONF_TYPE: EVENT_NEW_LOG_ENTRY + "_" + item.name.lower()}
    #     )

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""

    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: config["domain"] + "." + config[CONF_TYPE],
        }
    )

    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
