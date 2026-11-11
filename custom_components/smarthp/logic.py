"""Pure calculation helpers for SmartHP (no Home Assistant state access)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any, Iterable

from homeassistant.util import dt as dt_util

from .const import LEVEL_CHEAP, LEVEL_EXPENSIVE, LEVEL_NORMAL, LEVEL_UNKNOWN

_START_KEYS = ("start", "time", "start_time", "startsAt", "from", "datetime")
_END_KEYS = ("end", "end_time", "till", "to")
_VALUE_KEYS = ("value", "price", "total", "price_per_kwh", "value_exc_vat")
_TODAY_ATTRS = ("raw_today", "prices_today", "today", "prices", "data")
_TOMORROW_ATTRS = ("raw_tomorrow", "prices_tomorrow", "tomorrow")


@dataclass(frozen=True)
class PriceSlot:
    """One price period."""

    start: datetime
    end: datetime
    price: float


def interpolate(points: Iterable[tuple[float, float]], x: float) -> float:
    """Piecewise-linear interpolation, clamped outside the outermost points."""
    pts = sorted(points)
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value; if the limits are crossed the lower one wins."""
    if high < low:
        high = low
    return max(low, min(high, value))


def parse_time(value: Any) -> time:
    """Parse 'HH:MM[:SS]' (or a time object) into a time."""
    if isinstance(value, time):
        return value
    parsed = dt_util.parse_time(str(value))
    return parsed or time(0, 0)


def window_elapsed(now: datetime, start: time, end: time) -> float | None:
    """Minutes since the window started if `now` is inside it, else None.

    Windows may cross midnight. A window with start == end is disabled.
    """
    if start == end:
        return None
    t = now.time()
    today_start = now.replace(
        hour=start.hour, minute=start.minute, second=start.second, microsecond=0
    )
    if start < end:
        if start <= t < end:
            return (now - today_start).total_seconds() / 60
        return None
    if t >= start:
        return (now - today_start).total_seconds() / 60
    if t < end:
        return (now - (today_start - timedelta(days=1))).total_seconds() / 60
    return None


def _to_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        result = dt_util.parse_datetime(value)
    else:
        return None
    if result is None:
        return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
    return result


def _to_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:  # NaN
        return None
    return result


def slots_from_list(items: Any, day_start: datetime | None = None) -> list[PriceSlot]:
    """Build price slots from a list of dicts or a plain list of numbers."""
    if not isinstance(items, (list, tuple)) or not items:
        return []
    slots: list[PriceSlot] = []

    if isinstance(items[0], dict):
        raw: list[tuple[datetime, datetime | None, float]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            start = next(
                (d for k in _START_KEYS if (d := _to_datetime(item.get(k)))), None
            )
            price = next(
                (p for k in _VALUE_KEYS if (p := _to_float(item.get(k))) is not None),
                None,
            )
            if start is None or price is None:
                continue
            end = next((d for k in _END_KEYS if (d := _to_datetime(item.get(k)))), None)
            raw.append((start, end, price))
        raw.sort(key=lambda r: r[0])
        for idx, (start, end, price) in enumerate(raw):
            if end is None or end <= start:
                if idx + 1 < len(raw):
                    end = raw[idx + 1][0]
                elif idx > 0:
                    end = start + (start - raw[idx - 1][0])
                else:
                    end = start + timedelta(hours=1)
            slots.append(PriceSlot(start, end, price))
        return slots

    if day_start is None:
        return []
    values = [_to_float(v) for v in items]
    if any(v is None for v in values):
        return []
    step = timedelta(hours=24) / len(values)
    for idx, price in enumerate(values):
        slots.append(PriceSlot(day_start + idx * step, day_start + (idx + 1) * step, price))
    return slots


def slots_from_attributes(attrs: dict[str, Any], now: datetime) -> list[PriceSlot]:
    """Extract price slots from the attributes of a price sensor.

    Supports the HACS Nord Pool sensor (raw_today / today), ENTSO-e
    (prices_today / prices) and similar layouts.
    """
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    slots: list[PriceSlot] = []
    for name in _TODAY_ATTRS:
        slots = slots_from_list(attrs.get(name), midnight)
        if slots:
            break
    if not slots:
        return []
    for name in _TOMORROW_ATTRS:
        extra = slots_from_list(attrs.get(name), midnight + timedelta(days=1))
        if extra:
            known = {s.start for s in slots}
            slots.extend(s for s in extra if s.start not in known)
            break
    return sorted(slots, key=lambda s: s.start)


def price_rank(slots: list[PriceSlot], now: datetime) -> float | None:
    """Share (0..1) of today's periods that are cheaper than the current one."""
    today = [
        s for s in slots if s.start.astimezone(now.tzinfo).date() == now.date()
    ]
    if len(today) < 4:
        return None
    current = next((s for s in today if s.start <= now < s.end), None)
    if current is None:
        return None
    prices = [s.price for s in today]
    if max(prices) == min(prices):
        return 0.5
    return sum(1 for p in prices if p < current.price) / len(prices)


def rank_in_samples(samples: Iterable[float], price: float) -> float | None:
    """Fallback rank of `price` among recently recorded prices."""
    values = list(samples)
    if len(values) < 6 or max(values) == min(values):
        return None
    return sum(1 for p in values if p < price) / len(values)


def classify(
    rank: float | None,
    price: float | None,
    cheap_percent: float,
    expensive_percent: float,
    use_abs: bool,
    always_cheap: float,
    always_expensive: float,
) -> str:
    """Return the price level for the current period."""
    if use_abs and price is not None:
        if price <= always_cheap:
            return LEVEL_CHEAP
        if price >= always_expensive:
            return LEVEL_EXPENSIVE
    if rank is None:
        return LEVEL_UNKNOWN if price is None or not use_abs else LEVEL_NORMAL
    if rank < cheap_percent / 100:
        return LEVEL_CHEAP
    if rank >= 1 - expensive_percent / 100:
        return LEVEL_EXPENSIVE
    return LEVEL_NORMAL


def round_step(value: float, step: float) -> float:
    """Round to the nearest multiple of step."""
    if not step or step <= 0:
        return round(value, 2)
    return round(round(value / step) * step, 4)
