"""Sample API Client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from math import atan

from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError


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
# The API here will be to make sure that the temperature sensors are available.
# And then update will get the current state of the temperature sensors
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
        ec_sensor_id: str,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the sensor IDs used by the API ."""
        self.temp_sensor_id = temp_sensor_id
        self.humidity_sensor_id = humidity_sensor_id
        self.monitor_sensor_id = monitor_sensor_id
        self.ec_sensor_id = ec_sensor_id
        self.hass = hass

    def wet_bulb_temp(self, dry_bulb_temp: float, relative_humidity: float) -> float:
        """Calculate the wet bulb temperature at - the best EC could do."""
        T = dry_bulb_temp  # noqa: N806
        RH = relative_humidity  # noqa: N806

        f1 = T * atan(0.151977 * pow((RH + 8.313659), 0.5))
        f2 = atan(T + RH)
        f3 = atan(RH - 1.676331)
        f4 = 0.00391838 * pow(RH, 1.5) * atan(0.023101 * RH)
        f5 = 4.686035
        return f1 + f2 - f3 + f4 - f5

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.ec_sensor_id.replace(".", "_")

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper()

    # To get this to work, while waiting for sensors to be available
    # need to return ConfigNotReady here
    # then all the code for HA works to retry etc without error.
    # The ids all come from the configuration
    async def _api_wrapper(self) -> Any:
        tsensor = self.hass.states.get(self.temp_sensor_id)
        if not tsensor:
            msg = "EC Temperature sensor not available"
            raise ConfigEntryNotReady(msg)
        hsensor = self.hass.states.get(self.humidity_sensor_id)
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
                "EC - API get-device-value (lookup): temp Sensor= %s,humididty sensor = %s",  # noqa: E501
                temp,
                humidity,
            )

            best_temp = self.wet_bulb_temp(temp, humidity)

            LOGGER.debug("Efficiency Temperature = %f ", best_temp)
            #
            # This can be the difference of target to measured
            # binary : internal above potential or below potential
            # Put all the sensor values of interest here, and return them
            # then when there is a value_fn call which is .get("temp1")
            # it returns the proper sensor
            #
            # This now works, see below, can add all the info want here, and then use
            # a dictionary to get this in the sensors...
            internal_temp = "unavailable"
            delta_temp = "unavailable"
            msensor = self.hass.states.get(self.monitor_sensor_id)
            #
            # If there is an internal monitor sensor - can provide other state info
            #
            if msensor and msensor.state not in {"unknown", "unavailable"}:
                internal_temp = float(msensor.state)
                delta_temp = internal_temp - best_temp
        except ValueError as err:
            # raise ConfigEntryNotReady from err
            LOGGER.debug("Unable to calculate temperature", err)
            return {"ec_temp": 0}
            # raise EvaporativeCoolingReadoutError
        except Exception as err:  # noqa: BLE001
            LOGGER.debug("Unable to calculate temperature", err)
            return {
                "ec_temp": 0,
                "external_temp": temp,
                "external_humidity": humidity,
                "internal_temp": internal_temp,
            }
        else:
            return {
                "ec_temp": best_temp,
                "external_temp": temp,
                "external_humidity": humidity,
                "internal_temp": internal_temp,
                "temp_delta": delta_temp,
            }
