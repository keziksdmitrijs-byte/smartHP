"""Time settings for SmartHP."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN, TIMES, TimeDesc
from .entity import SmartHPEntity
from .logic import parse_time


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SmartHPTime(coordinator, desc)
        for desc in TIMES
        if coordinator.supports(desc.requires)
    )


class SmartHPTime(SmartHPEntity, TimeEntity):
    """One time-of-day SmartHP setting."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator, desc: TimeDesc) -> None:
        super().__init__(coordinator, "time", desc.key)

    @property
    def native_value(self) -> time:
        return parse_time(self.coordinator.settings[self.key])

    async def async_set_value(self, value: time) -> None:
        await self.coordinator.async_set_setting(self.key, value.strftime("%H:%M:%S"))
