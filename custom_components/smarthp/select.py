"""Select settings for SmartHP."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN, SELECTS, SelectDesc
from .entity import SmartHPEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SmartHPSelect(coordinator, desc)
        for desc in SELECTS
        if coordinator.supports(desc.requires)
    )


class SmartHPSelect(SmartHPEntity, SelectEntity):
    """One choice SmartHP setting."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:calendar-week"

    def __init__(self, coordinator, desc: SelectDesc) -> None:
        super().__init__(coordinator, "select", desc.key)
        self._attr_options = list(desc.options)

    @property
    def current_option(self) -> str:
        return str(self.coordinator.settings[self.key])

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_setting(self.key, option)
