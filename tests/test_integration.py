"""Integration tests running against a real Home Assistant core."""

from datetime import datetime, timedelta
import json
from pathlib import Path

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.smarthp import const
from custom_components.smarthp.const import DOMAIN

BASE = {
    "outdoor_sensor": "sensor.outdoor",
    "price_sensor": "sensor.price",
    "setpoint_entity": "input_number.hp_flow",
    "setpoint_mode": "flow",
    "block_switch": "switch.hp_enable",
    "block_inverted": False,
}
FULL = {
    **BASE,
    "circulation_pump": "switch.circ",
    "dhw_sensor": "sensor.boiler",
    "dhw_setpoint_entity": "input_number.dhw",
    "aux_heater": "switch.aux",
    "room_sensor": "sensor.room",
    "pv_sensor": "sensor.pv",
    "sg_ready_1": "switch.sg1",
    "sg_ready_2": "switch.sg2",
}


def _prices(hass: HomeAssistant, now: datetime) -> None:
    """Hourly prices 0.00 .. 0.23: hour N costs N cents."""
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    raw = [
        {"start": day + timedelta(hours=h), "end": day + timedelta(hours=h + 1), "value": h / 100}
        for h in range(24)
    ]
    hass.states.async_set("sensor.price", str(now.hour / 100), {"raw_today": raw})


def _states(hass: HomeAssistant, outdoor="-5") -> None:
    hass.states.async_set("sensor.outdoor", outdoor)
    hass.states.async_set("input_number.hp_flow", "30", {"min": 20, "max": 60, "step": 0.5})
    hass.states.async_set("input_number.dhw", "48", {"min": 30, "max": 70, "step": 1})
    hass.states.async_set("sensor.boiler", "50")
    hass.states.async_set("sensor.room", "21")
    hass.states.async_set("sensor.pv", "0")
    for name in ("hp_enable",):
        hass.states.async_set(f"switch.{name}", "on")
    for name in ("circ", "aux", "sg1", "sg2"):
        hass.states.async_set(f"switch.{name}", "off")


async def _setup(hass: HomeAssistant, data: dict, freezer, hour: int, outdoor="-5"):
    await hass.config.async_set_time_zone("Europe/Riga")
    now = datetime(2026, 1, 5, hour, 30, tzinfo=dt_util.get_time_zone("Europe/Riga"))
    freezer.move_to(now)
    _states(hass, outdoor)
    _prices(hass, now)
    calls = {
        "set_value": async_mock_service(hass, "input_number", "set_value"),
        "on": async_mock_service(hass, "homeassistant", "turn_on"),
        "off": async_mock_service(hass, "homeassistant", "turn_off"),
    }
    entry = MockConfigEntry(domain=DOMAIN, data=data, title="SmartHP")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry, calls


def _last_value(calls, entity_id):
    values = [c.data["value"] for c in calls["set_value"] if c.data["entity_id"] == entity_id]
    return values[-1] if values else None


def _switched(calls, kind, entity_id):
    return any(c.data["entity_id"] == entity_id for c in calls[kind])


async def test_config_flow(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "user"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "My HP", **BASE}
    )
    assert result["step_id"] == "optional"
    # only one SG Ready contact -> error
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"sg_ready_1": "switch.sg1"}
    )
    assert result["errors"] == {"base": "sg_both"}
    # the circulation pump is optional: finish without it
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "My HP"
    assert result["data"] == {**BASE, "nordpool_area": "LV", "vat_percent": 21.0}
    await hass.async_block_till_done()


async def test_minimal_setup_has_no_optional_entities(hass: HomeAssistant, freezer):
    data = {"outdoor_sensor": "sensor.outdoor", "price_sensor": "sensor.price", "setpoint_mode": "flow", "block_inverted": False}
    await _setup(hass, data, freezer, 12)
    assert hass.states.get("sensor.smarthp_target_flow").state == "37.5"
    assert hass.states.get("switch.smarthp_price_control") is not None
    for missing in (
        "switch.smarthp_circulation",
        "switch.smarthp_aux_by_temp",
        "number.smarthp_dhw_normal",
        "number.smarthp_room_target",
    ):
        assert hass.states.get(missing) is None


