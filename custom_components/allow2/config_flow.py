"""Config flow for Allow2 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    Allow2API,
    Allow2AuthError,
    Allow2ConnectionError,
    Allow2ResponseError,
    PairResult,
)
from .const import (
    CONF_CHILDREN,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TOKEN,
    CONF_PAIR_ID,
    CONF_PAIR_TOKEN,
    CONF_USER_ID,
    DEFAULT_DEVICE_NAME,
    DEFAULT_DEVICE_TOKEN,
    DOMAIN,
    ERROR_AUTH_FAILED,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_RESPONSE,
    ERROR_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_DEVICE_TOKEN, default=DEFAULT_DEVICE_TOKEN): str,
        vol.Optional(CONF_DEVICE_NAME, default=DEFAULT_DEVICE_NAME): str,
    }
)


class Allow2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Allow2.

    This config flow handles device pairing with the Allow2 service.
    Users provide their email and password, and the integration
    pairs with Allow2 to get persistent credentials (user_id, pair_id, pair_token).
    """

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._pair_result: PairResult | None = None
        self._device_token: str = DEFAULT_DEVICE_TOKEN
        self._device_name: str = DEFAULT_DEVICE_NAME

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - device pairing.

        This step collects email/password and pairs the device
        with Allow2, storing the credentials for future use.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Extract configuration
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            self._device_token = user_input.get(
                CONF_DEVICE_TOKEN, DEFAULT_DEVICE_TOKEN
            )
            self._device_name = user_input.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME)

            # Check if already configured for this email
            await self.async_set_unique_id(email.lower())
            self._abort_if_unique_id_configured()

            # Attempt to pair with Allow2
            try:
                session = async_get_clientsession(self.hass)
                api = Allow2API(
                    session=session,
                    device_token=self._device_token,
                    device_name=self._device_name,
                )

                self._pair_result = await api.pair(email, password)

                _LOGGER.info(
                    "Successfully paired with Allow2. User ID: %d, Pair ID: %d",
                    self._pair_result.user_id,
                    self._pair_result.pair_id,
                )

                # Store credentials and create the config entry
                return self.async_create_entry(
                    title=f"Allow2 ({email})",
                    data={
                        CONF_EMAIL: email,
                        CONF_USER_ID: self._pair_result.user_id,
                        CONF_PAIR_ID: self._pair_result.pair_id,
                        CONF_PAIR_TOKEN: self._pair_result.pair_token,
                        CONF_DEVICE_TOKEN: self._device_token,
                        CONF_DEVICE_NAME: self._device_name,
                        CONF_CHILDREN: self._pair_result.children,
                    },
                )

            except Allow2AuthError as err:
                _LOGGER.error("Authentication failed: %s", err)
                errors["base"] = ERROR_AUTH_FAILED
            except Allow2ConnectionError as err:
                _LOGGER.error("Connection error: %s", err)
                errors["base"] = ERROR_CANNOT_CONNECT
            except Allow2ResponseError as err:
                _LOGGER.error("Invalid response: %s", err)
                errors["base"] = ERROR_INVALID_RESPONSE
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during pairing: %s", err)
                errors["base"] = ERROR_UNKNOWN

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "default_token": DEFAULT_DEVICE_TOKEN,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> Allow2OptionsFlow:
        """Get the options flow for this handler."""
        return Allow2OptionsFlow(config_entry)


class Allow2OptionsFlow(config_entries.OptionsFlow):
    """Handle Allow2 options.

    Options flow allows users to update the device name
    and re-pair if needed.
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Update options
            return self.async_create_entry(title="", data=user_input)

        # Show current settings
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DEVICE_NAME,
                        default=self._config_entry.data.get(
                            CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME
                        ),
                    ): str,
                }
            ),
            errors=errors,
        )
