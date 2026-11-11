"""Adjustable parameters for SmartHP."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory

from .const import DOMAIN, NUMBERS, NumberDesc
from .entity import SmartHPEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SmartHPNumber(coordinator, desc)
        for desc in NUMBERS
        if coordinator.supports(desc.requires)
    )


class SmartHPNumber(SmartHPEntity, NumberEntity):
    """One numeric SmartHP setting."""

    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, desc: NumberDesc) -> None:
        super().__init__(coordinator, "number", desc.key)
        self._attr_icon = desc.icon
        self._attr_native_min_value = desc.min
        self._attr_native_max_value = desc.max
        self._attr_native_step = desc.step
        self._attr_native_unit_of_measurement = desc.unit

    @property
    def native_value(self) -> float:
        return float(self.coordinator.settings[self.key])

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_setting(self.key, float(value))
