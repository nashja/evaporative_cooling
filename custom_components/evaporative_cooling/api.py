"""Sample API Client."""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING, Any

from .const import LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from homeassistant.components.sensor import (
    SensorDeviceClass,
    # SensorEntity,
    # SensorStateClass,
)
from homeassistant.helpers import entity_registry as er


class EvaporativeCoolingConfigurationError(Exception):
    """Exception to indicate a general API error."""


class EvaporativeCoolingTemperatureConfigurationError(
    EvaporativeCoolingConfigurationError,
):
    """Exception to indicate a communication error."""


class EvaporativeCoolingHumidityConfigurationError(
    EvaporativeCoolingConfigurationError,
):
    """Exception to indicate an authentication error."""


# def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
#   """Verify that the response is valid."""
#   if response.status in (401, 403):
#       msg = "Invalid credentials"
#       raise EvaporativeCoolingApiClientAuthenticationError(
#           msg,
#       )
#   response.raise_for_status()


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

    # def __init__(
    #    self,
    #    username: str,
    #    password: str,
    #    session: aiohttp.ClientSession,
    # ) -> None:
    #    """Sample  Client."""
    #    self._username = username
    #    self._password = password
    #    self._session = session

    def __init__(
        self,
        temp_sensor_id: str,
        humidity_sensor_id: str,
        sensor_id: str,
        hass: HomeAssistant,
    ) -> None:
        """Initialise the API Client."""
        self.temp_sensor_id = temp_sensor_id
        self.humidity_sensor_id = humidity_sensor_id
        self.sensor_id = sensor_id
        self.temp_sensor = None
        self.humidity_sensor = None
        self.tSensor = None
        self.hSensor = None
        self.connected: bool = False
        self.hass = hass

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.sensor_id.replace(".", "_")

    def connect(self) -> bool:
        """Connect to api."""
        #
        # Could check here if the temp is a temp and humidity is a humidity
        #
        registry = er.async_get(self.hass)
        # Validate + resolve entity registry id to entity_id
        self.temp_sensor = er.async_validate_entity_id(registry, self.temp_sensor_id)
        self.humidity_sensor = er.async_validate_entity_id(
            registry, self.humidity_sensor_id
        )
        #
        # This gets the state of the entity
        #
        self.tSensor = self.hass.states.get(self.temp_sensor)
        self.hSensor = self.hass.states.get(self.humidity_sensor)
        is_valid = False
        if self.tSensor is not None and self.hSensor is not None:
            is_temp = (
                self.tSensor.attributes["device_class"] == SensorDeviceClass.TEMPERATURE
            )
            is_humidity = (
                self.hSensor.attributes["device_class"] == SensorDeviceClass.HUMIDITY
            )
            is_valid = is_temp and is_humidity

        LOGGER.debug(
            " Connect: temp Sensor= %s (is temp = %s), humididty sensor = %s (is humidity = %s)",
            self.tSensor,
            is_temp,
            self.hSensor,
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
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise EvaporativeCoolingApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise EvaporativeCoolingApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise EvaporativeCoolingApiClientError(
                msg,
            ) from exception
