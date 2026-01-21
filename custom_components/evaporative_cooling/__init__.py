"""
Custom integration to integrate evaporative_cooling with Home Assistant.

For more details about this integration, please refer to
https://github.com/nashja/evaporative_cooling
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.loader import async_get_loaded_integration

from .api import EvaporativeCoolingApiClient
from .const import (
    CONF_HUMIDITY_SENSOR,
    CONF_MONITOR_SENSOR,
    CONF_SENSOR_ID,
    CONF_TEMPERATURE_SENSOR,
    DEFAULT_SCAN_INTERVAL,
    LOGGER,
)
from .coordinator import EvaporativeCoolingDataUpdateCoordinator
from .data import EvaporativeCoolingData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import EvaporativeCoolingConfigEntry

#
# Only implementing a sensor for evaporative cooling
# There needs to be a sensor.py
#
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: EvaporativeCoolingConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    LOGGER.debug("async_setup_entry in __init__.py")
    LOGGER.debug("config_entry.options %s", entry.options)
    # Initialise the coordinator that manages data updates from the integration
    # This is defined in coordinator.py
    #
    # TODO if there are options - set the coordinator up with the new update interval
    #
    interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    LOGGER.debug("Scan Interval will be set to %d", interval)
    coordinator = EvaporativeCoolingDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        logger=LOGGER,
        name="EC Update Coordinator",
        update_interval=timedelta(interval),
    )

    # if not coordinator.api.connected:
    #    raise ConfigEntryNotReady

    entry.runtime_data = EvaporativeCoolingData(
        client=EvaporativeCoolingApiClient(
            temp_sensor_id=entry.data[CONF_TEMPERATURE_SENSOR],
            humidity_sensor_id=entry.data[CONF_HUMIDITY_SENSOR],
            monitor_sensor_id=entry.data.get(CONF_MONITOR_SENSOR, ""),
            sensor_id=entry.data[CONF_SENSOR_ID],
            hass=hass,
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: EvaporativeCoolingConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: EvaporativeCoolingConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
