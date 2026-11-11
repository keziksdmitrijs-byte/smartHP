/* SmartHP Lovelace card and sidebar panel. No external dependencies. */
const SMARTHP_VERSION = "0.3.0";

const TEXT = {
  en: {
    curve: "Heating curve", price: "Electricity price", block: "Heat pump blocking",
    summer: "Summer mode", room: "Room compensation", night: "Night setback",
    vacation: "Vacation", pv: "Solar surplus", dhw: "Hot water",
    legionella: "Legionella protection", circ: "Circulation pump", aux: "Auxiliary heater",
    outdoor: "Outdoor", flow: "Flow", priceNow: "Price", hotWater: "Hot water",
    none: "SmartHP is not set up yet. Add the integration in Settings → Devices & services.",
    priceHint: "Price values use the units of your price sensor.",
    outdoorAxis: "outdoor °C", curveBase: "curve", curveNow: "now",
  },
  ru: {
    curve: "Кривая отопления", price: "Цена электричества", block: "Блокировка теплового насоса",
    summer: "Летний режим", room: "Коррекция по помещению", night: "Ночное снижение",
    vacation: "Отпуск", pv: "Излишек солнечной энергии", dhw: "Горячая вода",
    legionella: "Защита от легионеллы", circ: "Циркуляционный насос", aux: "Дополнительный котёл",
    outdoor: "Улица", flow: "Подача", priceNow: "Цена", hotWater: "ГВС",
    none: "SmartHP ещё не настроен. Добавьте интеграцию в «Настройки → Устройства и службы».",
    priceHint: "Значения цены — в единицах вашего датчика цены.",
    outdoorAxis: "улица °C", curveBase: "кривая", curveNow: "сейчас",
  },
  lv: {
    curve: "Apkures līkne", price: "Elektrības cena", block: "Siltumsūkņa bloķēšana",
    summer: "Vasaras režīms", room: "Telpas korekcija", night: "Nakts pazeminājums",
    vacation: "Atvaļinājums", pv: "Saules enerģijas pārpalikums", dhw: "Karstais ūdens",
    legionella: "Aizsardzība pret legionellu", circ: "Cirkulācijas sūknis", aux: "Papildu katls",
    outdoor: "Ārā", flow: "Turpgaita", priceNow: "Cena", hotWater: "Karstais ūdens",
    none: "SmartHP vēl nav iestatīts. Pievienojiet integrāciju sadaļā Iestatījumi → Ierīces un pakalpojumi.",
    priceHint: "Cenas vērtības ir jūsu cenas sensora vienībās.",
    outdoorAxis: "ārā °C", curveBase: "līkne", curveNow: "tagad",
  },
};

const CURVE_KEYS = [
  [-20, "curve_m20"], [-10, "curve_m10"], [0, "curve_0"], [10, "curve_p10"], [20, "curve_p20"],
];

const SECTIONS = [
  { id: "curve", icon: "mdi:chart-bell-curve-cumulative", curve: true,
    keys: ["curve_shift", "flow_min", "flow_max", "outdoor_filter"] },
  { id: "price", icon: "mdi:cash-clock", toggle: "price_control", hint: "priceHint",
    keys: ["cheap_percent", "cheap_offset", "expensive_percent", "expensive_offset",
      "abs_thresholds", "price_always_cheap", "price_always_expensive"] },
  { id: "dhw", icon: "mdi:water-boiler", toggle: "dhw_price",
    keys: ["dhw_normal", "dhw_cheap", "dhw_expensive"] },
  { id: "legionella", icon: "mdi:bacteria", toggle: "legionella",
    keys: ["legionella_day", "legionella_time", "legionella_temp"] },
  { id: "circ", icon: "mdi:pump", toggle: "circulation",
    keys: ["circ1_start", "circ1_end", "circ2_start", "circ2_end", "circ3_start", "circ3_end",
      "circ_on_minutes", "circ_off_minutes", "circ_use_temp", "circ_min_temp", "circ_antiseize"] },
  { id: "aux", icon: "mdi:fire", hint: "priceHint",
    keys: ["aux_by_temp", "aux_outdoor_temp", "aux_hysteresis", "aux_by_price",
      "aux_price_limit", "aux_min_run", "aux_blocks_hp"] },
  { id: "summer", icon: "mdi:white-balance-sunny", toggle: "summer_mode", keys: ["summer_temp"] },
  { id: "room", icon: "mdi:home-thermometer", toggle: "room_compensation",
    keys: ["room_target", "room_factor"] },
  { id: "night", icon: "mdi:weather-night", toggle: "night_setback",
    keys: ["night_start", "night_end", "night_setback_temp"] },
  { id: "pv", icon: "mdi:solar-power", toggle: "pv_boost", keys: ["pv_threshold", "pv_offset"] },
  { id: "vacation", icon: "mdi:bag-suitcase", toggle: "vacation", keys: ["vacation_setback_temp"] },
];

