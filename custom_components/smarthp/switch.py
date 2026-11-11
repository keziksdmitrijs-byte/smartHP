"""Feature switches for SmartHP."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN, SWITCHES, SwitchDesc
from .entity import SmartHPEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SmartHPSwitch(coordinator, desc)
        for desc in SWITCHES
        if coordinator.supports(desc.requires)
    )


class SmartHPSwitch(SmartHPEntity, SwitchEntity):
    """Turns one SmartHP function on or off."""

    def __init__(self, coordinator, desc: SwitchDesc) -> None:
        super().__init__(coordinator, "switch", desc.key)
        self._attr_icon = desc.icon
        if desc.config:
            self._attr_entity_category = EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.settings[self.key])

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_setting(self.key, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_setting(self.key, False)