async def test_expensive_hour_only_shifts_setpoint(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, FULL, freezer, 20)
    assert hass.states.get("sensor.smarthp_price_level").state == "expensive"
    # curve at -5 C = 37.5, minus 3 C in expensive hours
    assert hass.states.get("sensor.smarthp_target_flow").state == "34.5"
    assert _last_value(calls, "input_number.hp_flow") == 34.5
    # the price never switches the heat pump off
    assert hass.states.get("switch.smarthp_hp_block") is None
    assert hass.states.get("binary_sensor.smarthp_hp_blocked").state == "off"
    assert not _switched(calls, "off", "switch.hp_enable")
    assert not _switched(calls, "on", "switch.sg1")
    assert hass.states.get("sensor.smarthp_sg_state").state == "2"
    assert hass.states.get("sensor.smarthp_status").state == "saving"
    # with an own price sensor the chart data is still provided
    assert len(hass.states.get("sensor.smarthp_current_price").attributes["today"]) == 24


async def test_cheap_hour_boosts_flow_and_dhw(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, FULL, freezer, 3)
    assert hass.states.get("sensor.smarthp_price_level").state == "cheap"
    assert _last_value(calls, "input_number.hp_flow") == 40.5
    assert hass.states.get("sensor.smarthp_sg_state").state == "3"
    assert _switched(calls, "on", "switch.sg2")
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": "switch.smarthp_dhw_price"}, blocking=True
    )
    assert _last_value(calls, "input_number.dhw") == 55


async def test_curve_edit_and_limits(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, BASE, freezer, 12)
    assert _last_value(calls, "input_number.hp_flow") == 37.5
    await hass.services.async_call(
        "number", "set_value", {"entity_id": "number.smarthp_curve_shift", "value": 3},
        blocking=True,
    )
    coordinator = next(iter(hass.data[DOMAIN].values()))
    assert hass.states.get("sensor.smarthp_target_flow").state == "40.5"
    await coordinator.async_set_setting("flow_max", 39.0)
    assert hass.states.get("sensor.smarthp_target_flow").state == "39.0"


async def test_offset_mode(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, {**BASE, "setpoint_mode": "offset"}, freezer, 20)
    hass.states.async_set("input_number.hp_flow", "0", {"min": -10, "max": 10, "step": 1})
    coordinator = next(iter(hass.data[DOMAIN].values()))
    await coordinator.async_refresh()
    assert _last_value(calls, "input_number.hp_flow") == -3


async def test_circulation_schedule_and_boiler_temperature(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, FULL, freezer, 7)  # 07:30, window 06:00-08:00
    coordinator = next(iter(hass.data[DOMAIN].values()))
    # 90 min into the window, 5 on / 15 off -> pause phase
    assert hass.states.get("binary_sensor.smarthp_circ_demand").state == "off"
    await coordinator.async_set_setting("circ_off_minutes", 0.0)
    assert hass.states.get("binary_sensor.smarthp_circ_demand").state == "on"
    assert _switched(calls, "on", "switch.circ")
    # boiler too cold -> no circulation
    hass.states.async_set("sensor.boiler", "30")
    await coordinator.async_set_setting("circ_use_temp", True)
    assert hass.states.get("binary_sensor.smarthp_circ_demand").state == "off"
    hass.states.async_set("sensor.boiler", "45")
    await coordinator.async_refresh()
    assert hass.states.get("binary_sensor.smarthp_circ_demand").state == "on"
    # outside every window
    freezer.move_to(datetime(2026, 1, 5, 12, 0, tzinfo=dt_util.get_time_zone("Europe/Riga")))
    await coordinator.async_refresh()
    assert hass.states.get("binary_sensor.smarthp_circ_demand").state == "off"


async def test_aux_heater_by_temperature_and_price(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, FULL, freezer, 12, outdoor="-20")
    assert hass.states.get("binary_sensor.smarthp_aux_demand").state == "on"
    assert _switched(calls, "on", "switch.aux")

    coordinator = next(iter(hass.data[DOMAIN].values()))
    hass.states.async_set("sensor.outdoor", "0")
    await coordinator.async_set_setting("aux_min_run", 0.0)
    assert hass.states.get("binary_sensor.smarthp_aux_demand").state == "off"
    # price 0.12 > limit 0.10 -> heater on and heat pump stopped
    await coordinator.async_set_setting("aux_by_price", True)
    await coordinator.async_set_setting("aux_blocks_hp", True)
    await coordinator.async_set_setting("aux_price_limit", 0.10)
    assert hass.states.get("binary_sensor.smarthp_aux_demand").state == "on"
    assert hass.states.get("binary_sensor.smarthp_hp_blocked").state == "on"


