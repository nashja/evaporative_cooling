"""Sample API Client."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from random import randrange
from sre_parse import State
from typing import TYPE_CHECKING, Any

from .const import EFFICIENCY_CHART, EFFICIENCY_HUMIDITY, EFFICIENCY_TEMPERATURE, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, State

from homeassistant.components.sensor import (
    SensorDeviceClass,
    # SensorEntity,
    # SensorStateClass,
)
from homeassistant.exceptions import HomeAssistantError, ConfigEntryNotReady
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

    device_id: str
    device_unique_id: str | None
    device_type: DeviceType
    name: str
    state: State | None


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

        self.temp_sensor = Device(
            device_id=temp_sensor_id,
            device_type=DeviceType.EC_TEMPERATURE_SENSOR,
            name="",
            state=None,
            device_unique_id=None,
        )

        self.humidity_sensor = Device(
            device_id=humidity_sensor_id,
            device_type=DeviceType.EC_HUMIDITY_SENSOR,
            name="",
            state=None,
            device_unique_id=None,
        )

        self.monitor_sensor = Device(
            device_id=monitor_sensor_id,
            device_type=DeviceType.EC_MONITOR_SENSOR,
            name="",
            state=None,
            device_unique_id=None,
        )

        self.ec_sensor = Device(
            device_id=sensor_id,
            device_type=DeviceType.EVAPORATIVE_COOLING_SENSOR,
            name="",
            state=None,
            device_unique_id=None,
        )

        self.connected: bool = False
        self.hass = hass

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.ec_sensor.device_id.replace(".", "_")

    def config(self) -> bool:
        """Configure the api."""
        registry = er.async_get(self.hass)
        # Validate + resolve entity registry id to entity_id

        try:
            valid_temp_id = er.async_validate_entity_id(
                registry, self.temp_sensor.device_id
            )
            valid_humidity_id = er.async_validate_entity_id(
                registry, self.humidity_sensor.device_id
            )
            self.temp_sensor.state = self.hass.states.get(self.temp_sensor.device_id)
            self.humidity_sensor.state = self.hass.states.get(
                self.humidity_sensor.device_id
            )
        except Exception as e:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception in configuring sensors", e)
            raise EvaporativeCoolingConfigurationError from e
        LOGGER.debug(
            "API Connect: temp Sensor= %s, humididty sensor = %s)",
            valid_temp_id,
            valid_humidity_id,
        )
        is_valid = False
        if (
            self.humidity_sensor.state is not None
            and self.temp_sensor.state is not None
        ):
            is_temp = (
                self.temp_sensor.state.attributes["device_class"]
                == SensorDeviceClass.TEMPERATURE
            )
            is_humidity = (
                self.humidity_sensor.state.attributes["device_class"]
                == SensorDeviceClass.HUMIDITY
            )
            is_valid = is_temp and is_humidity

        LOGGER.debug(
            "Connect: temp Sensor= %s (is temp = %s), humididty sensor = %s (is humidity = %s)",
            self.temp_sensor.device_id,
            is_temp,
            self.humidity_sensor.device_id,
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

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper()

    # To get this to work, while waiting for sensors to be available need to return ConfigNotReady here
    # then all the code for HA works to retry etc without error.
    async def _api_wrapper(self) -> Any:
        tsensor = self.hass.states.get(self.temp_sensor.device_id)
        if not tsensor:
            msg = "EC Temperature sensor not available"
            raise ConfigEntryNotReady(msg)
        hsensor = self.hass.states.get(self.humidity_sensor.device_id)
        if not hsensor:
            msg = "EC Humidity sensor not available"
            raise ConfigEntryNotReady(msg)
        # check if the sensors are available before converting to float
        # just catch an error if they aren't
        if tsensor.state in {"unknown", "unavailable"}:
            msg = "EC Temperature sensor not yet available"
            raise ConfigEntryNotReady(msg)
        if hsensor.state in {"unknown", "unavailable"}:
            msg = "EC Humidity sensor not yet available"
            raise ConfigEntryNotReady(msg)
        try:
            temp = float(tsensor.state)
            humidity = float(hsensor.state)
            LOGGER.debug(
                "EC - API get-device-value (lookup): temp Sensor= %s,humididty sensor = %s",
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
            return {"body": best_temp}
        except ValueError as err:
            # raise ConfigEntryNotReady from err
            LOGGER.debug("Unable to calculate temperature", err)
            return {"body": 0}
            # raise EvaporativeCoolingReadoutError
        except Exception as err:
            LOGGER.debug("Unable to calculate temperature", err)
            return {"body": 0}
            # raise EvaporativeCoolingReadoutError from err