const STYLE = `
  :host { display: block; }
  .card {
    background: var(--ha-card-background, var(--card-background-color, #fff));
    color: var(--primary-text-color);
    border-radius: var(--ha-card-border-radius, 12px);
    border: 1px solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
    padding: 16px; box-sizing: border-box;
  }
  .head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
  .head ha-icon { color: var(--primary-color); --mdc-icon-size: 28px; }
  .title { font-size: 20px; font-weight: 500; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
  .chip {
    display: flex; flex-direction: column; padding: 6px 12px; border-radius: 10px; min-width: 64px;
    background: var(--secondary-background-color, rgba(127,127,127,.12));
  }
  .chip small { color: var(--secondary-text-color); font-size: 11px; line-height: 14px; }
  .chip b { font-size: 15px; font-weight: 500; white-space: nowrap; }
  .chip.cheap b { color: var(--success-color, #43a047); }
  .chip.expensive b { color: var(--error-color, #db4437); }
  .flags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }
  .flag {
    display: none; align-items: center; gap: 4px; font-size: 12px; padding: 3px 8px;
    border-radius: 999px; background: var(--primary-color); color: var(--text-primary-color, #fff);
  }
  .flag.on { display: inline-flex; }
  .flag ha-icon { --mdc-icon-size: 14px; }
  section { border-top: 1px solid var(--divider-color, #e0e0e0); padding: 12px 0 4px; }
  .shead { display: flex; align-items: center; gap: 10px; min-height: 32px; }
  .shead ha-icon { color: var(--secondary-text-color); --mdc-icon-size: 20px; }
  .shead > span:not(.sw) { flex: 1; font-weight: 500; }
  .body { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 2px 20px; padding: 6px 0 8px; }
  .body.off { opacity: .45; }
  .row { display: flex; align-items: center; gap: 8px; min-height: 38px; }
  .row label { flex: 1; font-size: 14px; color: var(--primary-text-color); min-width: 0; }
  .unit { color: var(--secondary-text-color); font-size: 12px; min-width: 22px; }
  .hint { grid-column: 1 / -1; font-size: 12px; color: var(--secondary-text-color); }
  input[type=number], input[type=time], select {
    font: inherit; font-size: 14px; color: var(--primary-text-color);
    background: var(--secondary-background-color, rgba(127,127,127,.12));
    border: 1px solid transparent; border-radius: 8px; padding: 6px 8px; box-sizing: border-box;
    color-scheme: light dark;
  }
  input[type=number] { width: 84px; text-align: right; }
  input:focus, select:focus { outline: none; border-color: var(--primary-color); }
  .sw { position: relative; width: 40px; height: 22px; flex: none; cursor: pointer; }
  .sw input { opacity: 0; width: 100%; height: 100%; margin: 0; cursor: pointer; position: absolute; z-index: 1; }
  .sw i { position: absolute; inset: 0; border-radius: 999px; background: var(--disabled-color, #9e9e9e); transition: background .15s; }
  .sw i::after { content: ""; position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform .15s; }
  .sw input:checked + i { background: var(--primary-color); }
  .sw input:checked + i::after { transform: translateX(18px); }
  .sw input:focus-visible + i { box-shadow: 0 0 0 2px var(--primary-color); }
  svg { width: 100%; height: auto; max-height: 280px; display: block; margin: 4px 0; }
  svg text { fill: var(--secondary-text-color); font-size: 9px; }
  .grid { stroke: var(--divider-color, #e0e0e0); stroke-width: .5; }
  .base { fill: none; stroke: var(--secondary-text-color); stroke-width: 1.2; stroke-dasharray: 4 3; }
  .eff { fill: none; stroke: var(--primary-color); stroke-width: 2.2; stroke-linejoin: round; }
  .pt { fill: var(--primary-color); }
  .now { fill: var(--accent-color, #ff9800); stroke: var(--card-background-color, #fff); stroke-width: 1.5; }
  .points { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin: 2px 0 8px; }
  .points div { display: flex; flex-direction: column; align-items: center; gap: 2px; }
  .points small { color: var(--secondary-text-color); font-size: 11px; }
  .points input { width: 100%; text-align: center; padding: 6px 2px; }
  .empty { color: var(--secondary-text-color); padding: 8px 0; }
`;

