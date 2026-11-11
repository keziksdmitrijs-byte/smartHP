"""SmartHP - price and weather based heat pump control."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, FRONTEND_URL, PANEL_URL_PATH, PLATFORMS, VERSION
from .coordinator import SmartHPCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve the Lovelace card and register the sidebar panel."""
    hass.data.setdefault(DOMAIN, {})
    await _async_register_frontend(hass)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    if hass.http is None:
        return
    card = Path(__file__).parent / "frontend" / "smarthp-card.js"
    module_url = f"{FRONTEND_URL}?v={VERSION}"
    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(FRONTEND_URL, str(card), False)]
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("SmartHP: could not serve the card: %s", err)
        return
    if "frontend" not in hass.config.components:
        return
    try:
        from homeassistant.components.frontend import add_extra_js_url

        add_extra_js_url(hass, module_url)
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("SmartHP: could not register the card: %s", err)
    try:
        from homeassistant.components import panel_custom

        await panel_custom.async_register_panel(
            hass,
            webcomponent_name="smarthp-panel",
            frontend_url_path=PANEL_URL_PATH,
            module_url=module_url,
            sidebar_title="SmartHP",
            sidebar_icon="mdi:heat-pump",
            require_admin=False,
            config={},
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("SmartHP: could not register the panel: %s", err)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartHP from a config entry."""
    coordinator = SmartHPCoordinator(hass, entry)
    await coordinator.async_load()
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def _on_stop(event: Event) -> None:
        await coordinator.async_release()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _on_stop))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and release any heat pump block."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator: SmartHPCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_release()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Delete stored settings when the entry is removed."""
    await SmartHPCoordinator(hass, entry).async_remove_store()
