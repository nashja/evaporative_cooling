"""Custom types for evaporative_cooling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import EvaporativeCoolingApiClient
    from .coordinator import EvaporativeCoolingDataUpdateCoordinator


type EvaporativeCoolingConfigEntry = ConfigEntry[EvaporativeCoolingData]


@dataclass
class EvaporativeCoolingData:
    """Data for the EvaporativeCooling integration."""

    # Not sure we need a client ...
    client: EvaporativeCoolingApiClient
    coordinator: EvaporativeCoolingDataUpdateCoordinator
    integration: Integration
