"""Sensor platform for evaporative_cooling."""

from __future__ import annotations

from copyreg import add_extension
from turtle import up
from typing import TYPE_CHECKING
from xml.etree.ElementTree import VERSION

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

from .entity import EvaporativeCoolingEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import EvaporativeCoolingDataUpdateCoordinator
    from .data import EvaporativeCoolingConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="evaporative_cooling",
        name="Evaporative Cooling Sensor",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:air-conditioner",
    ),
)


#
# In order to get the code to wait for all the sensors to be available need to set
# update_before_add=True when adding entities.
#
async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: EvaporativeCoolingConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    async_add_entities(
        (
            EvaporativeCoolingSensor(
                coordinator=entry.runtime_data.coordinator,
                entity_description=entity_description,
            )
            for entity_description in ENTITY_DESCRIPTIONS
        ),
        update_before_add=True,
    )


class EvaporativeCoolingSensor(EvaporativeCoolingEntity, SensorEntity):
    """evaporative_cooling Sensor class."""

    def __init__(
        self,
        coordinator: EvaporativeCoolingDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        # manufacturer="Sanfrancej.com",
        # version=VERSION,

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.coordinator.data.get("body")
