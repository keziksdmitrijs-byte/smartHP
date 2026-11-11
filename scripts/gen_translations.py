"""Generate strings.json and translations/*.json from one table.

Run:  python3 scripts/gen_translations.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "smarthp"
LANGS = ("en", "ru", "lv")

# key: (en, ru, lv)
NUMBER = {
    "curve_m20": ("Flow temperature at −20 °C outdoor", "Подача при −20 °C на улице", "Turpgaita pie −20 °C ārā"),
    "curve_m10": ("Flow temperature at −10 °C outdoor", "Подача при −10 °C на улице", "Turpgaita pie −10 °C ārā"),
    "curve_0": ("Flow temperature at 0 °C outdoor", "Подача при 0 °C на улице", "Turpgaita pie 0 °C ārā"),
    "curve_p10": ("Flow temperature at +10 °C outdoor", "Подача при +10 °C на улице", "Turpgaita pie +10 °C ārā"),
    "curve_p20": ("Flow temperature at +20 °C outdoor", "Подача при +20 °C на улице", "Turpgaita pie +20 °C ārā"),
    "curve_shift": ("Curve parallel shift", "Параллельный сдвиг кривой", "Līknes paralēlā nobīde"),
    "flow_min": ("Minimum flow temperature", "Мин. температура подачи", "Min. turpgaitas temperatūra"),
    "flow_max": ("Maximum flow temperature", "Макс. температура подачи", "Maks. turpgaitas temperatūra"),
    "outdoor_filter": ("Outdoor temperature damping", "Усреднение наружной температуры", "Āra temperatūras vidējošana"),
    "cheap_percent": ("Cheap share of the day", "Доля дешёвых часов в сутках", "Lēto stundu daļa diennaktī"),
    "expensive_percent": ("Expensive share of the day", "Доля дорогих часов в сутках", "Dārgo stundu daļa diennaktī"),
    "cheap_offset": ("Flow boost in cheap hours", "Повышение подачи в дешёвые часы", "Turpgaitas paaugstinājums lētajās stundās"),
    "expensive_offset": ("Flow reduction in expensive hours", "Снижение подачи в дорогие часы", "Turpgaitas pazeminājums dārgajās stundās"),
    "price_always_cheap": ("Always cheap below price", "Всегда дёшево ниже цены", "Vienmēr lēti zem cenas"),
    "price_always_expensive": ("Always expensive above price", "Всегда дорого выше цены", "Vienmēr dārgi virs cenas"),
    "summer_temp": ("Summer mode above outdoor temperature", "Летний режим при наружной выше", "Vasaras režīms, ja ārā virs"),
    "room_target": ("Room target temperature", "Заданная температура в помещении", "Telpas uzdotā temperatūra"),
    "room_factor": ("Room influence factor", "Коэффициент влияния помещения", "Telpas ietekmes koeficients"),
    "night_setback_temp": ("Night flow reduction", "Ночное снижение подачи", "Nakts turpgaitas pazeminājums"),
    "vacation_setback_temp": ("Vacation flow reduction", "Снижение подачи в отпуске", "Turpgaitas pazeminājums atvaļinājumā"),
    "pv_threshold": ("PV surplus threshold", "Порог излишка солнечной энергии", "Saules enerģijas pārpalikuma slieksnis"),
    "pv_offset": ("Flow boost on PV surplus", "Повышение подачи при излишке PV", "Turpgaitas paaugstinājums pie PV pārpalikuma"),
    "dhw_normal": ("Hot water temperature, normal", "Температура ГВС, обычная", "Karstā ūdens temperatūra, parastā"),
    "dhw_cheap": ("Hot water temperature in cheap hours", "Температура ГВС в дешёвые часы", "Karstā ūdens temperatūra lētajās stundās"),
    "dhw_expensive": ("Hot water temperature in expensive hours", "Температура ГВС в дорогие часы", "Karstā ūdens temperatūra dārgajās stundās"),
    "legionella_temp": ("Legionella cycle temperature", "Температура антилегионеллы", "Antilegionellas temperatūra"),
    "circ_min_temp": ("Circulation minimum boiler temperature", "Мин. температура бойлера для циркуляции", "Min. boilera temperatūra cirkulācijai"),
    "circ_on_minutes": ("Circulation run time", "Циркуляция: работа", "Cirkulācija: darbība"),
    "circ_off_minutes": ("Circulation pause (0 = continuous)", "Циркуляция: пауза (0 = непрерывно)", "Cirkulācija: pauze (0 = nepārtraukti)"),
    "aux_outdoor_temp": ("Auxiliary heater below outdoor temperature", "Доп. котёл при наружной ниже", "Papildu katls, ja ārā zem"),
    "aux_hysteresis": ("Auxiliary heater hysteresis", "Гистерезис доп. котла", "Papildu katla histerēze"),
    "aux_price_limit": ("Auxiliary heater above electricity price", "Доп. котёл при цене выше", "Papildu katls, ja cena virs"),
    "aux_min_run": ("Auxiliary heater minimum run time", "Мин. время работы доп. котла", "Papildu katla min. darbības laiks"),
}

SWITCH = {
    "enabled": ("Control enabled", "Управление включено", "Vadība ieslēgta"),
    "price_control": ("Price-based flow adjustment", "Коррекция подачи по цене", "Turpgaitas korekcija pēc cenas"),
    "abs_thresholds": ("Absolute price thresholds", "Абсолютные пороги цены", "Absolūtie cenas sliekšņi"),
    "summer_mode": ("Automatic summer mode", "Автоматический летний режим", "Automātiskais vasaras režīms"),
    "room_compensation": ("Room temperature compensation", "Коррекция по температуре помещения", "Korekcija pēc telpas temperatūras"),
    "night_setback": ("Night setback", "Ночное снижение", "Nakts pazeminājums"),
    "vacation": ("Vacation mode", "Режим отпуска", "Atvaļinājuma režīms"),
    "pv_boost": ("PV surplus boost", "Использование излишка PV", "PV pārpalikuma izmantošana"),
    "dhw_price": ("Hot water by price", "ГВС по цене", "Karstais ūdens pēc cenas"),
    "legionella": ("Legionella protection", "Защита от легионеллы", "Aizsardzība pret legionellu"),
    "circulation": ("Circulation pump control", "Управление циркуляционным насосом", "Cirkulācijas sūkņa vadība"),
    "circ_use_temp": ("Circulation only with hot boiler", "Циркуляция только при горячем бойлере", "Cirkulācija tikai ar karstu boileri"),
    "circ_antiseize": ("Pump anti-seize run", "Защита насоса от закисания", "Sūkņa aizsardzība pret iestrēgšanu"),
    "aux_by_temp": ("Auxiliary heater by outdoor temperature", "Доп. котёл по наружной температуре", "Papildu katls pēc āra temperatūras"),
    "aux_by_price": ("Auxiliary heater by electricity price", "Доп. котёл по цене электричества", "Papildu katls pēc elektrības cenas"),
    "aux_blocks_hp": ("Stop heat pump while heater runs on price", "Останавливать насос, когда котёл работает по цене", "Apturēt siltumsūkni, kad katls strādā pēc cenas"),
}

TIME = {
    "night_start": ("Night setback start", "Ночное снижение: начало", "Nakts pazeminājums: sākums"),
    "night_end": ("Night setback end", "Ночное снижение: конец", "Nakts pazeminājums: beigas"),
    "legionella_time": ("Legionella cycle time", "Время антилегионеллы", "Antilegionellas laiks"),
}
for n in (1, 2, 3):
    TIME[f"circ{n}_start"] = (f"Circulation period {n} start", f"Циркуляция, период {n}: начало", f"Cirkulācija, periods {n}: sākums")
    TIME[f"circ{n}_end"] = (f"Circulation period {n} end", f"Циркуляция, период {n}: конец", f"Cirkulācija, periods {n}: beigas")

DAYS = {
    "mon": ("Monday", "Понедельник", "Pirmdiena"),
    "tue": ("Tuesday", "Вторник", "Otrdiena"),
    "wed": ("Wednesday", "Среда", "Trešdiena"),
    "thu": ("Thursday", "Четверг", "Ceturtdiena"),
    "fri": ("Friday", "Пятница", "Piektdiena"),
    "sat": ("Saturday", "Суббота", "Sestdiena"),
    "sun": ("Sunday", "Воскресенье", "Svētdiena"),
}
SELECT = {"legionella_day": (("Legionella cycle day", "День антилегионеллы", "Antilegionellas diena"), DAYS)}

STATUS = {
    "disabled": ("Off", "Выключено", "Izslēgts"),
    "no_data": ("No data", "Нет данных", "Nav datu"),
    "blocked": ("Blocked", "Заблокирован", "Bloķēts"),
    "legionella": ("Legionella cycle", "Антилегионелла", "Antilegionella"),
    "summer": ("Summer", "Лето", "Vasara"),
    "vacation": ("Vacation", "Отпуск", "Atvaļinājums"),
    "pv_boost": ("PV surplus", "Излишек PV", "PV pārpalikums"),
    "boost": ("Cheap - boosting", "Дёшево - нагрев", "Lēti - uzsildīšana"),
    "saving": ("Expensive - saving", "Дорого - экономия", "Dārgi - taupīšana"),
    "normal": ("Normal", "Норма", "Normāls"),
}
LEVEL = {
    "cheap": ("Cheap", "Дёшево", "Lēti"),
    "normal": ("Normal", "Нормально", "Normāli"),
    "expensive": ("Expensive", "Дорого", "Dārgi"),
    "unknown": ("Unknown", "Неизвестно", "Nav zināms"),
}
SENSOR = {
    "status": (("Status", "Статус", "Statuss"), STATUS),
    "target_flow": (("Target flow temperature", "Целевая температура подачи", "Mērķa turpgaitas temperatūra"), None),
    "curve_flow": (("Curve flow temperature", "Подача по кривой", "Turpgaita pēc līknes"), None),
    "total_offset": (("Total flow offset", "Суммарная коррекция подачи", "Kopējā turpgaitas korekcija"), None),
    "outdoor_filtered": (("Damped outdoor temperature", "Усреднённая наружная температура", "Vidējotā āra temperatūra"), None),
    "price_level": (("Price level", "Уровень цены", "Cenas līmenis"), LEVEL),
    "price_rank": (("Price rank today", "Место цены за сутки", "Cenas vieta diennaktī"), None),
    "current_price": (("Electricity price", "Цена электричества", "Elektrības cena"), None),
    "dhw_target": (("Hot water target", "Целевая температура ГВС", "Karstā ūdens mērķa temperatūra"), None),
    "sg_state": (("SG Ready state", "Состояние SG Ready", "SG Ready stāvoklis"), None),
}
BINARY = {
    "summer_active": ("Summer mode active", "Летний режим активен", "Vasaras režīms aktīvs"),
    "hp_blocked": ("Heat pump blocked", "Тепловой насос заблокирован", "Siltumsūknis bloķēts"),
    "legionella_active": ("Legionella cycle running", "Идёт антилегионелла", "Notiek antilegionella"),
    "circ_demand": ("Circulation pump", "Циркуляционный насос", "Cirkulācijas sūknis"),
    "aux_demand": ("Auxiliary heater", "Дополнительный котёл", "Papildu katls"),
}

# config flow field: (label, description)
MAIN_FIELDS = {
    "name": (("Name", "Название", "Nosaukums"), None),
    "outdoor_sensor": (
        ("Outdoor temperature sensor", "Датчик наружной температуры", "Āra temperatūras sensors"),
        None,
    ),
    "nordpool_area": (
        ("Nord Pool price area", "Ценовая зона Nord Pool", "Nord Pool cenu zona"),
        (
            "SmartHP downloads the prices itself; no other integration is needed.",
            "SmartHP сам загружает цены; другая интеграция не нужна.",
            "SmartHP pats lejupielādē cenas; cita integrācija nav vajadzīga.",
        ),
    ),
    "vat_percent": (
        ("VAT added to the price", "НДС, добавляемый к цене", "Cenai pieskaitāmais PVN"),
        None,
    ),
    "price_sensor": (
        ("Own price sensor instead of built-in Nord Pool (optional)", "Свой датчик цены вместо встроенного Nord Pool (необязательно)", "Savs cenas sensors iebūvētā Nord Pool vietā (nav obligāti)"),
        (
            "Leave empty to use the built-in Nord Pool prices.",
            "Оставьте пустым, чтобы использовать встроенные цены Nord Pool.",
            "Atstājiet tukšu, lai izmantotu iebūvētās Nord Pool cenas.",
        ),
    ),
    "setpoint_entity": (
        ("Heat pump setpoint (optional)", "Уставка теплового насоса (необязательно)", "Siltumsūkņa uzdotā vērtība (nav obligāti)"),
        (
            "Number or climate entity that SmartHP writes the calculated value to.",
            "Сущность number или climate, в которую SmartHP записывает рассчитанное значение.",
            "Number vai climate entītija, kurā SmartHP ieraksta aprēķināto vērtību.",
        ),
    ),
    "setpoint_mode": (
        ("What to write to the setpoint", "Что записывать в уставку", "Ko ierakstīt uzdotajā vērtībā"),
        None,
    ),
    "block_switch": (
        ("Heat pump stop contact (optional)", "Контакт остановки насоса (необязательно)", "Siltumsūkņa apturēšanas kontakts (nav obligāti)"),
        (
            "Used only by the optional function that stops the heat pump while the auxiliary heater runs. Electricity price alone never stops the heat pump, it only shifts the setpoint.",
            "Используется только необязательной функцией остановки насоса на время работы доп. котла. Сама цена электричества насос не выключает, а только сдвигает уставку.",
            "Izmanto tikai neobligātā funkcija, kas aptur siltumsūkni papildu katla darbības laikā. Elektrības cena pati siltumsūkni neizslēdz, tikai nobīda uzdoto vērtību.",
        ),
    ),
    "block_inverted": (
        ("Switch ON means the heat pump is blocked", "Включённый контакт = насос заблокирован", "Ieslēgts kontakts = siltumsūknis bloķēts"),
        (
            "Leave off if the switch ON means the heat pump may run.",
            "Оставьте выключенным, если включённый контакт разрешает работу насоса.",
            "Atstājiet izslēgtu, ja ieslēgts kontakts atļauj siltumsūkņa darbību.",
        ),
    ),
}
OPTIONAL_FIELDS = {
    "circulation_pump": (("Hot water circulation pump", "Циркуляционный насос ГВС", "Karstā ūdens cirkulācijas sūknis"), None),
    "dhw_sensor": (("Boiler (hot water) temperature sensor", "Датчик температуры воды в бойлере", "Boilera ūdens temperatūras sensors"), None),
    "dhw_setpoint_entity": (("Hot water setpoint", "Уставка температуры ГВС", "Karstā ūdens uzdotā temperatūra"), None),
    "aux_heater": (("Auxiliary heater contact", "Контакт дополнительного котла", "Papildu katla kontakts"), None),
    "room_sensor": (("Room temperature sensor", "Датчик температуры в помещении", "Telpas temperatūras sensors"), None),
    "pv_sensor": (
        ("PV surplus power sensor (W)", "Датчик излишка солнечной мощности (Вт)", "Saules enerģijas pārpalikuma jaudas sensors (W)"),
        (
            "Positive value = power exported to the grid.",
            "Положительное значение = мощность, отдаваемая в сеть.",
            "Pozitīva vērtība = tīklā nodotā jauda.",
        ),
    ),
    "sg_ready_1": (("SG Ready contact 1 (A)", "Контакт SG Ready 1 (A)", "SG Ready kontakts 1 (A)"), None),
    "sg_ready_2": (("SG Ready contact 2 (B)", "Контакт SG Ready 2 (B)", "SG Ready kontakts 2 (B)"), None),
}
TEXT = {
    "user_title": ("SmartHP: main entities", "SmartHP: основные сущности", "SmartHP: galvenās entītijas"),
    "user_desc": (
        "Choose the sensors SmartHP reads and the heat pump entities it controls.",
        "Выберите датчики, которые читает SmartHP, и сущности теплового насоса, которыми он управляет.",
        "Izvēlieties sensorus, kurus SmartHP nolasa, un siltumsūkņa entītijas, kuras tas vada.",
    ),
    "opt_title": ("SmartHP: additional functions", "SmartHP: дополнительные функции", "SmartHP: papildu funkcijas"),
    "opt_desc": (
        "All fields are optional. A function appears only if its entity is selected.",
        "Все поля необязательны. Функция появляется, только если выбрана её сущность.",
        "Visi lauki nav obligāti. Funkcija parādās tikai tad, ja izvēlēta tās entītija.",
    ),
    "sg_both": (
        "SG Ready needs both contacts.",
        "Для SG Ready нужны оба контакта.",
        "SG Ready vajadzīgi abi kontakti.",
    ),
    "mode_flow": (
        "Flow temperature (SmartHP heating curve)",
        "Температуру подачи (кривая SmartHP)",
        "Turpgaitas temperatūru (SmartHP līkne)",
    ),
    "mode_offset": (
        "Offset only (the heat pump keeps its own curve)",
        "Только смещение (кривая остаётся в насосе)",
        "Tikai nobīdi (līkne paliek siltumsūknī)",
    ),
}


def build(i: int) -> dict:
    def fields(table: dict) -> tuple[dict, dict]:
        data = {k: v[0][i] for k, v in table.items()}
        desc = {k: v[1][i] for k, v in table.items() if v[1]}
        return data, desc

    main_data, main_desc = fields(MAIN_FIELDS)
    opt_data, opt_desc = fields(OPTIONAL_FIELDS)
    init_data = {k: v for k, v in main_data.items() if k != "name"}
    simple = lambda table: {k: {"name": v[i]} for k, v in table.items()}  # noqa: E731
    with_states = lambda table: {  # noqa: E731
        k: {"name": v[0][i], **({"state": {s: t[i] for s, t in v[1].items()}} if v[1] else {})}
        for k, v in table.items()
    }
    optional_step = {
        "title": TEXT["opt_title"][i],
        "description": TEXT["opt_desc"][i],
        "data": opt_data,
        "data_description": opt_desc,
    }
    return {
        "config": {
            "step": {
                "user": {
                    "title": TEXT["user_title"][i],
                    "description": TEXT["user_desc"][i],
                    "data": main_data,
                    "data_description": main_desc,
                },
                "optional": optional_step,
            },
            "error": {"sg_both": TEXT["sg_both"][i]},
        },
        "options": {
            "step": {
                "init": {
                    "title": TEXT["user_title"][i],
                    "description": TEXT["user_desc"][i],
                    "data": init_data,
                    "data_description": main_desc,
                },
                "optional": optional_step,
            },
            "error": {"sg_both": TEXT["sg_both"][i]},
        },
        "selector": {
            "setpoint_mode": {
                "options": {"flow": TEXT["mode_flow"][i], "offset": TEXT["mode_offset"][i]}
            }
        },
        "entity": {
            "binary_sensor": simple(BINARY),
            "number": simple(NUMBER),
            "select": with_states(SELECT),
            "sensor": with_states(SENSOR),
            "switch": simple(SWITCH),
            "time": simple(TIME),
        },
    }


def main() -> None:
    (ROOT / "translations").mkdir(exist_ok=True)
    for i, lang in enumerate(LANGS):
        text = json.dumps(build(i), ensure_ascii=False, indent=2) + "\n"
        (ROOT / "translations" / f"{lang}.json").write_text(text, encoding="utf-8")
        if lang == "en":
            (ROOT / "strings.json").write_text(text, encoding="utf-8")
    print("translations written")


if __name__ == "__main__":
    main()
