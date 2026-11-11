"""Calculated values of SmartHP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature

from .const import CONF_PRICE, DOMAIN, F_DHW, F_SG, LEVELS, STATUSES
from .entity import SmartHPEntity


@dataclass(frozen=True)
class SensorDesc:
    key: str
    kind: str  # temp | delta | percent | enum | plain
    requires: tuple[str, ...] = ()
    options: tuple[str, ...] = ()
    icon: str | None = None


SENSORS: tuple[SensorDesc, ...] = (
    SensorDesc("status", "enum", options=tuple(STATUSES), icon="mdi:heat-pump"),
    SensorDesc("target_flow", "temp", icon="mdi:thermometer-auto"),
    SensorDesc("curve_flow", "temp", icon="mdi:chart-bell-curve-cumulative"),
    SensorDesc("total_offset", "delta", icon="mdi:plus-minus-variant"),
    SensorDesc("outdoor_filtered", "temp", icon="mdi:thermometer"),
    SensorDesc("price_level", "enum", options=tuple(LEVELS), icon="mdi:cash-clock"),
    SensorDesc("price_rank", "percent", icon="mdi:sort-numeric-ascending"),
    SensorDesc("current_price", "price", icon="mdi:currency-eur"),
    SensorDesc("dhw_target", "temp", (F_DHW,), icon="mdi:water-thermometer"),
    SensorDesc("sg_state", "plain", (F_SG,), icon="mdi:transmission-tower"),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SmartHPSensor(coordinator, desc)
        for desc in SENSORS
        if coordinator.supports(desc.requires)
    )


class SmartHPSensor(SmartHPEntity, SensorEntity):
    """One calculated SmartHP value."""

    def __init__(self, coordinator, desc: SensorDesc) -> None:
        super().__init__(coordinator, "sensor", desc.key)
        self._attr_icon = desc.icon
        self._unit: str | None = None
        if desc.kind == "temp":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._unit = UnitOfTemperature.CELSIUS
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif desc.kind == "delta":
            self._unit = UnitOfTemperature.CELSIUS
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif desc.kind == "percent":
            self._unit = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif desc.kind == "price":
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_suggested_display_precision = 4
        elif desc.kind == "enum":
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = list(desc.options)

    _unrecorded_attributes = frozenset({"today"})

    @property
    def native_unit_of_measurement(self) -> str | None:
        if self.key != "current_price":
            return self._unit
        if self.coordinator.builtin_prices:
            return "EUR/kWh"
        source = self.hass.states.get(self.coordinator.conf.get(CONF_PRICE) or "")
        return source.attributes.get("unit_of_measurement") if source else None

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get(self.key)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        if self.key == "target_flow":
            return {f"offset_{k}": v for k, v in data.get("offsets", {}).items()}
        if self.key == "current_price":
            return {**(data.get("price_stats") or {}), "today": data.get("price_today") or []}
        if self.key == "price_level":
            return {"price": data.get("price")}
        return None
