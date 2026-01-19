"""Adds config flow for EvaporativeCooling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from .api import (
    EvaporativeCoolingApiClient,
    EvaporativeCoolingConfigurationError,
    EvaporativeCoolingHumidityConfigurationError,
    EvaporativeCoolingTemperatureConfigurationError,
)
from .const import (
    CONF_HUMIDITY_SENSOR,
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
                domain=SENSOR_DOMAIN  # , filter={"integration": "weather"}
            ),
        ),
        vol.Required(CONF_TEMPERATURE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=SENSOR_DOMAIN  # , filter={"integration": "weather"}
            ),
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )
    LOGGER.debug("validate input data from config  %s", data)
    # do the validations step here for the two sensors (temp and humidity)
    api = EvaporativeCoolingApiClient(
        hass=hass,
        humidity_sensor_id=data[CONF_HUMIDITY_SENSOR],
        temp_sensor_id=data[CONF_TEMPERATURE_SENSOR],
        sensor_id=data[CONF_SENSOR_ID],
    )
    try:
        await hass.async_add_executor_job(api.connect)
    # Here the errors are EvaporativeCoolingTemperatureConfigurationError
    # EvaporativeCoolingHumidityConfigurationError
    # EvaporativeCoolingConfigurationError
    # If the authentication is wrong, raise InvalidAuth
    except EvaporativeCoolingTemperatureConfigurationError as err:
        raise ConfigEntryError from err
    except EvaporativeCoolingHumidityConfigurationError as err:
        raise ConfigEntryError from err
    except EvaporativeCoolingConfigurationError as err:
        raise ConfigEntryError from err

    return {"title": f"Evaoporative Cooling - {data[CONF_SENSOR_ID]}"}


class EvaporativeCoolingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for EvaporativeCooling."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except EvaporativeCoolingApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except EvaporativeCoolingApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except EvaporativeCoolingApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=slugify(user_input[CONF_USERNAME])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        client = EvaporativeCoolingApiClient(
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()


class EvaporativeCoolingOptionsFlowHandler(OptionsFlow):
    """Handles the options flow."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        # self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(title="", data=options)

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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
