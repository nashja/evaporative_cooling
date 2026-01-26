"""Sensor platform for evaporative_cooling."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import StatisticsError
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature

from .entity import EvaporativeCoolingEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import EvaporativeCoolingDataUpdateCoordinator
    from .data import EvaporativeCoolingConfigEntry


@dataclass(frozen=True, kw_only=True)
class EvaporativeCoolingEntityDescription(SensorEntityDescription):
    """Describes a Sage Coffee sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any]


ENTITY_DESCRIPTIONS: tuple[EvaporativeCoolingEntityDescription, ...] = (
    EvaporativeCoolingEntityDescription(
        key="evaporative_cooling",
        translation_key="evaporative_cooling",
        name="Evaporative Cooling Sensor",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        icon="mdi:air-conditioner",
        value_fn=lambda state: state.get("body"),
    ),
    EvaporativeCoolingEntityDescription(
        key="evaporative_cooling_external_temp",
        translation_key="evaporative_cooling_external_temp",
        name="EC External Temperature Sensor",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        icon="mdi:air-conditioner",
        value_fn=lambda state: state.get("external_temp"),
    ),
    EvaporativeCoolingEntityDescription(
        key="evaporative_cooling_external_humidity",
        translation_key="evaporative_cooling_external_humidity",
        name="EC External Humidity Sensor",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:air-conditioner",
        value_fn=lambda state: state.get("external_humidity"),
    ),
    EvaporativeCoolingEntityDescription(
        key="evaporative_cooling_internal_temp",
        translation_key="evaporative_cooling_internal_temp",
        name="EC Internal Temperature Sensor",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        icon="mdi:air-conditioner",
        value_fn=lambda state: state.get("internal_temp"),
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
        entity_description: EvaporativeCoolingEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{entity_description.key}"
        # manufacturer="Sanfrancej.com",  # noqa: ERA001
        # version=VERSION,  # noqa: ERA001

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        state = self.coordinator.data
        if state is None:
            return None
        return self.entity_description.value_fn(state)

        # self.coordinator.data.get("body")
