"""Base entity for SmartHP."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION
from .coordinator import SmartHPCoordinator


class SmartHPEntity(CoordinatorEntity[SmartHPCoordinator]):
    """Common properties of all SmartHP entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SmartHPCoordinator, platform: str, key: str) -> None:
        super().__init__(coordinator)
        self.key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self.entity_id = f"{platform}.{DOMAIN}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=coordinator.entry.title,
            manufacturer="SmartHP",
            model="Heat pump controller",
            sw_version=VERSION,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        """Settings stay available even if a source sensor is missing."""
        return True