async def test_summer_room_night_vacation_pv(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, FULL, freezer, 12)
    coordinator = next(iter(hass.data[DOMAIN].values()))
    base = 37.5
    hass.states.async_set("sensor.room", "20")
    await coordinator.async_set_setting("room_compensation", True)
    assert float(hass.states.get("sensor.smarthp_target_flow").state) == base + 2
    await coordinator.async_set_setting("room_compensation", False)
    await coordinator.async_set_setting("vacation", True)
    assert float(hass.states.get("sensor.smarthp_target_flow").state) == base - 5
    await coordinator.async_set_setting("vacation", False)
    hass.states.async_set("sensor.pv", "2500")
    await coordinator.async_set_setting("pv_boost", True)
    assert float(hass.states.get("sensor.smarthp_target_flow").state) == base + 3
    assert hass.states.get("sensor.smarthp_sg_state").state == "4"
    await coordinator.async_set_setting("pv_boost", False)
    await coordinator.async_set_setting("night_start", "11:00:00")
    await coordinator.async_set_setting("night_end", "13:00:00")
    await coordinator.async_set_setting("night_setback", True)
    assert float(hass.states.get("sensor.smarthp_target_flow").state) == base - 2
    hass.states.async_set("sensor.outdoor", "18")
    await coordinator.async_refresh()
    assert hass.states.get("binary_sensor.smarthp_summer_active").state == "on"
    assert hass.states.get("sensor.smarthp_status").state == "summer"
    assert _last_value(calls, "input_number.hp_flow") == 20


async def test_legionella_cycle(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, FULL, freezer, 3)  # Monday 03:30
    coordinator = next(iter(hass.data[DOMAIN].values()))
    await coordinator.async_set_setting("legionella_day", "mon")
    await coordinator.async_set_setting("legionella", True)
    assert hass.states.get("binary_sensor.smarthp_legionella_active").state == "on"
    assert _last_value(calls, "input_number.dhw") == 62
    hass.states.async_set("input_number.dhw", "62", {"min": 30, "max": 70, "step": 1})
    hass.states.async_set("sensor.boiler", "63")
    await coordinator.async_refresh()
    assert hass.states.get("binary_sensor.smarthp_legionella_active").state == "off"
    assert _last_value(calls, "input_number.dhw") == 48


async def test_disable_releases_block_and_unload(hass: HomeAssistant, freezer):
    entry, calls = await _setup(hass, FULL, freezer, 20)
    coordinator = next(iter(hass.data[DOMAIN].values()))
    # heater on price with "stop heat pump" -> blocked
    await coordinator.async_set_setting("aux_by_price", True)
    await coordinator.async_set_setting("aux_blocks_hp", True)
    await coordinator.async_set_setting("aux_price_limit", 0.10)
    assert _switched(calls, "off", "switch.hp_enable")
    hass.states.async_set("switch.hp_enable", "off")
    await coordinator.async_set_setting("enabled", False)
    assert hass.states.get("sensor.smarthp_status").state == "disabled"
    assert _switched(calls, "on", "switch.hp_enable")
    count = len(calls["set_value"])
    await coordinator.async_set_setting("curve_shift", 5.0)
    assert len(calls["set_value"]) == count  # nothing is written while disabled
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_settings_survive_reload(hass: HomeAssistant, freezer, hass_storage):
    entry, _ = await _setup(hass, BASE, freezer, 12)
    coordinator = next(iter(hass.data[DOMAIN].values()))
    await coordinator.async_set_setting("curve_0", 33.0)
    freezer.tick(timedelta(seconds=5))
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get("number.smarthp_curve_0").state == "33.0"


async def test_unavailable_outdoor_writes_nothing(hass: HomeAssistant, freezer):
    _, calls = await _setup(hass, BASE, freezer, 12, outdoor="unavailable")
    assert hass.states.get("sensor.smarthp_status").state == "no_data"
    assert calls["set_value"] == []


