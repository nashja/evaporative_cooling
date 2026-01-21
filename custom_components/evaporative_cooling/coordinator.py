"""DataUpdateCoordinator for evaporative_cooling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryError
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
        except EvaporativeCoolingConfigurationError as exception:
            raise ConfigEntryError from exception


#
# consider adding an exception for no valid data from sensors ...
#
