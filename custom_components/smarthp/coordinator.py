"""Control logic for SmartHP."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
import logging
import math
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    ANTISEIZE_INTERVAL_HOURS,
    ANTISEIZE_RUN_SECONDS,
    CIRC_TEMP_HYSTERESIS,
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
    CURVE_POINTS,
    DEFAULT_AREA,
    DEFAULT_VAT,
    DOMAIN,
    F_AUX,
    F_BLOCK,
    F_CIRC,
    F_DHW,
    F_DHW_TEMP,
    F_PV,
    F_ROOM,
    F_SG,
    LEGIONELLA_MAX_MINUTES,
    LEVEL_CHEAP,
    LEVEL_EXPENSIVE,
    MODE_OFFSET,
    NORDPOOL_TIMEZONE,
    NORDPOOL_URL,
    SUMMER_HYSTERESIS,
    WEEKDAYS,
    default_settings,
)
from .logic import (
    PriceSlot,
    clamp,
    classify,
    interpolate,
    parse_time,
    price_rank,
    rank_in_samples,
    round_step,
    slots_from_attributes,
    slots_from_list,
    window_elapsed,
)

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=60)
STORAGE_VERSION = 1
PRICE_FETCH_RETRY = timedelta(minutes=10)


class SmartHPCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Calculates targets every minute and writes them to the linked entities."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.entry = entry
        self.conf: dict[str, Any] = dict(entry.data)
        self.settings: dict[str, Any] = default_settings()
        self._store: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")

        self.features: set[str] = set()
        has_sg = bool(self.conf.get(CONF_SG1) and self.conf.get(CONF_SG2))
        if has_sg:
            self.features.add(F_SG)
        if self.conf.get(CONF_BLOCK) or has_sg:
            self.features.add(F_BLOCK)
        for conf_key, feature in (
            (CONF_ROOM, F_ROOM),
            (CONF_PV, F_PV),
            (CONF_DHW_SETPOINT, F_DHW),
            (CONF_DHW_TEMP, F_DHW_TEMP),
            (CONF_CIRC, F_CIRC),
            (CONF_AUX, F_AUX),
        ):
            if self.conf.get(conf_key):
                self.features.add(feature)
        if not self.conf.get(CONF_PRICE):
            self.features.add("builtin_prices")

        # runtime state
        self._filtered: float | None = None
        self._last_calc: datetime | None = None
        self._summer = False
        self._pv_active = False
        self._block_since: datetime | None = None
        self._pause_until: datetime | None = None
        self._was_enabled = True
        self._legionella_done: Any = None
        self._circ_temp_ok = False
        self._circ_last_run: datetime | None = None
        self._antiseize_until: datetime | None = None
        self._aux_temp_on = False
        self._aux_on_since: datetime | None = None
        self._price_samples: deque[tuple[datetime, float]] = deque()
        self._fetched_slots: list[PriceSlot] = []
        self._fetched_date: Any = None
        self._fetch_after: datetime | None = None
        self.builtin_prices = not self.conf.get(CONF_PRICE)
        self._np_cache: dict[Any, list[PriceSlot]] = {}
        self._np_retry: dict[Any, datetime] = {}

    # ------------------------------------------------------------------ setup
    def supports(self, requires: tuple[str, ...]) -> bool:
        """Return True if all required optional entities were configured."""
        return all(req in self.features for req in requires)

    async def async_load(self) -> None:
        """Load saved settings and start listening to the source entities."""
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            for key, value in stored.items():
                if key in self.settings and value is not None:
                    self.settings[key] = value
        self._circ_last_run = dt_util.now()

        watched = [
            self.conf.get(key)
            for key in (CONF_OUTDOOR, CONF_PRICE, CONF_ROOM, CONF_PV, CONF_DHW_TEMP)
            if self.conf.get(key)
        ]
        self.entry.async_on_unload(
            async_track_state_change_event(self.hass, watched, self._source_changed)
        )

    @callback
    def _source_changed(self, event: Event) -> None:
        self.hass.async_create_task(self.async_request_refresh())

    async def async_set_setting(self, key: str, value: Any) -> None:
        """Change one setting, persist it and recalculate immediately."""
        self.settings[key] = value
        self._store.async_delay_save(lambda: dict(self.settings), 2)
        await self.async_refresh()

    async def async_remove_store(self) -> None:
        """Delete saved settings."""
        await self._store.async_remove()

    # ---------------------------------------------------------------- helpers
    def _float(self, conf_key: str) -> float | None:
        entity_id = self.conf.get(conf_key)
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        return value if math.isfinite(value) else None

    async def _call(self, domain: str, service: str, data: dict[str, Any]) -> None:
        try:
            await self.hass.services.async_call(domain, service, data, blocking=True)
        except Exception as err:  # noqa: BLE001 - a failing target must not stop control
            _LOGGER.warning("SmartHP: %s.%s %s failed: %s", domain, service, data, err)

    async def _set_switch(self, entity_id: str | None, turn_on: bool) -> None:
        if not entity_id:
            return
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unavailable", "unknown"):
            return
        if (state.state == STATE_ON) == turn_on:
            return
        await self._call(
            "homeassistant",
            "turn_on" if turn_on else "turn_off",
            {"entity_id": entity_id},
        )

    async def _set_value(self, entity_id: str | None, value: float | None) -> None:
        if not entity_id or value is None:
            return
        state = self.hass.states.get(entity_id)
        if state is None or state.state == "unavailable":
            return
        domain = entity_id.split(".", 1)[0]
        attrs = state.attributes
        if domain in ("climate", "water_heater"):
            step = attrs.get("target_temp_step") or 0.5
            low, high = attrs.get("min_temp"), attrs.get("max_temp")
            current = attrs.get("temperature")
        else:
            step = attrs.get("step") or 0.5
            low, high = attrs.get("min"), attrs.get("max")
            current = state.state
        value = round_step(value, float(step))
        if low is not None:
            value = max(float(low), value)
        if high is not None:
            value = min(float(high), value)
        try:
            if current is not None and abs(float(current) - value) < 0.01:
                return
        except (TypeError, ValueError):
            pass
        if domain in ("climate", "water_heater"):
            await self._call(
                domain, "set_temperature", {"entity_id": entity_id, "temperature": value}
            )
        else:
            await self._call(
                domain, "set_value", {"entity_id": entity_id, "value": value}
            )

    # ----------------------------------------------------------------- prices
    async def _fetch_nordpool(self, day: Any) -> list[PriceSlot]:
        """Download one delivery day from the Nord Pool data portal."""
        area = self.conf.get(CONF_AREA) or DEFAULT_AREA
        vat = float(self.conf.get(CONF_VAT, DEFAULT_VAT) or 0)
        url = NORDPOOL_URL.format(date=day.isoformat(), area=area)
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    return []
                payload = await resp.json()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("SmartHP: Nord Pool download failed: %s", err)
            return []
        slots: list[PriceSlot] = []
        for item in (payload or {}).get("multiAreaEntries") or []:
            value = (item.get("entryPerArea") or {}).get(area)
            start = dt_util.parse_datetime(str(item.get("deliveryStart")))
            end = dt_util.parse_datetime(str(item.get("deliveryEnd")))
            if value is None or start is None or end is None:
                continue
            # EUR/MWh without VAT -> EUR/kWh with VAT
            slots.append(PriceSlot(start, end, round(float(value) / 1000 * (1 + vat / 100), 5)))
        return slots

    async def _builtin_slots(self, now: datetime) -> list[PriceSlot]:
        """Built-in Nord Pool prices: yesterday, today and tomorrow (CET days)."""
        cet_now = now.astimezone(dt_util.get_time_zone(NORDPOOL_TIMEZONE))
        today = cet_now.date()
        wanted = [today - timedelta(days=1), today, today + timedelta(days=1)]
        for day in list(self._np_cache):
            if day not in wanted:
                del self._np_cache[day]
        for day in wanted:
            if day in self._np_cache:
                continue
            if day > today and cet_now.hour < 13:
                continue  # tomorrow is published around 13:00 CET
            retry = self._np_retry.get(day)
            if retry and now < retry:
                continue
            self._np_retry[day] = now + PRICE_FETCH_RETRY
            slots = await self._fetch_nordpool(day)
            if slots:
                self._np_cache[day] = slots
        return sorted(
            (s for day in self._np_cache.values() for s in day), key=lambda s: s.start
        )

    async def _price_slots(self, now: datetime) -> list[PriceSlot]:
        if self.builtin_prices:
            return await self._builtin_slots(now)
        entity_id = self.conf.get(CONF_PRICE)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None:
            return []
        slots = slots_from_attributes(dict(state.attributes), now)
        if slots:
            return slots

        # Official Nord Pool integration: prices come from an action.
        if self._fetched_date == now.date() and self._fetched_slots:
            return self._fetched_slots
        if self._fetch_after and now < self._fetch_after:
            return []
        if not self.hass.services.has_service("nordpool", "get_prices_for_date"):
            return []
        reg_entry = er.async_get(self.hass).async_get(entity_id)
        if reg_entry is None or reg_entry.platform != "nordpool":
            return []
        self._fetch_after = now + PRICE_FETCH_RETRY
        try:
            response = await self.hass.services.async_call(
                "nordpool",
                "get_prices_for_date",
                {"config_entry": reg_entry.config_entry_id, "date": now.date().isoformat()},
                blocking=True,
                return_response=True,
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("SmartHP: Nord Pool price request failed: %s", err)
            return []
        if not isinstance(response, dict) or not response:
            return []
        uid = (reg_entry.unique_id or "").lower()
        area = next((a for a in response if a.lower() in uid), next(iter(response)))
        slots = slots_from_list(response.get(area))
        if slots:
            self._fetched_slots = slots
            self._fetched_date = now.date()
        return slots

    # ------------------------------------------------------------- calculation
    async def _async_update_data(self) -> dict[str, Any]:
        now = dt_util.now()
        slots = await self._price_slots(now)
        if self.builtin_prices:
            price = next((s.price for s in slots if s.start <= now < s.end), None)
        else:
            price = self._float(CONF_PRICE)
        data = self._compute(now, slots, price)
        today = [
            s.price for s in slots
            if s.start.astimezone(now.tzinfo).date() == now.date()
        ]
        data["current_price"] = price
        data["price_stats"] = (
            {
                "today_min": min(today),
                "today_max": max(today),
                "today_average": round(sum(today) / len(today), 5),
                "periods_today": len(today),
            }
            if today
            else {}
        )
        await self._apply(data)
        return data

    def _compute(
        self, now: datetime, slots: list[PriceSlot], price: float | None
    ) -> dict[str, Any]:
        s = self.settings
        enabled = bool(s["enabled"])
        outdoor = self._float(CONF_OUTDOOR)

        # --- damped outdoor temperature
        if outdoor is not None:
            tau = float(s["outdoor_filter"]) * 3600
            if self._filtered is None or tau <= 0 or self._last_calc is None:
                self._filtered = outdoor
            else:
                dt = max(0.0, (now - self._last_calc).total_seconds())
                self._filtered += (1 - math.exp(-dt / tau)) * (outdoor - self._filtered)
            self._last_calc = now
        filtered = self._filtered

        # --- price level
        if price is not None:
            self._price_samples.append((now, price))
        limit = now - timedelta(hours=24)
        while self._price_samples and self._price_samples[0][0] < limit:
            self._price_samples.popleft()
        rank = price_rank(slots, now)
        if rank is None and price is not None and self._price_samples:
            span = now - self._price_samples[0][0]
            if span >= timedelta(hours=6):
                rank = rank_in_samples((p for _, p in self._price_samples), price)
        use_abs = bool(s["abs_thresholds"])
        level = classify(
            rank,
            price,
            s["cheap_percent"],
            s["expensive_percent"],
            use_abs,
            s["price_always_cheap"],
            s["price_always_expensive"],
        )

        # --- summer mode
        if s["summer_mode"] and filtered is not None:
            if filtered >= s["summer_temp"]:
                self._summer = True
            elif filtered < s["summer_temp"] - SUMMER_HYSTERESIS:
                self._summer = False
        else:
            self._summer = False
        summer = self._summer

        # --- PV surplus
        pv_power = self._float(CONF_PV)
        if F_PV in self.features and s["pv_boost"] and pv_power is not None:
            if pv_power >= s["pv_threshold"]:
                self._pv_active = True
            elif pv_power < s["pv_threshold"] * 0.8:
                self._pv_active = False
        else:
            self._pv_active = False
        pv_active = self._pv_active

        vacation = bool(s["vacation"])

        # --- legionella cycle
        legionella = False
        dhw_temp = self._float(CONF_DHW_TEMP)
        if F_DHW in self.features and s["legionella"]:
            start_time = parse_time(s["legionella_time"])
            for day in (now.date(), now.date() - timedelta(days=1)):
                if WEEKDAYS[day.weekday()] != s["legionella_day"]:
                    continue
                start = now.replace(
                    year=day.year, month=day.month, day=day.day,
                    hour=start_time.hour, minute=start_time.minute,
                    second=0, microsecond=0,
                )
                if start <= now < start + timedelta(minutes=LEGIONELLA_MAX_MINUTES):
                    if dhw_temp is not None and dhw_temp >= s["legionella_temp"]:
                        self._legionella_done = start
                    legionella = self._legionella_done != start

        # --- flow temperature
        offsets: dict[str, float] = {}
        curve = target = total_offset = None
        if filtered is not None:
            curve = interpolate(((x, float(s[key])) for x, key in CURVE_POINTS), filtered)
            if s["price_control"]:
                if level == LEVEL_CHEAP:
                    offsets["price"] = float(s["cheap_offset"])
                elif level == LEVEL_EXPENSIVE:
                    offsets["price"] = -float(s["expensive_offset"])
            room = self._float(CONF_ROOM)
            if F_ROOM in self.features and s["room_compensation"] and room is not None:
                offsets["room"] = clamp((s["room_target"] - room) * s["room_factor"], -10, 10)
            if s["night_setback"] and window_elapsed(
                now, parse_time(s["night_start"]), parse_time(s["night_end"])
            ) is not None:
                offsets["night"] = -float(s["night_setback_temp"])
            if vacation:
                offsets["vacation"] = -float(s["vacation_setback_temp"])
            if pv_active:
                offsets["pv"] = float(s["pv_offset"])
            wanted = curve + float(s["curve_shift"]) + sum(offsets.values())
            target = clamp(wanted, s["flow_min"], s["flow_max"])
            if summer:
                target = float(s["flow_min"])
            total_offset = target - curve

        # --- auxiliary heater
        aux_demand = aux_price = False
        if F_AUX in self.features and not summer:
            if s["aux_by_temp"] and outdoor is not None:
                if outdoor < s["aux_outdoor_temp"]:
                    self._aux_temp_on = True
                elif outdoor >= s["aux_outdoor_temp"] + s["aux_hysteresis"]:
                    self._aux_temp_on = False
            else:
                self._aux_temp_on = False
            aux_price = bool(
                s["aux_by_price"] and price is not None and price > s["aux_price_limit"]
            )
            aux_demand = self._aux_temp_on or aux_price
        else:
            self._aux_temp_on = False
        if F_AUX in self.features:
            if aux_demand:
                if self._aux_on_since is None:
                    self._aux_on_since = now
            elif self._aux_on_since is not None:
                if now - self._aux_on_since < timedelta(minutes=float(s["aux_min_run"])):
                    aux_demand = True  # minimum run time
                else:
                    self._aux_on_since = None

        # --- heat pump blocking
        blocked = False
        if F_BLOCK in self.features:
            if F_AUX in self.features and s["aux_blocks_hp"] and aux_price:
                blocked = True
                self._block_since = None
            else:
                want = bool(
                    s["hp_block"]
                    and level == LEVEL_EXPENSIVE
                    and not legionella
                    and (outdoor is None or outdoor >= s["block_min_outdoor"])
                )
                if self._pause_until and now >= self._pause_until:
                    self._pause_until = None
                if want and self._pause_until is None:
                    if self._block_since is None:
                        self._block_since = now
                    if now - self._block_since >= timedelta(
                        minutes=float(s["block_max_minutes"])
                    ):
                        self._block_since = None
                        self._pause_until = now + timedelta(
                            minutes=float(s["block_pause_minutes"])
                        )
                    else:
                        blocked = True
                else:
                    self._block_since = None

        # --- SG Ready state
        sg_state = None
        if F_SG in self.features:
            very_cheap = use_abs and price is not None and price <= s["price_always_cheap"]
            if blocked:
                sg_state = 1
            elif pv_active or very_cheap:
                sg_state = 4
            elif level == LEVEL_CHEAP:
                sg_state = 3
            else:
                sg_state = 2

        # --- domestic hot water
        dhw_target = None
        if F_DHW in self.features and (s["dhw_price"] or s["legionella"]):
            if legionella:
                dhw_target = float(s["legionella_temp"])
            elif vacation:
                dhw_target = float(s["dhw_expensive"])
            elif s["dhw_price"] and (pv_active or level == LEVEL_CHEAP):
                dhw_target = float(s["dhw_cheap"])
            elif s["dhw_price"] and level == LEVEL_EXPENSIVE:
                dhw_target = float(s["dhw_expensive"])
            else:
                dhw_target = float(s["dhw_normal"])

        # --- circulation pump
        circ_demand = False
        if F_CIRC in self.features:
            if s["circulation"] and not vacation:
                for idx in (1, 2, 3):
                    elapsed = window_elapsed(
                        now,
                        parse_time(s[f"circ{idx}_start"]),
                        parse_time(s[f"circ{idx}_end"]),
                    )
                    if elapsed is None:
                        continue
                    on, off = float(s["circ_on_minutes"]), float(s["circ_off_minutes"])
                    if off <= 0 or elapsed % (on + off) < on:
                        circ_demand = True
                        break
                if circ_demand and F_DHW_TEMP in self.features and s["circ_use_temp"]:
                    if dhw_temp is not None:
                        if dhw_temp >= s["circ_min_temp"]:
                            self._circ_temp_ok = True
                        elif dhw_temp < s["circ_min_temp"] - CIRC_TEMP_HYSTERESIS:
                            self._circ_temp_ok = False
                    circ_demand = self._circ_temp_ok
            if circ_demand:
                self._circ_last_run = now
            elif s["circ_antiseize"]:
                if self._antiseize_until and now < self._antiseize_until:
                    circ_demand = True
                elif self._antiseize_until:
                    self._antiseize_until = None
                    self._circ_last_run = now
                elif self._circ_last_run and now - self._circ_last_run >= timedelta(
                    hours=ANTISEIZE_INTERVAL_HOURS
                ):
                    self._antiseize_until = now + timedelta(seconds=ANTISEIZE_RUN_SECONDS)
                    circ_demand = True

        # --- status
        if not enabled:
            status = "disabled"
        elif filtered is None:
            status = "no_data"
        elif blocked:
            status = "blocked"
        elif legionella:
            status = "legionella"
        elif summer:
            status = "summer"
        elif vacation:
            status = "vacation"
        elif pv_active:
            status = "pv_boost"
        elif "price" in offsets and offsets["price"] > 0:
            status = "boost"
        elif "price" in offsets and offsets["price"] < 0:
            status = "saving"
        else:
            status = "normal"

        return {
            "enabled": enabled,
            "status": status,
            "outdoor": outdoor,
            "outdoor_filtered": None if filtered is None else round(filtered, 2),
            "price": price,
            "price_level": level,
            "price_rank": None if rank is None else round(rank * 100, 1),
            "curve_flow": None if curve is None else round(curve, 1),
            "target_flow": None if target is None else round(target, 1),
            "total_offset": None if total_offset is None else round(total_offset, 1),
            "offsets": {k: round(v, 1) for k, v in offsets.items()},
            "summer_active": summer,
            "pv_active": pv_active,
            "hp_blocked": blocked,
            "sg_state": sg_state,
            "dhw_target": dhw_target,
            "legionella_active": legionella,
            "circ_demand": circ_demand,
            "aux_demand": aux_demand,
        }

    # ------------------------------------------------------------------ output
    async def _write_block(self, blocked: bool, sg_state: int | None) -> None:
        block_switch = self.conf.get(CONF_BLOCK)
        if block_switch:
            inverted = bool(self.conf.get(CONF_BLOCK_INVERTED))
            # normal: switch ON = heat pump allowed; inverted: switch ON = blocked
            await self._set_switch(block_switch, blocked if inverted else not blocked)
        if sg_state is not None:
            await self._set_switch(self.conf.get(CONF_SG1), sg_state in (1, 4))
            await self._set_switch(self.conf.get(CONF_SG2), sg_state in (3, 4))

    async def async_release(self) -> None:
        """Remove any block so the heat pump is never left locked out."""
        await self._write_block(False, 2 if F_SG in self.features else None)

    async def _apply(self, data: dict[str, Any]) -> None:
        if not data["enabled"]:
            if self._was_enabled:
                self._was_enabled = False
                await self.async_release()
            return
        self._was_enabled = True

        if data["target_flow"] is not None:
            if self.conf.get(CONF_SETPOINT_MODE) == MODE_OFFSET:
                value = data["total_offset"]
            else:
                value = data["target_flow"]
            await self._set_value(self.conf.get(CONF_SETPOINT), value)

        await self._write_block(data["hp_blocked"], data["sg_state"])
        await self._set_value(self.conf.get(CONF_DHW_SETPOINT), data["dhw_target"])
        if F_CIRC in self.features:
            await self._set_switch(self.conf.get(CONF_CIRC), data["circ_demand"])
        if F_AUX in self.features:
            await self._set_switch(self.conf.get(CONF_AUX), data["aux_demand"])