def _nordpool_payload(day: str, first_utc: datetime) -> dict:
    """96 quarter-hour prices; local (Riga) hour N costs N * 10 EUR/MWh."""
    riga = dt_util.get_time_zone("Europe/Riga")
    entries = []
    for i in range(96):
        start = first_utc + timedelta(minutes=15 * i)
        entries.append(
            {
                "deliveryStart": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "deliveryEnd": (start + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entryPerArea": {"LV": start.astimezone(riga).hour * 10.0},
            }
        )
    return {"deliveryDateCET": day, "currency": "EUR", "multiAreaEntries": entries}


async def test_builtin_nordpool(hass: HomeAssistant, freezer, aioclient_mock):
    from datetime import timezone

    from custom_components.smarthp.const import NORDPOOL_URL

    for day, first in (
        ("2026-01-04", datetime(2026, 1, 3, 23, tzinfo=timezone.utc)),
        ("2026-01-05", datetime(2026, 1, 4, 23, tzinfo=timezone.utc)),
    ):
        aioclient_mock.get(
            NORDPOOL_URL.format(date=day, area="LV"), json=_nordpool_payload(day, first)
        )
    aioclient_mock.get(NORDPOOL_URL.format(date="2026-01-06", area="LV"), status=204)

    data = {k: v for k, v in BASE.items() if k != "price_sensor"}
    data.update({"nordpool_area": "LV", "vat_percent": 21.0})
    _, calls = await _setup(hass, data, freezer, 20)  # 20:30 Riga
    price = hass.states.get("sensor.smarthp_current_price")
    # 200 EUR/MWh -> 0.2 EUR/kWh + 21 % VAT
    assert float(price.state) == 0.242
    assert price.attributes["periods_today"] == 96
    assert price.attributes["unit_of_measurement"] == "EUR/kWh"
    today = price.attributes["today"]
    assert len(today) == 96
    assert today[0] == {
        "start": "2026-01-05T00:00+02:00", "end": "2026-01-05T00:15+02:00",
        "price": 0.0, "level": "cheap",
    }
    assert today[-1]["level"] == "expensive" and today[48]["level"] == "normal"
    assert price.attributes["today_max"] == 0.2783
    assert hass.states.get("sensor.smarthp_price_level").state == "expensive"
    assert _last_value(calls, "input_number.hp_flow") == 34.5
    # yesterday + today are downloaded once; tomorrow answered 204 and is not retried at once
    count = aioclient_mock.call_count
    assert count == 3
    coordinator = next(iter(hass.data[DOMAIN].values()))
    await coordinator.async_refresh()
    assert aioclient_mock.call_count == count

    freezer.move_to(datetime(2026, 1, 5, 3, 30, tzinfo=dt_util.get_time_zone("Europe/Riga")))
    await coordinator.async_refresh()
    assert hass.states.get("sensor.smarthp_price_level").state == "cheap"
    assert _last_value(calls, "input_number.hp_flow") == 40.5


async def test_builtin_nordpool_offline(hass: HomeAssistant, freezer, aioclient_mock):
    import aiohttp

    from custom_components.smarthp.const import NORDPOOL_URL

    for day in ("2026-01-04", "2026-01-05", "2026-01-06"):
        aioclient_mock.get(
            NORDPOOL_URL.format(date=day, area="LV"), exc=aiohttp.ClientError("offline")
        )
    data = {k: v for k, v in BASE.items() if k != "price_sensor"}
    _, calls = await _setup(hass, data, freezer, 20)
    assert hass.states.get("sensor.smarthp_price_level").state == "unknown"
    # heating curve keeps working without prices
    assert _last_value(calls, "input_number.hp_flow") == 37.5


def test_every_entity_is_translated():
    root = Path(const.__file__).parent
    from custom_components.smarthp.binary_sensor import BINARY_SENSORS
    from custom_components.smarthp.sensor import SENSORS

    expected = {
        "number": {d.key for d in const.NUMBERS},
        "switch": {d.key for d in const.SWITCHES},
        "time": {d.key for d in const.TIMES},
        "select": {d.key for d in const.SELECTS},
        "sensor": {d.key for d in SENSORS},
        "binary_sensor": {b[0] for b in BINARY_SENSORS},
    }
    all_keys = [k for keys in expected.values() for k in keys]
    assert len(all_keys) == len(set(all_keys)), "keys must be unique across platforms"
    for lang in ("en", "ru", "lv"):
        data = json.loads((root / "translations" / f"{lang}.json").read_text("utf-8"))
        for platform, keys in expected.items():
            assert set(data["entity"][platform]) == keys, (lang, platform)
    assert json.loads((root / "strings.json").read_text("utf-8")) == json.loads(
        (root / "translations" / "en.json").read_text("utf-8")
    )
