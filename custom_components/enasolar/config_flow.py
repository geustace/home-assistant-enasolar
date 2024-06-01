"""EnaSolar solar inverter configuration."""
from __future__ import annotations

import contextlib
import logging
import socket
from typing import Any

import aiohttp
import pyenasolar
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_CAPABILITY,
    CONF_DC_STRINGS,
    CONF_HOST,
    CONF_MAX_OUTPUT,
    CONF_NAME,
    CONF_NO_SUN,
    DC_STRINGS,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DOMAIN,
    HAS_POWER_METER,
    HAS_SOLAR_METER,
    HAS_TEMPERATURE,
    MAX_OUTPUT,
    USE_FAHRENHIET,
)

_LOGGER = logging.getLogger(__name__)


def _get_ip(host: str) -> str | None:
    """Get the ip address from the host name."""
    with contextlib.suppress(socket.gaierror):
        return socket.gethostbyname(host)
    return None


class EnaSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """User Configuration of EnaSolar Integration."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        # Only exposes methods, no significant
        # code is executed during instantiation
        self._enasolar = pyenasolar.EnaSolar()
        self._data: dict[str, Any] = {}

    def _conf_for_inverter_exists(self, serial: str) -> bool:
        """Return True if inverter exists in configuration."""
        return any(
            entry
            for entry in self._async_current_entries(include_ignore=False)
            if serial == entry.unique_id
        )

    async def _try_connect(self, host: str) -> str | None:
        """Needed to mock connection when running tests."""
        error = None
        try:
            await self._enasolar.interogate_inverter(host)
        except aiohttp.client_exceptions.ClientConnectorError:
            error = "cannot_connect"
        except aiohttp.client_exceptions.ClientResponseError:
            error = "unexpected_response"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            error = "unknown"
        return error


    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get options flow for this handler."""
        return EnaSolarOptionsFlowHandler(config_entry)


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step when user initializes an integration."""
        _errors: dict[str, Any] = {}

        if user_input is not None:
            ip_address = await self.hass.async_add_executor_job(
                _get_ip, user_input[CONF_HOST]
            )
            if not ip_address:
                _errors[CONF_HOST] = "invalid_host"
            else:
                self._data[CONF_HOST] = user_input[CONF_HOST]
                self._data[CONF_NAME] = user_input[CONF_NAME]
                error = await self._try_connect(self._data[CONF_HOST])
                if error is not None:
                    _errors[CONF_HOST] = error
                else:
                    if self._conf_for_inverter_exists(self._enasolar.get_serial_no()):
                        return self.async_abort(reason="already_configured")
                    await self.async_set_unique_id(self._enasolar.get_serial_no())
                    return await self.async_step_inverter(None)
        else:
            user_input = {}
            user_input[CONF_NAME] = DEFAULT_NAME
            user_input[CONF_HOST] = DEFAULT_HOST

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): cv.string,
                    vol.Optional(CONF_NAME, default=user_input[CONF_NAME]): cv.string,
                }
            ),
            errors=_errors,
            last_step=False,
        )

    async def async_step_inverter(
        self, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Give the user the opportunities to override inverter config."""

        _errors: dict[str, Any] = {}
        if user_input is not None:
            # CAPABILITY is a 9 bit value, bits 1-3 and 9 representing
            # what features the Innverter has.
            cap: int = 0
            if "power" in user_input[CONF_CAPABILITY]:
                cap |= HAS_POWER_METER
            if "solar" in user_input[CONF_CAPABILITY]:
                cap |= HAS_SOLAR_METER
            if "temperature" in user_input[CONF_CAPABILITY]:
                cap |= HAS_TEMPERATURE
            if "fahrenhiet" in user_input[CONF_CAPABILITY]:
                cap |= USE_FAHRENHIET
            user_input[CONF_CAPABILITY] = cap
            self._data.update(user_input)
            title = self._data[CONF_NAME]
            return self.async_create_entry(title=title, data=self._data)

        # Use the capability bits from the Inverter. This assumes it
        # had been possible to actually scrape them from the jScript
        capabilities = []
        caps = self._enasolar.get_capability()
        if caps & HAS_POWER_METER:
            capabilities.append("power")
        if caps & HAS_SOLAR_METER:
            capabilities.append("solar")
        if caps & HAS_TEMPERATURE:
            capabilities.append("temperature")
        if caps & USE_FAHRENHIET:
            capabilities.append("fahrenhiet")

        return self.async_show_form(
            step_id="inverter",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MAX_OUTPUT, default=self._enasolar.get_max_output()
                    ): vol.In(MAX_OUTPUT),
                    vol.Required(
                        CONF_DC_STRINGS, default=self._enasolar.get_dc_strings()
                    ): vol.In(DC_STRINGS),
                    vol.Optional(
                        CONF_CAPABILITY, default=capabilities
                    ): cv.multi_select(
                        {
                            "power": "has a POWER meter",
                            "solar": "has a SOLAR meter",
                            "temperature": "has a TEMPERATURE meter",
                            "fahrenhiet": "Temperatures are in FAHRENHIET",
                        }
                    )
                }
            ),
            errors=_errors,
            last_step=True,
        )


class EnaSolarOptionsFlowHandler(config_entries.OptionsFlow):
    """Set Polling window to be updated."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize EnaSolar options flow."""
        self.config_entry = config_entry
        self._options = dict(config_entry.options)

    async def async_step_init(self, user_input: dict[str, Any] | None) -> FlowResult:
        """Allow user to update polling."""

        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(title="", data=self._options)
        else:
            user_input = {}
            if self._options:
                user_input.update(self._options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NO_SUN, default=user_input.get(CONF_NO_SUN, False)
                    ): cv.boolean,
                }
            ),
            errors=None,
            last_step=True
        )
