"""Constants and entity descriptors for SmartHP."""

from __future__ import annotations

from dataclasses import dataclass

DOMAIN = "smarthp"
VERSION = "0.3.0"
PLATFORMS = ["binary_sensor", "number", "select", "sensor", "switch", "time"]

FRONTEND_URL = "/smarthp_static/smarthp-card.js"
PANEL_URL_PATH = "smarthp"

# --- config entry keys -------------------------------------------------------
CONF_OUTDOOR = "outdoor_sensor"
CONF_PRICE = "price_sensor"
CONF_AREA = "nordpool_area"
CONF_VAT = "vat_percent"
CONF_SETPOINT = "setpoint_entity"
CONF_SETPOINT_MODE = "setpoint_mode"
CONF_BLOCK = "block_switch"
CONF_BLOCK_INVERTED = "block_inverted"
CONF_ROOM = "room_sensor"
CONF_PV = "pv_sensor"
CONF_SG1 = "sg_ready_1"
CONF_SG2 = "sg_ready_2"
CONF_DHW_TEMP = "dhw_sensor"
CONF_DHW_SETPOINT = "dhw_setpoint_entity"
CONF_CIRC = "circulation_pump"
CONF_AUX = "aux_heater"

NORDPOOL_URL = (
    "https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices"
    "?date={date}&market=DayAhead&deliveryArea={area}&currency=EUR"
)
NORDPOOL_TIMEZONE = "Europe/Stockholm"
NORDPOOL_AREAS = [
    "LV", "LT", "EE", "FI", "SE1", "SE2", "SE3", "SE4",
    "NO1", "NO2", "NO3", "NO4", "NO5", "DK1", "DK2",
    "PL", "GER", "AT", "NL", "BE", "FR",
]
DEFAULT_AREA = "LV"
DEFAULT_VAT = 21.0

MODE_FLOW = "flow"
MODE_OFFSET = "offset"

# --- feature groups (which optional entities were configured) ----------------
F_BLOCK = "block"
F_SG = "sg"
F_ROOM = "room"
F_PV = "pv"
F_DHW = "dhw"
F_DHW_TEMP = "dhw_temp"
F_CIRC = "circ"
F_AUX = "aux"

LEVEL_CHEAP = "cheap"
LEVEL_NORMAL = "normal"
LEVEL_EXPENSIVE = "expensive"
LEVEL_UNKNOWN = "unknown"
LEVELS = [LEVEL_CHEAP, LEVEL_NORMAL, LEVEL_EXPENSIVE, LEVEL_UNKNOWN]

STATUSES = [
    "disabled",
    "no_data",
    "blocked",
    "legionella",
    "summer",
    "vacation",
    "pv_boost",
    "boost",
    "saving",
    "normal",
]

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

CURVE_POINTS = [
    (-20.0, "curve_m20"),
    (-10.0, "curve_m10"),
    (0.0, "curve_0"),
    (10.0, "curve_p10"),
    (20.0, "curve_p20"),
]

LEGIONELLA_MAX_MINUTES = 180
SUMMER_HYSTERESIS = 1.0
CIRC_TEMP_HYSTERESIS = 3.0
ANTISEIZE_INTERVAL_HOURS = 24
ANTISEIZE_RUN_SECONDS = 60


@dataclass(frozen=True)
class NumberDesc:
    key: str
    default: float
    min: float
    max: float
    step: float
    unit: str | None = None
    requires: tuple[str, ...] = ()
    icon: str | None = None


@dataclass(frozen=True)
class SwitchDesc:
    key: str
    default: bool
    requires: tuple[str, ...] = ()
    icon: str | None = None
    config: bool = True


@dataclass(frozen=True)
class TimeDesc:
    key: str
    default: str
    requires: tuple[str, ...] = ()


@dataclass(frozen=True)
class SelectDesc:
    key: str
    default: str
    options: tuple[str, ...]
    requires: tuple[str, ...] = ()


C = "°C"
PRICE_MIN, PRICE_MAX, PRICE_STEP = -500.0, 5000.0, 0.001

