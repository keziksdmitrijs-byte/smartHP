/* SmartHP Lovelace card and sidebar panel. No external dependencies. */
const SMARTHP_VERSION = "0.4.0";

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
    chart: "Electricity price today", info: "What is this?", hours: "h",
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
    chart: "Цена электричества сегодня", info: "Что это?", hours: "ч",
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
    chart: "Elektrības cena šodien", info: "Kas tas ir?", hours: "h",
  },
};

const HELP = {
  ru: {
    enabled: "Главный выключатель. Когда выключен, SmartHP продолжает считать значения, но ничего не записывает в тепловой насос, бойлер, циркуляционный насос и доп. котёл.",
    chart: "Цены на сегодня по периодам. Зелёные — дешёвые периоды, красные — дорогие, серые — обычные. Обведённый столбец — текущий период. Доли дешёвых и дорогих часов задаются в разделе «Цена электричества».",
    curve: "Кривая задаёт температуру подачи для пяти наружных температур; между точками значение считается по прямой. Чем холоднее на улице, тем горячее подача. Пунктир — сама кривая, сплошная линия — с учётом сдвига и ограничений, точка — текущий режим.",
    curve_shift: "Поднимает или опускает всю кривую на заданное число градусов. Удобно, если в доме постоянно чуть холодно или чуть жарко.",
    flow_min: "Ниже этой температуры подача не опустится, что бы ни давали кривая и коррекции. Она же задаётся в летнем режиме.",
    flow_max: "Выше этой температуры подача не поднимется. Для тёплого пола обычно 35–40 °C, для радиаторов 50–55 °C.",
    outdoor_filter: "Сглаживает наружную температуру за указанное число часов, чтобы насос не реагировал на короткие скачки (солнце на датчике, порыв ветра). 0 — без сглаживания.",
    price_control: "В дешёвые периоды уставка повышается, в дорогие понижается — дом запасает тепло, когда электричество дешевле. Насос при этом не выключается.",
    cheap_percent: "Какая доля суток считается дешёвой. 30 % — это примерно 7 самых дешёвых часов дня.",
    cheap_offset: "На сколько градусов повышается уставка в дешёвые периоды.",
    expensive_percent: "Какая доля суток считается дорогой. 25 % — это 6 самых дорогих часов дня.",
    expensive_offset: "На сколько градусов понижается уставка в дорогие периоды.",
    abs_thresholds: "Дополнительно к долям суток: цена ниже первого порога всегда считается дешёвой, выше второго — всегда дорогой, даже если в этот день все цены похожи.",
    price_always_cheap: "Если цена не выше этого значения, период считается дешёвым. Работает, только когда включены абсолютные пороги.",
    price_always_expensive: "Если цена не ниже этого значения, период считается дорогим. Работает, только когда включены абсолютные пороги.",
    dhw_price: "Меняет уставку бойлера по цене: в дешёвые периоды вода греется сильнее, в дорогие — слабее.",
    dhw_normal: "Уставка бойлера в периоды с обычной ценой.",
    dhw_cheap: "Уставка бойлера в дешёвые периоды и при излишке солнечной энергии.",
    dhw_expensive: "Уставка бойлера в дорогие периоды и в режиме отпуска.",
    legionella: "Раз в неделю прогревает бойлер до высокой температуры, чтобы в воде не размножались бактерии легионеллы.",
    legionella_day: "День недели, в который выполняется прогрев.",
    legionella_time: "Время начала прогрева. Он длится, пока бойлер не достигнет заданной температуры, но не дольше 3 часов.",
    legionella_temp: "Температура прогрева. Выше примерно 55 °C большинству насосов нужен ТЭН — проверьте, что ваш насос это может.",
    circulation: "Включает циркуляционный насос ГВС по расписанию, чтобы горячая вода сразу была в кранах. В режиме отпуска циркуляция не работает.",
    circ_period: "Циркуляция работает внутри заданных периодов. Период можно задать через полночь. Если начало и конец совпадают, период выключен.",
    circ_on_minutes: "Сколько минут подряд насос работает внутри периода.",
    circ_off_minutes: "Сколько минут насос отдыхает после работы. 0 — работает весь период без пауз.",
    circ_use_temp: "Разрешает циркуляцию, только когда вода в бойлере достаточно горячая, чтобы не гонять по трубам остывшую воду.",
    circ_min_temp: "Циркуляция включается, когда бойлер не холоднее этой температуры, и выключается, когда он остынет на 3 °C ниже.",
    circ_antiseize: "Если насос не работал сутки, включает его на минуту, чтобы он не закис.",
    aux: "Дополнительный котёл включается контактом. Условия по температуре и по цене работают независимо: достаточно одного. В летнем режиме котёл выключен.",
    aux_by_temp: "Включает доп. котёл, когда на улице холоднее заданной температуры и насосу не хватает мощности.",
    aux_outdoor_temp: "Наружная температура, ниже которой включается доп. котёл (точка бивалентности).",
    aux_hysteresis: "На сколько градусов должно потеплеть выше порога, чтобы котёл выключился. Защищает от частых включений.",
    aux_by_price: "Включает доп. котёл, когда электричество дороже заданной цены, то есть топить котлом выгоднее.",
    aux_price_limit: "Цена электричества, выше которой включается доп. котёл.",
    aux_min_run: "Минимальное время работы котла после включения, даже если условие уже пропало.",
    aux_blocks_hp: "Пока котёл работает по цене, тепловой насос останавливается контактом остановки. Выключите, если котёл должен только помогать насосу.",
    summer_mode: "Когда на улице теплее заданной температуры, отопление выключается: уставка опускается до минимальной, доп. котёл не работает.",
    summer_temp: "Наружная температура, выше которой включается летний режим. Обратно он выключается, когда станет на 1 °C холоднее.",
    room_compensation: "Поправляет уставку по реальной температуре в помещении: в доме холоднее заданной — подача выше, теплее — ниже.",
    room_target: "Температура, которую нужно держать в помещении.",
    room_factor: "На сколько градусов меняется подача за каждый градус отклонения в помещении. Чем больше, тем сильнее реакция. Поправка не больше ±10 °C.",
    night_setback: "Понижает уставку в заданное время, например ночью.",
    night_time: "Время, в которое действует ночное снижение. Можно задать через полночь, например с 22:00 до 06:00.",
    night_setback_temp: "На сколько градусов понижается уставка в это время.",
    pv_boost: "Когда солнечные панели отдают излишек в сеть, уставка отопления и бойлера повышается, чтобы использовать свою энергию.",
    pv_threshold: "Мощность излишка, начиная с которой включается повышение. Выключается, когда излишек упадёт ниже 80 % порога.",
    pv_offset: "На сколько градусов повышается уставка при излишке.",
    vacation: "Режим на время отъезда: уставка отопления понижена, бойлер на экономной температуре, циркуляция выключена.",
    vacation_setback_temp: "На сколько градусов понижается уставка отопления в режиме отпуска.",
  },
  en: {
    enabled: "Master switch. When off, SmartHP keeps calculating but writes nothing to the heat pump, boiler, circulation pump or auxiliary heater.",
    chart: "Today's prices by period. Green periods are cheap, red are expensive, grey are normal. The outlined bar is the current period. The cheap and expensive shares are set in the Electricity price section.",
    curve: "The curve sets the flow temperature for five outdoor temperatures; values in between follow a straight line. The colder it is outside, the hotter the flow. Dashed line: the curve itself; solid line: with shift and limits; dot: current operating point.",
    curve_shift: "Raises or lowers the whole curve by this many degrees. Useful if the house is always slightly too cold or too warm.",
    flow_min: "The flow never goes below this temperature, whatever the curve and corrections say. It is also used in summer mode.",
    flow_max: "The flow never goes above this temperature. Typically 35–40 °C for underfloor heating, 50–55 °C for radiators.",
    outdoor_filter: "Smooths the outdoor temperature over this many hours so the heat pump ignores short spikes (sun on the sensor, a gust of wind). 0 = no smoothing.",
    price_control: "The setpoint is raised in cheap periods and lowered in expensive ones, so the house stores heat when electricity is cheaper. The heat pump is never switched off.",
    cheap_percent: "Which share of the day counts as cheap. 30 % is roughly the 7 cheapest hours of the day.",
    cheap_offset: "How many degrees the setpoint is raised in cheap periods.",
    expensive_percent: "Which share of the day counts as expensive. 25 % is the 6 most expensive hours of the day.",
    expensive_offset: "How many degrees the setpoint is lowered in expensive periods.",
    abs_thresholds: "In addition to the daily shares: a price below the first threshold is always cheap and above the second always expensive, even on a day when all prices are similar.",
    price_always_cheap: "A period at or below this price counts as cheap. Used only when absolute thresholds are on.",
    price_always_expensive: "A period at or above this price counts as expensive. Used only when absolute thresholds are on.",
    dhw_price: "Changes the boiler setpoint by price: hotter in cheap periods, cooler in expensive ones.",
    dhw_normal: "Boiler setpoint in periods with a normal price.",
    dhw_cheap: "Boiler setpoint in cheap periods and during PV surplus.",
    dhw_expensive: "Boiler setpoint in expensive periods and in vacation mode.",
    legionella: "Heats the boiler to a high temperature once a week so legionella bacteria cannot grow in the water.",
    legionella_day: "Day of the week on which the cycle runs.",
    legionella_time: "Start time of the cycle. It runs until the boiler reaches the set temperature, but no longer than 3 hours.",
    legionella_temp: "Cycle temperature. Above about 55 °C most heat pumps need an immersion heater — check that yours can reach it.",
    circulation: "Runs the hot water circulation pump on a schedule so hot water is at the taps immediately. Circulation is off in vacation mode.",
    circ_period: "Circulation runs inside these periods. A period may cross midnight. If start and end are equal, the period is off.",
    circ_on_minutes: "How many minutes in a row the pump runs inside a period.",
    circ_off_minutes: "How many minutes the pump rests after running. 0 = runs for the whole period without pauses.",
    circ_use_temp: "Allows circulation only when the boiler water is hot enough, so cooled water is not pumped around.",
    circ_min_temp: "Circulation starts when the boiler is at least this warm and stops when it cools 3 °C below.",
    circ_antiseize: "If the pump has not run for a day, runs it for one minute so it does not seize.",
    aux: "The auxiliary heater is switched by a contact. The temperature and price conditions work independently: one is enough. The heater is off in summer mode.",
    aux_by_temp: "Turns the heater on when it is colder outside than the set temperature and the heat pump lacks capacity.",
    aux_outdoor_temp: "Outdoor temperature below which the heater turns on (bivalence point).",
    aux_hysteresis: "How many degrees above the threshold it must warm up before the heater turns off. Prevents frequent switching.",
    aux_by_price: "Turns the heater on when electricity costs more than the set price, i.e. the heater is cheaper to run.",
    aux_price_limit: "Electricity price above which the heater turns on.",
    aux_min_run: "Minimum time the heater stays on after starting, even if the condition has gone.",
    aux_blocks_hp: "While the heater runs because of price, the heat pump is stopped by the stop contact. Turn off if the heater should only assist the heat pump.",
    summer_mode: "When it is warmer outside than the set temperature, heating is off: the setpoint drops to the minimum and the auxiliary heater does not run.",
    summer_temp: "Outdoor temperature above which summer mode starts. It ends when it gets 1 °C colder.",
    room_compensation: "Corrects the setpoint by the real room temperature: colder than the target — higher flow, warmer — lower flow.",
    room_target: "Temperature to keep in the room.",
    room_factor: "How many degrees the flow changes per degree of room deviation. Higher means a stronger reaction. The correction is limited to ±10 °C.",
    night_setback: "Lowers the setpoint at a set time, for example at night.",
    night_time: "Time during which the night setback applies. It may cross midnight, e.g. 22:00 to 06:00.",
    night_setback_temp: "How many degrees the setpoint is lowered during this time.",
    pv_boost: "When the solar panels export surplus power, the heating and boiler setpoints are raised to use your own energy.",
    pv_threshold: "Surplus power at which the boost starts. It ends when the surplus falls below 80 % of the threshold.",
    pv_offset: "How many degrees the setpoint is raised during surplus.",
    vacation: "Mode for when you are away: heating setpoint lowered, boiler at the economy temperature, circulation off.",
    vacation_setback_temp: "How many degrees the heating setpoint is lowered in vacation mode.",
  },
  lv: {
    enabled: "Galvenais slēdzis. Kad izslēgts, SmartHP turpina rēķināt vērtības, bet neko neieraksta siltumsūknī, boilerī, cirkulācijas sūknī un papildu katlā.",
    chart: "Šodienas cenas pa periodiem. Zaļie — lētie periodi, sarkanie — dārgie, pelēkie — parastie. Apvilktais stabiņš — pašreizējais periods. Lēto un dārgo stundu daļas iestata sadaļā «Elektrības cena».",
    curve: "Līkne nosaka turpgaitas temperatūru piecām āra temperatūrām; starp punktiem vērtība mainās pa taisni. Jo aukstāks ārā, jo karstāka turpgaita. Raustītā līnija — pati līkne, nepārtrauktā — ar nobīdi un ierobežojumiem, punkts — pašreizējais režīms.",
    curve_shift: "Paceļ vai nolaiž visu līkni par norādīto grādu skaitu. Noder, ja mājā pastāvīgi ir nedaudz par aukstu vai par siltu.",
    flow_min: "Turpgaita nenokritīs zem šīs temperatūras neatkarīgi no līknes un korekcijām. To izmanto arī vasaras režīmā.",
    flow_max: "Turpgaita nepacelsies virs šīs temperatūras. Siltajām grīdām parasti 35–40 °C, radiatoriem 50–55 °C.",
    outdoor_filter: "Izlīdzina āra temperatūru norādītajā stundu skaitā, lai siltumsūknis nereaģētu uz īsiem lēcieniem (saule uz sensora, vēja brāzma). 0 — bez izlīdzināšanas.",
    price_control: "Lētajos periodos uzdotā vērtība tiek paaugstināta, dārgajos pazemināta — māja uzkrāj siltumu, kad elektrība ir lētāka. Siltumsūknis netiek izslēgts.",
    cheap_percent: "Kāda diennakts daļa tiek uzskatīta par lētu. 30 % ir apmēram 7 lētākās dienas stundas.",
    cheap_offset: "Par cik grādiem uzdotā vērtība tiek paaugstināta lētajos periodos.",
    expensive_percent: "Kāda diennakts daļa tiek uzskatīta par dārgu. 25 % ir 6 dārgākās dienas stundas.",
    expensive_offset: "Par cik grādiem uzdotā vērtība tiek pazemināta dārgajos periodos.",
    abs_thresholds: "Papildus diennakts daļām: cena zem pirmā sliekšņa vienmēr ir lēta, virs otrā — vienmēr dārga, pat ja tajā dienā visas cenas ir līdzīgas.",
    price_always_cheap: "Ja cena nepārsniedz šo vērtību, periods tiek uzskatīts par lētu. Darbojas tikai tad, ja ieslēgti absolūtie sliekšņi.",
    price_always_expensive: "Ja cena nav zemāka par šo vērtību, periods tiek uzskatīts par dārgu. Darbojas tikai tad, ja ieslēgti absolūtie sliekšņi.",
    dhw_price: "Maina boilera uzdoto temperatūru pēc cenas: lētajos periodos ūdens tiek sildīts vairāk, dārgajos — mazāk.",
    dhw_normal: "Boilera uzdotā temperatūra periodos ar parastu cenu.",
    dhw_cheap: "Boilera uzdotā temperatūra lētajos periodos un pie saules enerģijas pārpalikuma.",
    dhw_expensive: "Boilera uzdotā temperatūra dārgajos periodos un atvaļinājuma režīmā.",
    legionella: "Reizi nedēļā uzsilda boileri līdz augstai temperatūrai, lai ūdenī nevairotos legionellas baktērijas.",
    legionella_day: "Nedēļas diena, kurā notiek uzsildīšana.",
    legionella_time: "Uzsildīšanas sākuma laiks. Tā ilgst, līdz boileris sasniedz uzdoto temperatūru, bet ne ilgāk par 3 stundām.",
    legionella_temp: "Uzsildīšanas temperatūra. Virs aptuveni 55 °C lielākajai daļai siltumsūkņu vajadzīgs elektriskais sildelements — pārbaudiet, vai jūsu siltumsūknis to spēj.",
    circulation: "Ieslēdz karstā ūdens cirkulācijas sūkni pēc grafika, lai karstais ūdens krānos būtu uzreiz. Atvaļinājuma režīmā cirkulācija nedarbojas.",
    circ_period: "Cirkulācija darbojas norādītajos periodos. Periods var pāriet pāri pusnaktij. Ja sākums un beigas sakrīt, periods ir izslēgts.",
    circ_on_minutes: "Cik minūtes pēc kārtas sūknis darbojas perioda laikā.",
    circ_off_minutes: "Cik minūtes sūknis atpūšas pēc darbības. 0 — darbojas visu periodu bez pauzēm.",
    circ_use_temp: "Atļauj cirkulāciju tikai tad, kad ūdens boilerī ir pietiekami karsts, lai pa caurulēm netiktu dzīts atdzisis ūdens.",
    circ_min_temp: "Cirkulācija ieslēdzas, kad boileris nav aukstāks par šo temperatūru, un izslēdzas, kad tas atdziest par 3 °C zemāk.",
    circ_antiseize: "Ja sūknis nav darbojies diennakti, ieslēdz to uz minūti, lai tas neiestrēgtu.",
    aux: "Papildu katls tiek ieslēgts ar kontaktu. Temperatūras un cenas nosacījumi darbojas neatkarīgi: pietiek ar vienu. Vasaras režīmā katls ir izslēgts.",
    aux_by_temp: "Ieslēdz papildu katlu, kad ārā ir aukstāks par uzdoto temperatūru un siltumsūknim nepietiek jaudas.",
    aux_outdoor_temp: "Āra temperatūra, zem kuras ieslēdzas papildu katls (bivalences punkts).",
    aux_hysteresis: "Par cik grādiem jākļūst siltākam virs sliekšņa, lai katls izslēgtos. Pasargā no biežas ieslēgšanās.",
    aux_by_price: "Ieslēdz papildu katlu, kad elektrība ir dārgāka par uzdoto cenu, tātad kurināt ar katlu ir izdevīgāk.",
    aux_price_limit: "Elektrības cena, virs kuras ieslēdzas papildu katls.",
    aux_min_run: "Minimālais katla darbības laiks pēc ieslēgšanas, pat ja nosacījums vairs nepastāv.",
    aux_blocks_hp: "Kamēr katls darbojas cenas dēļ, siltumsūknis tiek apturēts ar apturēšanas kontaktu. Izslēdziet, ja katlam tikai jāpalīdz siltumsūknim.",
    summer_mode: "Kad ārā ir siltāks par uzdoto temperatūru, apkure tiek izslēgta: uzdotā vērtība nokrītas līdz minimālajai, papildu katls nedarbojas.",
    summer_temp: "Āra temperatūra, virs kuras ieslēdzas vasaras režīms. Tas izslēdzas, kad kļūst par 1 °C vēsāks.",
    room_compensation: "Koriģē uzdoto vērtību pēc faktiskās telpas temperatūras: mājā vēsāks par uzdoto — turpgaita augstāka, siltāks — zemāka.",
    room_target: "Temperatūra, kas jāuztur telpā.",
    room_factor: "Par cik grādiem mainās turpgaita uz katru telpas novirzes grādu. Jo lielāks, jo spēcīgāka reakcija. Korekcija nepārsniedz ±10 °C.",
    night_setback: "Pazemina uzdoto vērtību noteiktā laikā, piemēram, naktī.",
    night_time: "Laiks, kurā darbojas nakts pazeminājums. Var pāriet pāri pusnaktij, piemēram, no 22:00 līdz 06:00.",
    night_setback_temp: "Par cik grādiem uzdotā vērtība tiek pazemināta šajā laikā.",
    pv_boost: "Kad saules paneļi nodod pārpalikumu tīklā, apkures un boilera uzdotās vērtības tiek paaugstinātas, lai izmantotu savu enerģiju.",
    pv_threshold: "Pārpalikuma jauda, no kuras sākas paaugstināšana. Tā beidzas, kad pārpalikums nokrītas zem 80 % no sliekšņa.",
    pv_offset: "Par cik grādiem uzdotā vērtība tiek paaugstināta pārpalikuma laikā.",
    vacation: "Režīms prombūtnes laikam: apkures uzdotā vērtība pazemināta, boileris taupības temperatūrā, cirkulācija izslēgta.",
    vacation_setback_temp: "Par cik grādiem apkures uzdotā vērtība tiek pazemināta atvaļinājuma režīmā.",
  },
};

