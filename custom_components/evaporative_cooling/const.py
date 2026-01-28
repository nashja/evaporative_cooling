"""Constants for evaporative_cooling."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "evaporative_cooling"
ATTRIBUTION = "Data provided by http://sanfrancej.com/"
CONF_HUMIDITY_SENSOR = "humidity_sensor"
CONF_TEMPERATURE_SENSOR = "temperature_sensor"
CONF_MONITOR_SENSOR = "monitor_sensor"
CONF_SENSOR_ID = "sensor_id"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 2
MIN_SCAN_INTERVAL = 1
