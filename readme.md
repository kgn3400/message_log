# Message log

![GitHub release (latest by date)](https://img.shields.io/github/v/release/kgn3400/message_log)
![GitHub all releases](https://img.shields.io/github/downloads/kgn3400/message_log/total)
![GitHub last commit](https://img.shields.io/github/last-commit/kgn3400/message_log)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kgn3400/message_log)
[![Validate% with hassfest](https://github.com/kgn3400/message_log/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/kgn3400/message_log/actions/workflows/hassfest.yaml)

The Message log integration allows you to log and view logged messages in Home Assistant added from a external system. Message can be created as info, attention, warning or error.

For installation instructions until the Message log integrations is part of HACS, [see this guide](https://hacs.xyz/docs/faq/custom_repositories).
Or click
[![My Home Assistant](https://img.shields.io/badge/Home%20Assistant-%2341BDF5.svg?style=flat&logo=home-assistant&label=Add%20to%20HACS)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kgn3400&repository=message_log&category=integration)

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=message_log)

## Configuration

Configuration is setup via UI in Home assistant. To add one, go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations) and click the add button. Next choose the [Message log](https://my.home-assistant.io/redirect/config_flow_start?domain=message_log) option.

## Services

Available services: __add__, __order_by__, __remove_message__ and __show_message__

## Adding messages from an external system

Below is an example of how to add a message from an external system written in Python.

```python
class MessageLevels(Enum):
    """Message levels."""

    INFO = 10
    ATTENTION = 20
    WARNING = 30
    ERROR = 40

def message_to_hass_log(
    message: str,
    message_level: MessageLevels | None = None,
    icon: str | None = None,
    remove_after: float | None = None,
    notify: bool | None = None,
    added_at: datetime | None = None,
) -> None:
    """Message to hass."""

    headers = {
        "Authorization": f"Bearer {HASS_TOKEN}",
        "content-type": "application/json",
    }
    data: dict[str, Any] = {"message": message}

    if message_level is not None:
        data["message_level"] = message_level.name

    if icon is not None:
        data["icon"] = icon

    if remove_after is not None:
        data["remove_after"] = remove_after

    if notify:
        data["notify"] = notify

    if added_at:
        data["added_at"] = added_at.strftime("%Y-%m-%d %H:%M:%S")

    post(URL, headers=headers, json=data, timeout=3)
```
