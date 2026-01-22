"""DataUpdateCoordinator for evaporative_cooling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import (
    EvaporativeCoolingConfigurationError,
)

if TYPE_CHECKING:
    from .data import EvaporativeCoolingConfigEntry


class EvaporativeCoolingDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: EvaporativeCoolingConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except ConfigEntryNotReady as exception:
            raise ConfigEntryNotReady from exception
            # return {"body": "0"}
        except EvaporativeCoolingConfigurationError as exception:
            return {"body": "0"}


#
# consider adding an exception for no valid data from sensors ...
#
