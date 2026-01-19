"""Constants for evaporative_cooling."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "evaporative_cooling"
ATTRIBUTION = "Data provided by http://sanfrancej.com/"
CONF_HUMIDITY_SENSOR = "humidity_sensor"
CONF_TEMPERATURE_SENSOR = "temperature_sensor"
CONF_SENSOR_ID = "sensor_id"
CONF_FOO_ID = "foo_id"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 2
MIN_SCAN_INTERVAL = 1

EFFICIENCY_HUMIDITY = [
    5,
    10,
    15,
    20,
    25,
    30,
    35,
    40,
    45,
    50,
    55,
    60,
    65,
    70,
    75,
    80,
    85,
]
EFFICIENCY_TEMPERATURE = [25, 27, 29, 31, 33, 35, 37, 39, 41]

EFFICIENCY_CHART = [
    [
        12.7,
        13.6,
        14.4,
        15.2,
        15.9,
        16.6,
        17.3,
        18.0,
        18.7,
        19.4,
        20.0,
        20.6,
        21.2,
        21.8,
        22.4,
        22.9,
        23.4,
    ],
    [
        14.0,
        14.9,
        15.8,
        16.6,
        17.4,
        18.2,
        18.9,
        19.7,
        20.4,
        21.1,
        21.7,
        22.4,
        23.0,
        23.6,
        24.2,
        24.8,
        25.4,
    ],
    [
        15.2,
        16.2,
        17.1,
        18.0,
        18.9,
        19.7,
        20.5,
        21.3,
        22.1,
        22.8,
        23.5,
        24.2,
        24.9,
        25.5,
        26.1,
        26.7,
        27.3,
    ],
    [
        16.4,
        17.5,
        18.5,
        19.5,
        20.4,
        21.2,
        22.1,
        22.9,
        23.7,
        24.5,
        25.3,
        26.0,
        26.7,
        27.3,
    ],
    [17.6, 18.8, 19.8, 20.9, 21.8, 22.8, 23.7, 24.6, 25.4, 26.2, 27.0, 27.8],
    [18.8, 20.0, 21.2, 22.3, 23.3, 24.3, 25.3, 26.2, 27.1, 28.0],
    [19.9, 21.3, 22.5, 23.8, 24.8, 25.9, 26.9, 27.9],
    [21.1, 22.5, 23.9, 25.2, 26.3, 27.4],
    [22.2, 23.8, 25.2, 26.5, 27.7],
]
