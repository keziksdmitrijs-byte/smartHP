"""Demand and state flags of SmartHP."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN, F_AUX, F_BLOCK, F_CIRC, F_DHW
from .entity import SmartHPEntity

BINARY_SENSORS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("summer_active", (), "mdi:white-balance-sunny"),
    ("hp_blocked", (F_BLOCK,), "mdi:lock"),
    ("legionella_active", (F_DHW,), "mdi:bacteria"),
    ("circ_demand", (F_CIRC,), "mdi:pump"),
    ("aux_demand", (F_AUX,), "mdi:fire"),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SmartHPBinarySensor(coordinator, key, icon)
        for key, requires, icon in BINARY_SENSORS
        if coordinator.supports(requires)
    )


class SmartHPBinarySensor(SmartHPEntity, BinarySensorEntity):
    """One SmartHP state flag."""

    def __init__(self, coordinator, key: str, icon: str) -> None:
        super().__init__(coordinator, "binary_sensor", key)
        self._attr_icon = icon

    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get(self.key))
