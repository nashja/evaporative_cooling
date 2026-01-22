"""Adds config flow for EvaporativeCooling."""

from __future__ import annotations

from tkinter import SE
from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    SensorDeviceClass,
    # SensorEntity,
    # SensorStateClass,
)
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import selector

from .api import (
    EvaporativeCoolingApiClient,
    EvaporativeCoolingConfigurationError,
    EvaporativeCoolingHumidityConfigurationError,
    EvaporativeCoolingReadoutError,
    EvaporativeCoolingTemperatureConfigurationError,
)
from .const import (
    CONF_HUMIDITY_SENSOR,
    CONF_MONITOR_SENSOR,
    CONF_SENSOR_ID,
    CONF_TEMPERATURE_SENSOR,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    MIN_SCAN_INTERVAL,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

STEP_SETTINGS_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSOR_ID): cv.string,
        vol.Required(CONF_HUMIDITY_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=SENSOR_DOMAIN,
                device_class=SensorDeviceClass.HUMIDITY,  # , filter={"integration": "weather"}
            ),
        ),
        vol.Required(CONF_TEMPERATURE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=SENSOR_DOMAIN,  # ,
                device_class=SensorDeviceClass.TEMPERATURE,
            ),
        ),
        vol.Optional(CONF_MONITOR_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=SENSOR_DOMAIN,
                device_class=SensorDeviceClass.TEMPERATURE,  # , filter={"integration": "weather"}
            ),
        ),
    }
)


class EvaporativeCoolingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for EvaporativeCooling."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> EvaporativeCoolingOptionsFlowHandler:
        """Get the options flow for this handler."""
        # Remove this method and the ExampleOptionsFlowHandler class
        # if you do not want any options for your integration.
        return EvaporativeCoolingOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        # Called when you initiate adding an integration via the UI
        errors: dict[str, str] = {}

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.
            try:
                # Validate that the setup data is valid and if not handle errors.
                # The errors["base"] values match the values in your strings.json and translation files.pi
                # info = await validate_input(self.hass, user_input)
                info = {"title": "ECUnique"}
                LOGGER.debug("setting info - not now validating")
            except ConfigEntryError:
                errors["base"] = "configuration"
            except EvaporativeCoolingTemperatureConfigurationError:
                errors["base"] = "temperature_sensor"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                # Validation was successful, so create a unique id for this instance of your integration
                # and create the config entry.
                await self.async_set_unique_id(info.get("title"))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        # Show initial form.

        return self.async_show_form(
            step_id="user", data_schema=STEP_SETTINGS_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add reconfigure step to allow to reconfigure a config entry."""
        # This methid displays a reconfigure option in the integration and is
        # different to options.
        # It can be used to reconfigure any of the data submitted when first installed.
        # This is optional and can be removed if you do not want to allow reconfiguration.
        errors: dict[str, str] = {}
        config_entry = self._get_reconfigure_entry()
        if user_input is not None:
            try:
                user_input[CONF_HUMIDITY_SENSOR] = config_entry.data[
                    CONF_HUMIDITY_SENSOR
                ]
                user_input[CONF_TEMPERATURE_SENSOR] = config_entry.data[
                    CONF_TEMPERATURE_SENSOR
                ]
                user_input[CONF_SENSOR_ID] = config_entry.data[CONF_SENSOR_ID]
                # await validate_input(self.hass, user_input)

            except ConfigEntryError:
                errors["base"] = "configuration"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    config_entry,
                    unique_id=config_entry.unique_id,
                    data={**config_entry.data, **user_input},
                    reason="reconfigure_successful",
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HUMIDITY_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=SENSOR_DOMAIN,
                            device_class=SensorDeviceClass.HUMIDITY,  # , filter={"integration": "weather"}
                        ),
                    ),
                    vol.Required(CONF_TEMPERATURE_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=SENSOR_DOMAIN,
                            device_class=SensorDeviceClass.TEMPERATURE,  # , filter={"integration": "weather"}
                        ),
                    ),
                }
            ),
            errors=errors,
        )


class EvaporativeCoolingOptionsFlowHandler(OptionsFlow):
    """Handles the options flow."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Handle options flow."""
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(title="", data=options)  # type: ignore
        # It is recommended to prepopulate options fields with default values if available.
        # These will be the same default values you use on your coordinator for setting variable values
        # if the option has not been set.
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): (vol.All(vol.Coerce(int), vol.Clamp(min=MIN_SCAN_INTERVAL))),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
