"""Allows to configure custom shell commands to turn a value for a sensor."""

from homeassistant.const import Platform

CONF_COMMAND_TIMEOUT = "command_timeout"
CONF_JSON_ATTRIBUTES = "json_attributes"
CONF_RAW_ATTR = "include_raw_attribute"

ATTR_RAW = "raw"

DEFAULT_TIMEOUT = 15
DOMAIN = "command_line"
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.COVER,
    Platform.SENSOR,
    Platform.SWITCH,
]