NUMBERS: tuple[NumberDesc, ...] = (
    # heating curve
    NumberDesc("curve_m20", 45, 15, 80, 0.5, C, icon="mdi:chart-bell-curve-cumulative"),
    NumberDesc("curve_m10", 40, 15, 80, 0.5, C, icon="mdi:chart-bell-curve-cumulative"),
    NumberDesc("curve_0", 35, 15, 80, 0.5, C, icon="mdi:chart-bell-curve-cumulative"),
    NumberDesc("curve_p10", 30, 15, 80, 0.5, C, icon="mdi:chart-bell-curve-cumulative"),
    NumberDesc("curve_p20", 25, 15, 80, 0.5, C, icon="mdi:chart-bell-curve-cumulative"),
    NumberDesc("curve_shift", 0, -10, 10, 0.5, C, icon="mdi:arrow-up-down"),
    NumberDesc("flow_min", 20, 10, 50, 0.5, C, icon="mdi:thermometer-low"),
    NumberDesc("flow_max", 55, 25, 80, 0.5, C, icon="mdi:thermometer-high"),
    NumberDesc("outdoor_filter", 0, 0, 48, 1, "h", icon="mdi:timer-sand"),
    # price
    NumberDesc("cheap_percent", 30, 0, 100, 5, "%", icon="mdi:percent"),
    NumberDesc("expensive_percent", 25, 0, 100, 5, "%", icon="mdi:percent"),
    NumberDesc("cheap_offset", 3, 0, 15, 0.5, C, icon="mdi:thermometer-plus"),
    NumberDesc("expensive_offset", 3, 0, 15, 0.5, C, icon="mdi:thermometer-minus"),
    NumberDesc("price_always_cheap", 0.05, PRICE_MIN, PRICE_MAX, PRICE_STEP, icon="mdi:cash-minus"),
    NumberDesc("price_always_expensive", 0.30, PRICE_MIN, PRICE_MAX, PRICE_STEP, icon="mdi:cash-plus"),
    # summer / room / night / vacation / pv
    NumberDesc("summer_temp", 16, 5, 30, 0.5, C, icon="mdi:white-balance-sunny"),
    NumberDesc("room_target", 21, 10, 30, 0.5, C, (F_ROOM,), "mdi:home-thermometer"),
    NumberDesc("room_factor", 2, 0, 10, 0.5, None, (F_ROOM,), "mdi:multiplication"),
    NumberDesc("night_setback_temp", 2, 0, 15, 0.5, C, icon="mdi:weather-night"),
    NumberDesc("vacation_setback_temp", 5, 0, 20, 0.5, C, icon="mdi:bag-suitcase"),
    NumberDesc("pv_threshold", 1500, 0, 20000, 100, "W", (F_PV,), "mdi:solar-power"),
    NumberDesc("pv_offset", 3, 0, 15, 0.5, C, (F_PV,), "mdi:thermometer-plus"),
    # domestic hot water
    NumberDesc("dhw_normal", 48, 30, 65, 0.5, C, (F_DHW,), "mdi:water-thermometer"),
    NumberDesc("dhw_cheap", 55, 30, 70, 0.5, C, (F_DHW,), "mdi:water-thermometer"),
    NumberDesc("dhw_expensive", 42, 20, 65, 0.5, C, (F_DHW,), "mdi:water-thermometer"),
    NumberDesc("legionella_temp", 62, 55, 75, 0.5, C, (F_DHW,), "mdi:bacteria"),
    # circulation pump
    NumberDesc("circ_min_temp", 40, 20, 70, 0.5, C, (F_CIRC, F_DHW_TEMP), "mdi:thermometer-water"),
    NumberDesc("circ_on_minutes", 5, 1, 60, 1, "min", (F_CIRC,), "mdi:timer"),
    NumberDesc("circ_off_minutes", 15, 0, 120, 1, "min", (F_CIRC,), "mdi:timer-off"),
    # auxiliary heater
    NumberDesc("aux_outdoor_temp", -15, -40, 20, 0.5, C, (F_AUX,), "mdi:thermometer-chevron-down"),
    NumberDesc("aux_hysteresis", 1, 0.5, 5, 0.5, C, (F_AUX,), "mdi:arrow-expand-vertical"),
    NumberDesc("aux_price_limit", 0.30, PRICE_MIN, PRICE_MAX, PRICE_STEP, None, (F_AUX,), "mdi:cash-alert"),
    NumberDesc("aux_min_run", 15, 0, 240, 5, "min", (F_AUX,), "mdi:timer"),
)

SWITCHES: tuple[SwitchDesc, ...] = (
    SwitchDesc("enabled", True, icon="mdi:power", config=False),
    SwitchDesc("price_control", True, icon="mdi:cash-clock"),
    SwitchDesc("abs_thresholds", False, icon="mdi:cash-lock"),
    SwitchDesc("summer_mode", True, icon="mdi:white-balance-sunny"),
    SwitchDesc("room_compensation", False, (F_ROOM,), "mdi:home-thermometer"),
    SwitchDesc("night_setback", False, icon="mdi:weather-night"),
    SwitchDesc("vacation", False, icon="mdi:bag-suitcase", config=False),
    SwitchDesc("pv_boost", False, (F_PV,), "mdi:solar-power"),
    SwitchDesc("dhw_price", False, (F_DHW,), "mdi:water-boiler"),
    SwitchDesc("legionella", False, (F_DHW,), "mdi:bacteria"),
    SwitchDesc("circulation", True, (F_CIRC,), "mdi:pump"),
    SwitchDesc("circ_use_temp", False, (F_CIRC, F_DHW_TEMP), "mdi:thermometer-water"),
    SwitchDesc("circ_antiseize", True, (F_CIRC,), "mdi:pump-off"),
    SwitchDesc("aux_by_temp", True, (F_AUX,), "mdi:thermometer-chevron-down"),
    SwitchDesc("aux_by_price", False, (F_AUX,), "mdi:cash-alert"),
    SwitchDesc("aux_blocks_hp", False, (F_AUX, F_BLOCK), "mdi:swap-horizontal"),
)

TIMES: tuple[TimeDesc, ...] = (
    TimeDesc("night_start", "22:00:00"),
    TimeDesc("night_end", "06:00:00"),
    TimeDesc("legionella_time", "03:00:00", (F_DHW,)),
    TimeDesc("circ1_start", "06:00:00", (F_CIRC,)),
    TimeDesc("circ1_end", "08:00:00", (F_CIRC,)),
    TimeDesc("circ2_start", "17:00:00", (F_CIRC,)),
    TimeDesc("circ2_end", "22:00:00", (F_CIRC,)),
    TimeDesc("circ3_start", "00:00:00", (F_CIRC,)),
    TimeDesc("circ3_end", "00:00:00", (F_CIRC,)),
)

SELECTS: tuple[SelectDesc, ...] = (
    SelectDesc("legionella_day", "sun", tuple(WEEKDAYS), (F_DHW,)),
)


def default_settings() -> dict:
    """Return the default value of every setting."""
    out: dict = {}
    for group in (NUMBERS, SWITCHES, TIMES, SELECTS):
        for desc in group:
            out[desc.key] = desc.default
    return out
