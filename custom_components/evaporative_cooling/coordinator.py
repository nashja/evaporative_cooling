"""DataUpdateCoordinator for evaporative_cooling."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    EvaporativeCoolingApiClient,
    EvaporativeCoolingConfigurationError,
    EvaporativeCoolingHumidityConfigurationError,
    EvaporativeCoolingTemperatureConfigurationError,
)
from .const import (
    CONF_HUMIDITY_SENSOR,
    CONF_MONITOR_SENSOR,
    CONF_SCAN_INTERVAL,
    CONF_SENSOR_ID,
    CONF_TEMPERATURE_SENSOR,
    DEFAULT_SCAN_INTERVAL,
    LOGGER,
)

if TYPE_CHECKING:
    from .data import EvaporativeCoolingConfigEntry


class EvaporativeCoolingDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: EvaporativeCoolingConfigEntry

    # def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    #    """Initialize coordinator."""
    # Set variables from values entered in config flow setup

    #    self.humidity_sensor = config_entry.data[CONF_HUMIDITY_SENSOR]
    #    self.temperature_sensor = config_entry.data[CONF_TEMPERATURE_SENSOR]
    #    self.sensor_id = config_entry.data[CONF_SENSOR_ID]
    #    self.monitor_sensor = config_entry.data[CONF_MONITOR_SENSOR]
    #    self.poll_interval = DEFAULT_SCAN_INTERVAL
    #    self.poll_interval = config_entry.options.get(
    #        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
    #     )

    # super().__init__(
    #    hass,
    #    LOGGER,
    #    name=f"{DOMAIN} ({config_entry.unique_id})",
    # Method to call on every update interval.
    #    update_method=self._async_update_data,
    # Polling interval. Will only be polled if there are subscribers.
    # Using config option here but you can just use a value.
    #    # note scan interval is in minutes defined here ...
    #    update_interval=timedelta(minutes=self.poll_interval),
    # )

    # Initialise your api here
    #
    # self.api = EvaporativeCoolingApiClient(
    #    hass=hass,
    #    humidity_sensor_id=self.humidity_sensor,
    #    temp_sensor_id=self.temperature_sensor,
    #    monitor_sensor_id=self.monitor_sensor,
    #    sensor_id=self.sensor_id,
    # )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            devices = await self.hass.async_add_executor_job(
                self.config_entry.runtime_data.client.get_devices
            )
        except (
            EvaporativeCoolingTemperatureConfigurationError,
            EvaporativeCoolingHumidityConfigurationError,
        ) as exception:
            raise EvaporativeCoolingConfigurationError(exception) from exception
        except EvaporativeCoolingConfigurationError as exception:
            raise UpdateFailed(exception) from exception
