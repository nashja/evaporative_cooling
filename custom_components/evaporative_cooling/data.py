"""Custom types for evaporative_cooling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import EvaporativeCoolingApiClient
    from .coordinator import BlueprintDataUpdateCoordinator


type EvaporativeCoolingConfigEntry = ConfigEntry[EvaporativeCoolingData]


@dataclass
class EvaporativeCoolingData:
    """Data for the Blueprint integration."""

    client: EvaporativeCoolingApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
