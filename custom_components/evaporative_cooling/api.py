"""Sample API Client."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from random import randrange
from typing import TYPE_CHECKING, Any

from .const import EFFICIENCY_CHART, EFFICIENCY_HUMIDITY, EFFICIENCY_TEMPERATURE, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from homeassistant.components.sensor import (
    SensorDeviceClass,
    # SensorEntity,
    # SensorStateClass,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er


class EvaporativeCoolingReadoutError(HomeAssistantError):
    """Exception to indicate a general API error."""


class EvaporativeCoolingConfigurationError(HomeAssistantError):
    """Exception to indicate a general API error."""


class EvaporativeCoolingTemperatureConfigurationError(
    EvaporativeCoolingConfigurationError,
):
    """Exception to indicate a communication error."""


class EvaporativeCoolingHumidityConfigurationError(
    EvaporativeCoolingConfigurationError,
):
    """Exception to indicate an authentication error."""


#
# Some types to deal with the sensors we need in the configuration
#
class DeviceType(StrEnum):
    """Device types."""

    EVAPORATIVE_COOLING_SENSOR = "evaporative_cooling_sensor"
    EC_TEMPERATURE_SENSOR = "evaporative_cooling_temperature_sensor"
    EC_HUMIDITY_SENSOR = "evaporative_cooling_humidity_sensor"
    EC_MONITOR_SENSOR = "evaporative_cooling_monitor_sensor"
    OTHER = "other"


@dataclass
class Device:
    """API device."""

    device_id: int
    device_unique_id: str
    device_type: DeviceType
    name: str
    state: float | bool


#
# The API here will be to make sure that the temperature sensors are available.  And then update
# will get the current state of the temperature sensors
# need to initialise this with the names of the sensors
#
class EvaporativeCoolingApiClient:
    """
    API Client.

    In this case the API reads the required sensors to calculate the EV Cooling
    potential.
    """

    def __init__(
        self,
        temp_sensor_id: str,
        humidity_sensor_id: str,
        monitor_sensor_id: str,
        sensor_id: str,
        hass: HomeAssistant,
    ) -> None:
        """Initialise the API Client."""
        self.DEVICES = {}
        self.DEVICES[DeviceType.EC_TEMPERATURE_SENSOR] = {
            "id": temp_sensor_id,
            "type": DeviceType.EC_TEMPERATURE_SENSOR,
            "sensor": None,
            "value": None,
        }
        self.DEVICES[DeviceType.EC_TEMPERATURE_SENSOR] = {
            "id": humidity_sensor_id,
            "type": DeviceType.EC_TEMPERATURE_SENSOR,
            "sensor": None,
            "value": None,
        }
        self.DEVICES[DeviceType.EC_MONITOR_SENSOR] = {
            "id": monitor_sensor_id,
            "type": DeviceType.EC_MONITOR_SENSOR,
            "sensor": None,
            "value": None,
        }
        self.DEVICES[DeviceType.EVAPORATIVE_COOLING_SENSOR] = {
            "id": sensor_id,
            "type": DeviceType.EVAPORATIVE_COOLING_SENSOR,
            "sensor": None,
            "value": None,
        }
        self.ts = self.DEVICES[DeviceType.EC_TEMPERATURE_SENSOR]
        self.hs = self.DEVICES[DeviceType.EC_HUMIDITY_SENSOR]
        # self.temp_sensor_id = temp_sensor_id
        # self.humidity_sensor_id = humidity_sensor_id
        self.sensor_id = sensor_id
        # self.temp_sensor = None
        # self.humidity_sensor = None
        # self.tSensor = None
        # self.hSensor = None

        self.connected: bool = False
        self.hass = hass

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.sensor_id.replace(".", "_")

    def config(self) -> bool:
        """Configure the api."""
        registry = er.async_get(self.hass)
        # Validate + resolve entity registry id to entity_id
        ts = self.DEVICES[DeviceType.EC_TEMPERATURE_SENSOR]
        ts["sensor"] = er.async_validate_entity_id(registry, ts["id"])
        ts["value"] = self.hass.states.get(ts["sensor"])

        th = self.DEVICES[DeviceType.EC_HUMIDITY_SENSOR]
        th["sensor"] = er.async_validate_entity_id(registry, th["id"])
        th["value"] = self.hass.states.get(ts["sensor"])
        #
        # This gets the state of the entity
        #

        is_valid = False
        if th["value"] is not None and ts["value"] is not None:
            is_temp = (
                ts["sensor"].attributes["device_class"] == SensorDeviceClass.TEMPERATURE
            )
            is_humidity = (
                th["sensor"].attributes["device_class"] == SensorDeviceClass.HUMIDITY
            )
            is_valid = is_temp and is_humidity

        LOGGER.debug(
            " Connect: temp Sensor= %s (is temp = %s), humididty sensor = %s (is humidity = %s)",
            ts["sensor"],
            is_temp,
            th["sensor"],
            is_humidity,
        )

        if is_valid:
            self.connected = True
            return True
        if not is_temp:
            raise EvaporativeCoolingTemperatureConfigurationError
        if not is_humidity:
            raise EvaporativeCoolingHumidityConfigurationError
        raise EvaporativeCoolingConfigurationError

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self.connected = False
        return True

    def get_devices(self) -> list[Device]:
        """Get devices on api."""
        return [
            Device(
                device_id=device.get("id"),
                device_unique_id=self.get_device_unique_id(
                    device.get("id"), device.get("type")
                ),
                device_type=device.get("type"),
                name=self.get_device_name(device.get("id"), device.get("type")),
                state=self.get_device_value(
                    device.get("id"), device.get("type"), device.get("sensor")
                ),
            )
            for device in self.DEVICES
        ]

    def get_device_unique_id(self, device_id: str, device_type: DeviceType) -> str:
        """Return a unique device id."""
        if device_type == DeviceType.EVAPORATIVE_COOLING_SENSOR:
            return f"{self.controller_name}_{device_id}"
        if device_type == DeviceType.EC_TEMPERATURE_SENSOR:
            return f"{self.controller_name}_T{device_id}"
        if device_type == DeviceType.EC_HUMIDITY_SENSOR:
            return f"{self.controller_name}_H{device_id}"
        if device_type == DeviceType.EC_MONITOR_SENSOR:
            return f"{self.controller_name}_M{device_id}"
        return f"{self.controller_name}_Z{device_id}"

    def get_device_name(self, device_id: str, device_type: DeviceType) -> str:
        """Return the device name."""
        if device_type == DeviceType.EC_HUMIDITY_SENSOR:
            return f"ECHumiditySensor{device_id}"
        if device_type == DeviceType.EC_TEMPERATURE_SENSOR:
            return f"ECTemperatureSensor{device_id}"
        if device_type == DeviceType.EVAPORATIVE_COOLING_SENSOR:
            return f"EvaporativeCoolingSensor{device_id}"
        return f"OtherSensor{device_id}"

    def get_device_value(
        self, device_id: str, device_type: DeviceType, sensor: str
    ) -> float | bool:
        """Get device value."""
        if device_type == DeviceType.EC_TEMPERATURE_SENSOR:
            tsensor = self.hass.states.get(sensor)
            if not tsensor:
                raise EvaporativeCoolingReadoutError
            return float(tsensor.state)

        if device_type == DeviceType.EC_HUMIDITY_SENSOR:
            hsensor = self.hass.states.get(sensor)
            if not hsensor:
                raise EvaporativeCoolingReadoutError
            return float(hsensor.state)

        if device_type == DeviceType.EVAPORATIVE_COOLING_SENSOR:
            LOGGER.debug(
                " get-device-value (stored): temp Sensor= %s, humididty sensor = %s",
                self.ts.get("sensor").state,
                self.hs.get("sensor").state,
                # self.tSensor.state,
                # self.hSensor.state,
            )
            try:
                # tSensor = self.hass.states.get(self.temp_sensor).state
                # hSensor = self.hass.states.get(self.humidity_sensor).state
                tSensor = self.ts.get("value")
                hSensor = self.hs.get("value")
            except Exception as e:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception", e)
                return 0.0

            temp = float(tSensor)
            humidity = float(hSensor)
            LOGGER.debug(
                " get-device-value (lookup): temp Sensor= %s, humididty sensor = %s",
                temp,
                humidity,
            )
            for t in range(len(EFFICIENCY_TEMPERATURE)):
                if temp < EFFICIENCY_TEMPERATURE[t]:
                    temp_index = t
                    break

            for t in range(len(EFFICIENCY_HUMIDITY)):
                if humidity < EFFICIENCY_HUMIDITY[t]:
                    humidity_index = t
                    break

            best_temp = EFFICIENCY_CHART[temp_index][humidity_index]

            LOGGER.debug("Efficiency Temperature = %f ", best_temp)
            return best_temp

        return randrange(1, 10)
