"""Config flow for SmartHP."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AREA,
    CONF_AUX,
    CONF_BLOCK,
    CONF_BLOCK_INVERTED,
    CONF_CIRC,
    CONF_DHW_SETPOINT,
    CONF_DHW_TEMP,
    CONF_OUTDOOR,
    CONF_PRICE,
    CONF_PV,
    CONF_ROOM,
    CONF_SETPOINT,
    CONF_SETPOINT_MODE,
    CONF_SG1,
    CONF_SG2,
    CONF_VAT,
    DEFAULT_AREA,
    DEFAULT_VAT,
    DOMAIN,
    MODE_FLOW,
    MODE_OFFSET,
    NORDPOOL_AREAS,
)

SENSOR = ["sensor", "input_number", "number"]
SWITCH = ["switch", "input_boolean"]


def _entity(domains: list[str]) -> selector.EntitySelector:
    return selector.EntitySelector(selector.EntitySelectorConfig(domain=domains))


def _main_schema(with_name: bool) -> vol.Schema:
    fields: dict[Any, Any] = {}
    if with_name:
        fields[vol.Required(CONF_NAME, default="SmartHP")] = selector.TextSelector()
    fields.update(
        {
            vol.Required(CONF_OUTDOOR): _entity(SENSOR),
            vol.Required(CONF_AREA, default=DEFAULT_AREA): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=NORDPOOL_AREAS, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(CONF_VAT, default=DEFAULT_VAT): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=50, step=0.1, unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_PRICE): _entity(SENSOR),
            vol.Optional(CONF_SETPOINT): _entity(["number", "input_number", "climate"]),
            vol.Required(CONF_SETPOINT_MODE, default=MODE_FLOW): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[MODE_FLOW, MODE_OFFSET],
                    translation_key=CONF_SETPOINT_MODE,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Optional(CONF_BLOCK): _entity(SWITCH),
            vol.Required(CONF_BLOCK_INVERTED, default=False): selector.BooleanSelector(),
        }
    )
    return vol.Schema(fields)


OPTIONAL_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_CIRC): _entity(SWITCH),
        vol.Optional(CONF_DHW_TEMP): _entity(SENSOR),
        vol.Optional(CONF_DHW_SETPOINT): _entity(
            ["number", "input_number", "water_heater", "climate"]
        ),
        vol.Optional(CONF_AUX): _entity(SWITCH),
        vol.Optional(CONF_ROOM): _entity(SENSOR),
        vol.Optional(CONF_PV): _entity(SENSOR),
        vol.Optional(CONF_SG1): _entity(SWITCH),
        vol.Optional(CONF_SG2): _entity(SWITCH),
    }
)


def _validate_optional(data: dict[str, Any]) -> dict[str, str]:
    if bool(data.get(CONF_SG1)) != bool(data.get(CONF_SG2)):
        return {"base": "sg_both"}
    return {}


class SmartHPConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask which entities SmartHP should read and control."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._data = dict(user_input)
            return await self.async_step_optional()
        return self.async_show_form(step_id="user", data_schema=_main_schema(True))

    async def async_step_optional(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_optional(user_input)
            if not errors:
                data = {**self._data, **user_input}
                title = data.pop(CONF_NAME, "SmartHP") or "SmartHP"
                return self.async_create_entry(title=title, data=data)
        schema = self.add_suggested_values_to_schema(OPTIONAL_SCHEMA, user_input or {})
        return self.async_show_form(
            step_id="optional", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SmartHPOptionsFlow()


class SmartHPOptionsFlow(OptionsFlow):
    """Change the linked entities later."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._data = dict(user_input)
            return await self.async_step_optional()
        schema = self.add_suggested_values_to_schema(
            _main_schema(False), dict(self.config_entry.data)
        )
        return self.async_show_form(step_id="init", data_schema=schema)

    async def async_step_optional(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_optional(user_input)
            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data={**self._data, **user_input}
                )
                self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})
        schema = self.add_suggested_values_to_schema(
            OPTIONAL_SCHEMA, user_input or dict(self.config_entry.data)
        )
        return self.async_show_form(
            step_id="optional", data_schema=schema, errors=errors
        )