function smarthpDevices(hass) {
  const ids = [];
  for (const ent of Object.values(hass.entities || {})) {
    if (ent.platform === "smarthp" && ent.device_id && !ids.includes(ent.device_id)) {
      ids.push(ent.device_id);
    }
  }
  return ids;
}

class SmartHPCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._signature = null;
    this._controls = [];
  }

  static getStubConfig() { return {}; }
  setConfig(config) { this._config = config || {}; this._signature = null; }
  getCardSize() { return 14; }
  getGridOptions() { return { columns: "full" }; }

  set hass(hass) {
    this._hass = hass;
    this._refresh();
  }

  get _t() {
    const lang = ((this._hass.locale && this._hass.locale.language) || this._hass.language || "en").slice(0, 2);
    return TEXT[lang] || TEXT.en;
  }

  _deviceId() {
    const ids = smarthpDevices(this._hass);
    const want = this._config.device;
    if (want) {
      const devices = this._hass.devices || {};
      const found = ids.find((id) => id === want || (devices[id] && (devices[id].name_by_user || devices[id].name) === want));
      if (found) return found;
    }
    return ids[0];
  }

  _entityMap(deviceId) {
    const map = {};
    for (const ent of Object.values(this._hass.entities || {})) {
      if (ent.platform !== "smarthp" || ent.device_id !== deviceId) continue;
      const key = ent.translation_key || ent.entity_id.split(".")[1].replace(/^smarthp_/, "");
      if (this._hass.states[ent.entity_id]) map[key] = ent.entity_id;
    }
    return map;
  }

  _refresh() {
    if (!this._hass) return;
    const deviceId = this._deviceId();
    const map = deviceId ? this._entityMap(deviceId) : {};
    const lang = this._t === TEXT.en ? "en" : this._t.curve;
    const signature = `${deviceId}|${lang}|${Object.values(map).sort().join(",")}`;
    if (signature !== this._signature) {
      this._signature = signature;
      this._map = map;
      this._deviceName = this._name(deviceId);
      this._build();
    }
    this._update();
  }

  _name(deviceId) {
    const dev = (this._hass.devices || {})[deviceId];
    return (dev && (dev.name_by_user || dev.name)) || "SmartHP";
  }

  _label(key) {
    const st = this._hass.states[this._map[key]];
    let name = (st && st.attributes.friendly_name) || key;
    if (name.startsWith(this._deviceName + " ")) name = name.slice(this._deviceName.length + 1);
    return name.charAt(0).toUpperCase() + name.slice(1);
  }

  _el(tag, cls, text) {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text !== undefined) el.textContent = text;
    return el;
  }

  _icon(icon) {
    const el = document.createElement("ha-icon");
    el.setAttribute("icon", icon);
    return el;
  }

  _control(key) {
    const entityId = this._map[key];
    const domain = entityId.split(".")[0];
    const st = this._hass.states[entityId];
    let el;
    let wrap;
    if (domain === "switch") {
      wrap = this._el("span", "sw");
      el = document.createElement("input");
      el.type = "checkbox";
      wrap.append(el, document.createElement("i"));
      el.addEventListener("change", () =>
        this._hass.callService("switch", el.checked ? "turn_on" : "turn_off", { entity_id: entityId }));
    } else if (domain === "number") {
      el = document.createElement("input");
      el.type = "number";
      el.min = st.attributes.min; el.max = st.attributes.max; el.step = st.attributes.step;
      el.inputMode = "decimal";
      el.addEventListener("change", () => {
        const value = parseFloat(el.value);
        if (Number.isNaN(value)) { this._update(); return; }
        this._hass.callService("number", "set_value", { entity_id: entityId, value });
      });
    } else if (domain === "time") {
      el = document.createElement("input");
      el.type = "time";
      el.addEventListener("change", () => {
        if (el.value) this._hass.callService("time", "set_value", { entity_id: entityId, time: `${el.value.slice(0, 5)}:00` });
      });
    } else if (domain === "select") {
      el = document.createElement("select");
      for (const option of st.attributes.options || []) {
        const opt = document.createElement("option");
        opt.value = option;
        const tk = `component.smarthp.entity.select.${key}.state.${option}`;
        opt.textContent = (this._hass.localize && this._hass.localize(tk)) || option;
        el.append(opt);
      }
      el.addEventListener("change", () =>
        this._hass.callService("select", "select_option", { entity_id: entityId, option: el.value }));
    } else {
      el = this._el("span");
    }
    el.setAttribute("aria-label", this._label(key));
    this._controls.push({ el, entityId, domain });
    return wrap || el;
  }

  _row(key) {
    const row = this._el("div", "row");
    row.append(this._el("label", "", this._label(key)), this._control(key));
    const unit = this._hass.states[this._map[key]].attributes.unit_of_measurement;
    if (unit) row.append(this._el("span", "unit", unit));
    return row;
  }

  _build() {
    const root = this.shadowRoot;
    root.innerHTML = "";
    this._controls = [];
    this._chips = {};
    this._flags = {};
    this._bodies = [];
    const style = document.createElement("style");
    style.textContent = STYLE;
    const card = this._el("div", "card");
    root.append(style, card);
    const t = this._t;
    const map = this._map;

    const head = this._el("div", "head");
    head.append(this._icon("mdi:heat-pump"), this._el("div", "title", this._config.title || this._deviceName));
    if (map.enabled) head.append(this._control("enabled"));
    card.append(head);

    if (!Object.keys(map).length) {
      card.append(this._el("div", "empty", t.none));
      return;
    }

    const chips = this._el("div", "chips");
    const chip = (id, label) => {
      const el = this._el("div", "chip");
      const value = this._el("b", "", "–");
      el.append(this._el("small", "", label), value);
      chips.append(el);
      this._chips[id] = { el, value };
    };
    if (map.status) chip("status", this._label("status"));
    if (map.outdoor_filtered) chip("outdoor_filtered", t.outdoor);
    if (map.target_flow) chip("target_flow", t.flow);
    if (map.price_level) chip("price_level", t.priceNow);
    if (map.current_price) chip("current_price", "Nord Pool");
    if (map.dhw_target) chip("dhw_target", t.hotWater);
    if (map.sg_state) chip("sg_state", "SG Ready");
    card.append(chips);

    const flags = this._el("div", "flags");
    for (const [key, icon] of [["hp_blocked", "mdi:lock"], ["summer_active", "mdi:white-balance-sunny"],
      ["legionella_active", "mdi:bacteria"], ["circ_demand", "mdi:pump"], ["aux_demand", "mdi:fire"]]) {
      if (!map[key]) continue;
      const el = this._el("span", "flag");
      el.append(this._icon(icon), this._el("span", "", this._label(key)));
      flags.append(el);
      this._flags[key] = el;
    }
    card.append(flags);

    for (const sec of SECTIONS) {
      const keys = sec.keys.filter((k) => map[k]);
      const hasCurve = sec.curve && CURVE_KEYS.every(([, k]) => map[k]);
      if (!keys.length && !hasCurve && !(sec.toggle && map[sec.toggle])) continue;
      const section = document.createElement("section");
      const shead = this._el("div", "shead");
      shead.append(this._icon(sec.icon), this._el("span", "", t[sec.id]));
      if (sec.toggle && map[sec.toggle]) shead.append(this._control(sec.toggle));
      section.append(shead);
      if (hasCurve) {
        this._svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this._svg.setAttribute("viewBox", "0 0 340 150");
        this._svg.setAttribute("role", "img");
        this._svg.setAttribute("aria-label", t.curve);
        section.append(this._svg);
        const points = this._el("div", "points");
        for (const [temp, key] of CURVE_KEYS) {
          const cell = this._el("div");
          cell.append(this._el("small", "", `${temp > 0 ? "+" : ""}${temp} °C`), this._control(key));
          points.append(cell);
        }
        section.append(points);
      }
      const body = this._el("div", "body");
      for (const key of keys) body.append(this._row(key));
      if (sec.hint && keys.length) body.append(this._el("div", "hint", t[sec.hint]));
      section.append(body);
      if (sec.toggle && map[sec.toggle]) this._bodies.push({ body, entityId: map[sec.toggle] });
      card.append(section);
    }
  }

  _format(entityId) {
    const st = this._hass.states[entityId];
    if (!st || st.state === "unknown" || st.state === "unavailable") return "–";
    if (this._hass.formatEntityState) return this._hass.formatEntityState(st);
    const unit = st.attributes.unit_of_measurement;
    return unit ? `${st.state} ${unit}` : st.state;
  }

  _num(key) {
    const st = this._hass.states[this._map[key]];
    const value = st ? parseFloat(st.state) : NaN;
    return Number.isNaN(value) ? null : value;
  }

  _update() {
    const hass = this._hass;
    const active = this.shadowRoot.activeElement;
    for (const { el, entityId, domain } of this._controls) {
      const st = hass.states[entityId];
      if (!st || el === active) continue;
      if (domain === "switch") el.checked = st.state === "on";
      else if (domain === "number") el.value = String(parseFloat(st.state));
      else if (domain === "time") el.value = (st.state || "").slice(0, 5);
      else if (domain === "select") el.value = st.state;
    }
    for (const { body, entityId } of this._bodies || []) {
      const st = hass.states[entityId];
      body.classList.toggle("off", !!st && st.state !== "on");
    }
    for (const [key, chip] of Object.entries(this._chips || {})) {
      chip.value.textContent = this._format(this._map[key]);
      if (key === "price_level") {
        const st = hass.states[this._map[key]];
        chip.el.classList.toggle("cheap", !!st && st.state === "cheap");
        chip.el.classList.toggle("expensive", !!st && st.state === "expensive");
        const price = st && st.attributes.price;
        chip.el.title = price === undefined || price === null ? "" : String(price);
      }
    }
    for (const [key, el] of Object.entries(this._flags || {})) {
      const st = hass.states[this._map[key]];
      el.classList.toggle("on", !!st && st.state === "on");
    }
    if (this._svg && this._svg.isConnected) this._drawCurve();
  }

  _drawCurve() {
    const pts = CURVE_KEYS.map(([x, key]) => [x, this._num(key)]);
    if (pts.some(([, y]) => y === null)) return;
    const shift = this._num("curve_shift") || 0;
    const fmin = this._num("flow_min");
    const fmax = this._num("flow_max");
    const lim = (y) => Math.max(fmin === null ? -1e9 : fmin, Math.min(fmax === null ? 1e9 : fmax, y));
    const eff = pts.map(([x, y]) => [x, lim(y + shift)]);
    const outdoor = this._num("outdoor_filtered");
    const target = this._num("target_flow");
    const ys = [...pts.map((p) => p[1]), ...eff.map((p) => p[1])];
    if (target !== null) ys.push(target);
    const yMin = Math.floor((Math.min(...ys) - 3) / 5) * 5;
    const yMax = Math.ceil((Math.max(...ys) + 3) / 5) * 5;
    const X0 = 28, X1 = 332, Y0 = 8, Y1 = 126, xMin = -25, xMax = 25;
    const px = (x) => X0 + ((Math.max(xMin, Math.min(xMax, x)) - xMin) / (xMax - xMin)) * (X1 - X0);
    const py = (y) => Y1 - ((y - yMin) / (yMax - yMin || 1)) * (Y1 - Y0);
    const line = (list) => {
      const full = [[xMin, list[0][1]], ...list, [xMax, list[list.length - 1][1]]];
      return full.map(([x, y]) => `${px(x).toFixed(1)},${py(y).toFixed(1)}`).join(" ");
    };
    let html = "";
    const stepY = yMax - yMin > 30 ? 10 : 5;
    for (let y = yMin; y <= yMax; y += stepY) {
      html += `<line class="grid" x1="${X0}" x2="${X1}" y1="${py(y)}" y2="${py(y)}"/>`;
      html += `<text x="${X0 - 4}" y="${py(y) + 3}" text-anchor="end">${y}</text>`;
    }
    for (let x = -20; x <= 20; x += 10) {
      html += `<line class="grid" x1="${px(x)}" x2="${px(x)}" y1="${Y0}" y2="${Y1}"/>`;
      html += `<text x="${px(x)}" y="${Y1 + 11}" text-anchor="middle">${x > 0 ? "+" : ""}${x}</text>`;
    }
    html += `<text x="${X1}" y="${Y1 + 22}" text-anchor="end">${this._t.outdoorAxis}</text>`;
    html += `<polyline class="base" points="${line(pts)}"/>`;
    html += `<polyline class="eff" points="${line(eff)}"/>`;
    for (const [x, y] of eff) html += `<circle class="pt" cx="${px(x)}" cy="${py(y)}" r="2.6"/>`;
    if (outdoor !== null && target !== null) {
      html += `<circle class="now" cx="${px(outdoor)}" cy="${py(target)}" r="4.5"><title>${this._t.curveNow}: ${outdoor} °C → ${target} °C</title></circle>`;
    }
    this._svg.innerHTML = html;
  }
}

class SmartHPPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._cards = new Map();
  }

  set narrow(value) { this._narrow = value; this._layout(); }
  set panel(value) { this._panel = value; }

  set hass(hass) {
    this._hass = hass;
    if (!this._wrap) {
      this.shadowRoot.innerHTML = `
        <style>
          :host { display: block; min-height: 100vh; background: var(--primary-background-color); }
          .bar { display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 16px;
            background: var(--app-header-background-color, var(--primary-color));
            color: var(--app-header-text-color, #fff); font-size: 20px; position: sticky; top: 0; z-index: 2; }
          .bar button { display: none; background: none; border: 0; color: inherit; cursor: pointer; padding: 8px; }
          .bar.narrow button { display: block; }
          .wrap { max-width: 960px; margin: 0 auto; padding: 16px; display: grid; gap: 16px; }
        </style>
        <div class="bar"><button aria-label="Menu"><ha-icon icon="mdi:menu"></ha-icon></button><span>SmartHP</span></div>
        <div class="wrap"></div>`;
      this._wrap = this.shadowRoot.querySelector(".wrap");
      this._bar = this.shadowRoot.querySelector(".bar");
      this._bar.querySelector("button").addEventListener("click", () =>
        this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true })));
      this._layout();
    }
    const ids = smarthpDevices(hass);
    const list = ids.length ? ids : [""];
    for (const [id, card] of this._cards) {
      if (!list.includes(id)) { card.remove(); this._cards.delete(id); }
    }
    for (const id of list) {
      let card = this._cards.get(id);
      if (!card) {
        card = document.createElement("smarthp-card");
        card.setConfig(id ? { device: id } : {});
        this._cards.set(id, card);
        this._wrap.append(card);
      }
      card.hass = hass;
    }
  }

  _layout() {
    if (this._bar) this._bar.classList.toggle("narrow", !!this._narrow);
  }
}

if (!customElements.get("smarthp-card")) customElements.define("smarthp-card", SmartHPCard);
if (!customElements.get("smarthp-panel")) customElements.define("smarthp-panel", SmartHPPanel);

window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "smarthp-card")) {
  window.customCards.push({
    type: "smarthp-card",
    name: "SmartHP",
    description: "Heat pump control: heating curve, electricity price, hot water, circulation, auxiliary heater.",
    preview: false,
  });
}
console.info(`%c SMARTHP-CARD %c ${SMARTHP_VERSION} `, "background:#1976d2;color:#fff", "background:#eee;color:#333");