function helpKey(key) {
  if (/^circ\d_(start|end)$/.test(key)) return "circ_period";
  if (key === "night_start" || key === "night_end") return "night_time";
  return key;
}

const CURVE_KEYS = [
  [-20, "curve_m20"], [-10, "curve_m10"], [0, "curve_0"], [10, "curve_p10"], [20, "curve_p20"],
];

const SECTIONS = [
  { id: "curve", icon: "mdi:chart-bell-curve-cumulative", curve: true, help: "curve",
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
  { id: "aux", icon: "mdi:fire", hint: "priceHint", help: "aux",
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
  .body { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 2px 20px; padding: 6px 0 8px; align-items: start; }
  .body.off { opacity: .45; }
  .row { display: flex; align-items: center; gap: 8px; min-height: 38px; }
  .row { flex-wrap: wrap; }
  .lbl { flex: 1; min-width: 0; display: flex; align-items: center; gap: 6px; }
  .row label { font-size: 14px; color: var(--primary-text-color); min-width: 0; }
  .info {
    width: 20px; height: 20px; flex: none; padding: 0; border-radius: 50%; cursor: pointer;
    border: 1px solid var(--secondary-text-color); background: none; color: var(--secondary-text-color);
    font: italic 700 12px/1 Georgia, "Times New Roman", serif;
  }
  .info:hover, .info:focus-visible { border-color: var(--primary-color); color: var(--primary-color); outline: none; }
  .info[aria-expanded="true"] { background: var(--primary-color); border-color: var(--primary-color); color: var(--text-primary-color, #fff); }
  .help {
    flex-basis: 100%; font-size: 12.5px; line-height: 1.45; color: var(--primary-text-color);
    background: var(--secondary-background-color, rgba(127,127,127,.12));
    border-left: 3px solid var(--primary-color); border-radius: 6px; padding: 8px 10px; margin: 4px 0 8px;
  }
  .help[hidden], section[hidden] { display: none; }
  .bar { fill: var(--disabled-color, #9e9e9e); opacity: .75; }
  .bar.cheap { fill: var(--success-color, #43a047); }
  .bar.expensive { fill: var(--error-color, #db4437); }
  .bar.cur { opacity: 1; stroke: var(--primary-text-color); stroke-width: 1; }
  .curmark { fill: var(--primary-text-color); }
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

  get _lang() {
    const hass = this._hass;
    const lang = String((hass.locale && hass.locale.language) || hass.language || "en").toLowerCase().slice(0, 2);
    return TEXT[lang] ? lang : "en";
  }

  get _t() { return TEXT[this._lang]; }

  _helpText(key) {
    const k = helpKey(key);
    return HELP[this._lang][k] || HELP.en[k] || "";
  }

  _info(key) {
    const text = this._helpText(key);
    if (!text) return null;
    const btn = this._el("button", "info", "i");
    btn.type = "button";
    btn.setAttribute("aria-label", this._t.info);
    btn.setAttribute("aria-expanded", "false");
    const help = this._el("div", "help", text);
    help.hidden = true;
    btn.addEventListener("click", () => {
      help.hidden = !help.hidden;
      btn.setAttribute("aria-expanded", String(!help.hidden));
    });
    return { btn, help };
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
    const lang = this._lang;
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
    const entityId = this._map[key];
    const st = this._hass.states[entityId];
    // UI language first (same language as the rest of Home Assistant)
    if (entityId && this._hass.localize) {
      const text = this._hass.localize(`component.smarthp.entity.${entityId.split(".")[0]}.${key}.name`);
      if (text) return text;
    }
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
    const lbl = this._el("span", "lbl");
    lbl.append(this._el("label", "", this._label(key)));
    const info = this._info(key);
    if (info) lbl.append(info.btn);
    row.append(lbl, this._control(key));
    const unit = this._hass.states[this._map[key]].attributes.unit_of_measurement;
    if (unit) row.append(this._el("span", "unit", unit));
    if (info) row.append(info.help);
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
    const headInfo = map.enabled ? this._info("enabled") : null;
    if (headInfo) head.append(headInfo.btn);
    if (map.enabled) head.append(this._control("enabled"));
    card.append(head);
    if (headInfo) card.append(headInfo.help);

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
    if (map.price_level) chip("price_level", this._label("price_level"));
    if (map.current_price) chip("current_price", this._label("current_price"));
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

    this._priceSvg = null;
    if (map.current_price) {
      const section = document.createElement("section");
      const shead = this._el("div", "shead");
      shead.append(this._icon("mdi:chart-bar"), this._el("span", "", t.chart));
      const info = this._info("chart");
      if (info) shead.append(info.btn);
      section.append(shead);
      if (info) section.append(info.help);
      this._priceSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      this._priceSvg.setAttribute("viewBox", "0 0 340 112");
      this._priceSvg.setAttribute("role", "img");
      this._priceSvg.setAttribute("aria-label", t.chart);
      section.append(this._priceSvg);
      this._priceSection = section;
      card.append(section);
    }

    for (const sec of SECTIONS) {
      const keys = sec.keys.filter((k) => map[k]);
      const hasCurve = sec.curve && CURVE_KEYS.every(([, k]) => map[k]);
      if (!keys.length && !hasCurve && !(sec.toggle && map[sec.toggle])) continue;
      const section = document.createElement("section");
      const shead = this._el("div", "shead");
      shead.append(this._icon(sec.icon), this._el("span", "", t[sec.id]));
      const secInfo = this._info(sec.help || sec.toggle || "");
      if (secInfo) shead.append(secInfo.btn);
      if (sec.toggle && map[sec.toggle]) shead.append(this._control(sec.toggle));
      section.append(shead);
      if (secInfo) section.append(secInfo.help);
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
    if (this._priceSvg && this._priceSvg.isConnected) this._drawPrices();
  }

  _drawPrices() {
    const st = this._hass.states[this._map.current_price];
    const list = (st && st.attributes.today) || [];
    this._priceSection.hidden = !list.length;
    if (!list.length) return;
    const signature = JSON.stringify(list) + new Date().toISOString().slice(0, 15);
    if (signature === this._priceSignature) return;
    this._priceSignature = signature;
    const unit = (st.attributes.unit_of_measurement || "").trim();
    const hour = (iso, isEnd) => {
      const h = parseInt(iso.slice(11, 13), 10) + parseInt(iso.slice(14, 16), 10) / 60;
      return isEnd && h === 0 ? 24 : h;
    };
    const prices = list.map((p) => p.price);
    const max = Math.max(...prices, 0);
    const min = Math.min(...prices, 0);
    const span = max - min || 1;
    const X0 = 30, X1 = 334, Y0 = 8, Y1 = 88;
    const px = (h) => X0 + (h / 24) * (X1 - X0);
    const py = (v) => Y1 - ((v - min) / span) * (Y1 - Y0);
    const fmt = (v) => (Math.abs(v) >= 10 ? v.toFixed(0) : Math.abs(v) >= 1 ? v.toFixed(2) : v.toFixed(3));
    const now = Date.now();
    let html = "";
    for (const v of [max, (max + min) / 2, min]) {
      html += `<line class="grid" x1="${X0}" x2="${X1}" y1="${py(v)}" y2="${py(v)}"/>`;
      html += `<text x="${X0 - 4}" y="${py(v) + 3}" text-anchor="end">${fmt(v)}</text>`;
    }
    for (const p of list) {
      const a = hour(p.start, false), b = hour(p.end, true);
      const x = px(a), w = Math.max(0.6, px(b) - px(a) - (list.length > 48 ? 0.4 : 1.2));
      const y = Math.min(py(p.price), py(0)), h = Math.max(0.8, Math.abs(py(p.price) - py(0)));
      const cur = now >= Date.parse(p.start) && now < Date.parse(p.end);
      html += `<rect class="bar ${p.level}${cur ? " cur" : ""}" x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${w.toFixed(2)}" height="${h.toFixed(2)}"><title>${p.start.slice(11, 16)}–${p.end.slice(11, 16)}: ${fmt(p.price)} ${unit}</title></rect>`;
      if (cur) html += `<path class="curmark" d="M${(x + w / 2).toFixed(2)} ${Y1 + 3} l-3 5 h6 z"/>`;
    }
    for (let h = 0; h <= 24; h += 6) {
      html += `<text x="${px(h)}" y="${Y1 + 19}" text-anchor="${h === 24 ? "end" : h === 0 ? "start" : "middle"}">${String(h).padStart(2, "0")}:00</text>`;
    }
    if (unit) html += `<text x="${X1}" y="${Y0 + 2}" text-anchor="end">${unit}</text>`;
    this._priceSvg.innerHTML = html;
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
