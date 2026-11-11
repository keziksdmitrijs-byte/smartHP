"""Unit tests for the pure calculation helpers."""

from datetime import datetime, time, timedelta, timezone

from custom_components.smarthp.logic import (
    classify,
    interpolate,
    price_rank,
    slots_from_attributes,
    slots_from_list,
    window_elapsed,
)

TZ = timezone(timedelta(hours=2))
CURVE = [(-20, 45), (-10, 40), (0, 35), (10, 30), (20, 25)]


def test_interpolate():
    assert interpolate(CURVE, -5) == 37.5
    assert interpolate(CURVE, -30) == 45
    assert interpolate(CURVE, 25) == 25
    assert interpolate(CURVE, 0) == 35


def test_window_elapsed():
    now = datetime(2026, 1, 5, 7, 30, tzinfo=TZ)
    assert window_elapsed(now, time(6), time(8)) == 90
    assert window_elapsed(now, time(8), time(9)) is None
    assert window_elapsed(now, time(0), time(0)) is None
    # overnight window 22:00-06:00
    assert window_elapsed(now.replace(hour=23, minute=0), time(22), time(6)) == 60
    assert window_elapsed(now.replace(hour=2, minute=0), time(22), time(6)) == 240
    assert window_elapsed(now.replace(hour=12), time(22), time(6)) is None


def _raw(day: datetime, prices, minutes=60):
    return [
        {
            "start": day + timedelta(minutes=minutes * i),
            "end": day + timedelta(minutes=minutes * (i + 1)),
            "value": p,
        }
        for i, p in enumerate(prices)
    ]


def test_rank_hourly_and_quarter_hourly():
    day = datetime(2026, 1, 5, tzinfo=TZ)
    slots = slots_from_attributes({"raw_today": _raw(day, list(range(24)))}, day)
    assert len(slots) == 24
    assert price_rank(slots, day.replace(hour=0, minute=30)) == 0
    assert price_rank(slots, day.replace(hour=18)) == 0.75
    quarter = slots_from_attributes({"raw_today": _raw(day, list(range(96)), 15)}, day)
    assert len(quarter) == 96
    assert price_rank(quarter, day.replace(hour=12, minute=20)) == 49 / 96


def test_plain_list_and_iso_strings():
    day = datetime(2026, 1, 5, tzinfo=TZ)
    slots = slots_from_attributes({"today": [5, 1, 9, 3] * 6}, day.replace(hour=1, minute=5))
    assert len(slots) == 24 and slots[1].price == 1
    assert price_rank(slots, day.replace(hour=1, minute=5)) == 0
    official = [
        {"start": "2026-01-05T00:00:00+02:00", "end": "2026-01-05T01:00:00+02:00", "price": 50.0},
        {"start": "2026-01-05T01:00:00+02:00", "end": "2026-01-05T02:00:00+02:00", "price": 70.0},
    ]
    parsed = slots_from_list(official)
    assert [s.price for s in parsed] == [50.0, 70.0]
    assert parsed[0].end == parsed[1].start


def test_flat_prices_are_normal():
    day = datetime(2026, 1, 5, tzinfo=TZ)
    slots = slots_from_attributes({"today": [0.1] * 24}, day)
    rank = price_rank(slots, day.replace(hour=5))
    assert classify(rank, 0.1, 30, 25, False, 0, 0) == "normal"


def test_classify():
    assert classify(0.1, 0.2, 30, 25, False, 0, 0) == "cheap"
    assert classify(0.5, 0.2, 30, 25, False, 0, 0) == "normal"
    assert classify(0.75, 0.2, 30, 25, False, 0, 0) == "expensive"
    assert classify(None, 0.2, 30, 25, False, 0, 0) == "unknown"
    # absolute thresholds win over the rank
    assert classify(0.9, 0.01, 30, 25, True, 0.05, 0.3) == "cheap"
    assert classify(0.1, 0.5, 30, 25, True, 0.05, 0.3) == "expensive"
    assert classify(None, 0.1, 30, 25, True, 0.05, 0.3) == "normal"
