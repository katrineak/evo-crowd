#!/usr/bin/env python3
"""
Generates graf.html — an interactive Plotly.js chart with tabs for multiple
EVO locations, showing:
  1. Historical (coarse) visitor data as stepped lines
  2. Evo's own estimates overlaid for comparison
  3. Real-time (fine, 5-min) polling data as smooth lines
  4. Future predictions based on both data sources
  5. Click-to-backtest: click any real-time point to see predictions from that moment
"""
import json
import csv
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "graf.html")
PREDICTION_DAYS = 7
GYM_OPEN_HOUR = 5
GYM_CLOSE_HOUR = 24

INTERVAL_SPEC = [
    ("06-10", 6, 10), ("10-12", 10, 12), ("12-15", 12, 15),
    ("15-17", 15, 17), ("17-20", 17, 20), ("20-24", 20, 24),
]

# ─── Location definitions ────────────────────────────────────────────────────

LOCATIONS = [
    {
        "name": "EVO Adamstuen",
        "key": "adamstuen",
        "id": "360e51d3-a434-4697-91c9-f956725108fc",
        "max_capacity": 35,
        "csv": os.path.join(BASE_DIR, "visitor_log.csv"),
        "historical": {
            "2026-02-23": {"06-10": 2407, "10-12": 2084, "12-15": 3317, "15-17": 3200, "17-20": 7122, "20-24": 3444},
            "2026-02-24": {"06-10": 3215, "10-12": 2488, "12-15": 2449, "15-17": 3292, "17-20": 7384, "20-24": 3653},
            "2026-02-25": {"06-10": 3555, "10-12": 2401, "12-15": 3347, "15-17": 3929, "17-20": 7168, "20-24": 2945},
            "2026-02-26": {"06-10": 3836, "10-12": 1769, "12-15": 2666, "15-17": 3698, "17-20": 5374, "20-24": 2858},
            "2026-02-27": {"06-10": 3392, "10-12": 2749, "12-15": 3762, "15-17": 3096, "17-20": 4444, "20-24": 2463},
            "2026-02-28": {"06-10": 2358, "10-12": 3864, "12-15": 4711, "15-17": 2719, "17-20": 3046, "20-24": 1695},
            "2026-03-01": {"06-10": 2285, "10-12": 2138, "12-15": 4800, "15-17": 2377, "17-20": 2526, "20-24": 1491},
            "2026-03-02": {"06-10": 2998, "10-12": 2258, "12-15": 3222, "15-17": 3394, "17-20": 7509, "20-24": 4610},
            "2026-03-03": {"06-10": 3086, "10-12": 2629, "12-15": 2720, "15-17": 3549, "17-20": 6064, "20-24": 3870},
            "2026-03-04": {"06-10": 3488, "10-12": 2269, "12-15": 3337, "15-17": 2635, "17-20": 7305, "20-24": 4221},
            "2026-03-05": {"06-10": 3670, "10-12": 1624, "12-15": 2647, "15-17": 2953, "17-20": 5414, "20-24": 3437},
            "2026-03-06": {"06-10": 3453, "10-12": 1989, "12-15": 3367, "15-17": 3132, "17-20": 4013, "20-24": 1495},
            "2026-03-07": {"06-10": 1991, "10-12": 3239, "12-15": 4342, "15-17": 1895, "17-20": 1895, "20-24": 1121},
            "2026-03-08": {"06-10": 2315, "10-12": 2243, "12-15": 4270, "15-17": 2528, "17-20": 2561, "20-24": 1805},
        },
        "evo_estimates": {
            "2026-03-09": {"15-17": 3297, "17-20": 7315.5, "20-24": 4027},
            "2026-03-10": {"06-10": 3150.5, "10-12": 2558.5, "12-15": 2584.5, "15-17": 3420.5, "17-20": 6724, "20-24": 3761.5},
            "2026-03-11": {"06-10": 3521.5, "10-12": 2335, "12-15": 3342, "15-17": 3282, "17-20": 7236.5, "20-24": 3583},
            "2026-03-12": {"06-10": 3753, "10-12": 1696.5, "12-15": 2656.5, "15-17": 3325.5, "17-20": 5394, "20-24": 3147.5},
            "2026-03-13": {"06-10": 3422.5, "10-12": 2369, "12-15": 3564.5, "15-17": 3114, "17-20": 4228.5, "20-24": 1979},
            "2026-03-14": {"06-10": 2174.5, "10-12": 3551.5, "12-15": 4526.5, "15-17": 2307, "17-20": 2470.5, "20-24": 1408},
            "2026-03-15": {"06-10": 2300, "10-12": 2190.5, "12-15": 4535, "15-17": 2452.5, "17-20": 2543.5, "20-24": 1648},
        },
    },
    {
        "name": "EVO Teisen",
        "key": "teisen",
        "id": "eebcd9b8-93f1-4b2d-9ab9-7b064d66ba3c",
        "max_capacity": 35,
        "csv": os.path.join(BASE_DIR, "visitor_log_teisen.csv"),
        "historical": {
            "2026-02-23": {"06-10": 1525, "10-12": 1514, "12-15": 2389, "15-17": 3011, "17-20": 5178, "20-24": 3223},
            "2026-02-24": {"06-10": 1888, "10-12": 1304, "12-15": 1711, "15-17": 3245, "17-20": 5673, "20-24": 3135},
            "2026-02-25": {"06-10": 1958, "10-12": 1052, "12-15": 2070, "15-17": 2964, "17-20": 5366, "20-24": 4314},
            "2026-02-26": {"06-10": 1388, "10-12": 1518, "12-15": 1887, "15-17": 3033, "17-20": 5636, "20-24": 3880},
            "2026-02-27": {"06-10": 2143, "10-12": 1558, "12-15": 2843, "15-17": 2633, "17-20": 3675, "20-24": 3062},
            "2026-02-28": {"06-10": 1620, "10-12": 2023, "12-15": 3015, "15-17": 1440, "17-20": 2270, "20-24": 2610},
            "2026-03-01": {"06-10": 1715, "10-12": 2338, "12-15": 4025, "15-17": 2191, "17-20": 2355, "20-24": 2222},
            "2026-03-02": {"06-10": 2121, "10-12": 1444, "12-15": 2569, "15-17": 2529, "17-20": 5148, "20-24": 4546},
            "2026-03-03": {"06-10": 2330, "10-12":  932, "12-15": 1944, "15-17": 2697, "17-20": 5131, "20-24": 4016},
            "2026-03-04": {"06-10": 2889, "10-12": 1380, "12-15": 1950, "15-17": 3718, "17-20": 3932, "20-24": 3433},
            "2026-03-05": {"06-10": 1882, "10-12": 1409, "12-15": 2020, "15-17": 2335, "17-20": 4562, "20-24": 2593},
            "2026-03-06": {"06-10": 1603, "10-12": 1206, "12-15": 2162, "15-17": 2485, "17-20": 3622, "20-24": 2098},
            "2026-03-07": {"06-10": 1082, "10-12": 1666, "12-15": 2922, "15-17": 2387, "17-20": 2108, "20-24": 1868},
            "2026-03-08": {"06-10":  889, "10-12": 1428, "12-15": 2652, "15-17": 1482, "17-20": 1430, "20-24": 1870},
        },
        "evo_estimates": {
            "2026-03-09": {"17-20": 5163, "20-24": 3884.5},
            "2026-03-10": {"06-10": 2109, "10-12": 1118, "12-15": 1827.5, "15-17": 2971, "17-20": 5402, "20-24": 3575.5},
            "2026-03-11": {"06-10": 2423.5, "10-12": 1216, "12-15": 2010, "15-17": 3341, "17-20": 4649, "20-24": 3873.5},
            "2026-03-12": {"06-10": 1635, "10-12": 1463.5, "12-15": 1953.5, "15-17": 2684, "17-20": 5099, "20-24": 3236.5},
            "2026-03-13": {"06-10": 1873, "10-12": 1382, "12-15": 2502.5, "15-17": 2559, "17-20": 3648.5, "20-24": 2580},
            "2026-03-14": {"06-10": 1351, "10-12": 1844.5, "12-15": 2968.5, "15-17": 1913.5, "17-20": 2189, "20-24": 2239},
            "2026-03-15": {"06-10": 1302, "10-12": 1883, "12-15": 3338.5, "15-17": 1836.5, "17-20": 1892.5, "20-24": 2046},
        },
    },
]

# ─── Processing functions (parameterized, not using globals) ──────────────────

def historical_to_timeseries(hist_data):
    points = []
    for date_str, intervals in sorted(hist_data.items()):
        y, m, d = map(int, date_str.split("-"))
        base = datetime(y, m, d)
        for iv_name, start_h, end_h in INTERVAL_SPEC:
            duration_min = (end_h - start_h) * 60
            onsite_min = intervals.get(iv_name, 0)
            avg_people = onsite_min / duration_min
            t_start = base + timedelta(hours=start_h)
            t_end = base + timedelta(hours=end_h, seconds=-1)
            points.append({"t": t_start.isoformat(), "v": round(avg_people, 1)})
            points.append({"t": t_end.isoformat(), "v": round(avg_people, 1)})
    return points


def build_evo_estimate_series(hist_data, evo_estimates):
    points = []
    sorted_dates = sorted(hist_data.keys())
    for date_str in sorted_dates:
        y, m, d = map(int, date_str.split("-"))
        target_dt = datetime(y, m, d)
        target_dow = target_dt.weekday()
        prior_same_dow = []
        for other_date in sorted_dates:
            if other_date >= date_str:
                break
            oy, om, od = map(int, other_date.split("-"))
            if datetime(oy, om, od).weekday() == target_dow:
                prior_same_dow.append(other_date)
        if not prior_same_dow:
            prior_all = [dd for dd in sorted_dates if dd < date_str]
            if not prior_all:
                continue
            for iv_name, start_h, end_h in INTERVAL_SPEC:
                duration_min = (end_h - start_h) * 60
                vals = [hist_data[pd].get(iv_name, 0) / duration_min for pd in prior_all]
                avg = sum(vals) / len(vals)
                t_s = target_dt + timedelta(hours=start_h)
                t_e = target_dt + timedelta(hours=end_h, seconds=-1)
                points.append({"t": t_s.isoformat(), "v": round(avg, 1)})
                points.append({"t": t_e.isoformat(), "v": round(avg, 1)})
        else:
            for iv_name, start_h, end_h in INTERVAL_SPEC:
                duration_min = (end_h - start_h) * 60
                vals = [hist_data[pd].get(iv_name, 0) / duration_min for pd in prior_same_dow]
                avg = sum(vals) / len(vals)
                t_s = target_dt + timedelta(hours=start_h)
                t_e = target_dt + timedelta(hours=end_h, seconds=-1)
                points.append({"t": t_s.isoformat(), "v": round(avg, 1)})
                points.append({"t": t_e.isoformat(), "v": round(avg, 1)})
    for date_str, intervals in sorted(evo_estimates.items()):
        y, m, d = map(int, date_str.split("-"))
        base = datetime(y, m, d)
        for iv_name, start_h, end_h in INTERVAL_SPEC:
            if iv_name not in intervals:
                continue
            duration_min = (end_h - start_h) * 60
            avg = intervals[iv_name] / duration_min
            t_s = base + timedelta(hours=start_h)
            t_e = base + timedelta(hours=end_h, seconds=-1)
            points.append({"t": t_s.isoformat(), "v": round(avg, 1)})
            points.append({"t": t_e.isoformat(), "v": round(avg, 1)})
    return points


def read_polling_csv(csv_path):
    points = []
    if not os.path.exists(csv_path):
        return points
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = row["timestamp"].strip()
                current = int(row["current"].strip())
                points.append({"t": ts.replace(" ", "T"), "v": current})
            except (ValueError, KeyError):
                continue
    return points


def build_prediction_model(hist_data, realtime_points):
    SLOT_COUNT = 288
    slots = {dow: {s: [] for s in range(SLOT_COUNT)} for dow in range(7)}
    now = datetime.now()
    for date_str, intervals in sorted(hist_data.items()):
        y, m, d = map(int, date_str.split("-"))
        dt = datetime(y, m, d)
        dow = dt.weekday()
        days_ago = (now - dt).days
        recency_weight = 0.5 * (0.5 ** (days_ago / 14.0))
        for iv_name, start_h, end_h in INTERVAL_SPEC:
            duration_min = (end_h - start_h) * 60
            avg_people = intervals.get(iv_name, 0) / duration_min
            for s in range(start_h * 12, end_h * 12):
                slots[dow][s].append((avg_people, recency_weight))
    for pt in realtime_points:
        dt = datetime.fromisoformat(pt["t"])
        dow = dt.weekday()
        slot = min(dt.hour * 12 + dt.minute // 5, SLOT_COUNT - 1)
        days_ago = (now - dt).total_seconds() / 86400.0
        recency_weight = 1.0 * (0.5 ** (days_ago / 14.0))
        slots[dow][slot].append((pt["v"], recency_weight))
    model = {}
    for dow in range(7):
        model[dow] = {}
        for s in range(SLOT_COUNT):
            entries = slots[dow][s]
            if not entries:
                continue
            total_w = sum(e[1] for e in entries)
            if total_w == 0:
                continue
            weighted_avg = sum(e[0] * e[1] for e in entries) / total_w
            if len(entries) > 1:
                variance = sum(e[1] * (e[0] - weighted_avg) ** 2 for e in entries) / total_w
                std = variance ** 0.5
            else:
                std = weighted_avg * 0.2
            model[dow][s] = {"avg": round(weighted_avg, 1), "std": round(std, 1), "n": len(entries)}
    for dow in range(7):
        filled = sorted(model[dow].keys())
        if not filled:
            continue
        for s in range(min(filled), max(filled) + 1):
            if s in model[dow]:
                continue
            prev_s = max((fs for fs in filled if fs < s), default=None)
            next_s = min((fs for fs in filled if fs > s), default=None)
            if prev_s is not None and next_s is not None:
                frac = (s - prev_s) / (next_s - prev_s)
                a = model[dow][prev_s]["avg"] * (1 - frac) + model[dow][next_s]["avg"] * frac
                st = model[dow][prev_s]["std"] * (1 - frac) + model[dow][next_s]["std"] * frac
                model[dow][s] = {"avg": round(a, 1), "std": round(st, 1), "n": 0}
            elif prev_s is not None:
                model[dow][s] = dict(model[dow][prev_s])
            elif next_s is not None:
                model[dow][s] = dict(model[dow][next_s])
    return model


def generate_predictions(model, days=7):
    now = datetime.now().replace(second=0, microsecond=0)
    now = now.replace(minute=(now.minute // 5) * 5)
    predictions, upper_band, lower_band = [], [], []
    t = now
    end = now + timedelta(days=days)
    while t <= end:
        dow = t.weekday()
        slot = t.hour * 12 + t.minute // 5
        if slot < 288 and slot in model.get(dow, {}):
            entry = model[dow][slot]
            avg, std = entry["avg"], entry["std"]
            if t.hour < GYM_OPEN_HOUR:
                avg, std = 0, 0
            predictions.append({"t": t.isoformat(), "v": round(max(0, avg), 1)})
            upper_band.append({"t": t.isoformat(), "v": round(max(0, min(avg + std, 50)), 1)})
            lower_band.append({"t": t.isoformat(), "v": round(max(0, avg - std), 1)})
        else:
            v = 0 if t.hour < GYM_OPEN_HOUR else None
            predictions.append({"t": t.isoformat(), "v": v})
            upper_band.append({"t": t.isoformat(), "v": v})
            lower_band.append({"t": t.isoformat(), "v": v})
        t += timedelta(minutes=5)
    return predictions, upper_band, lower_band


def build_model_snapshot_data(hist_data, realtime_points):
    all_readings = []
    for date_str, intervals in sorted(hist_data.items()):
        y, m, d = map(int, date_str.split("-"))
        dt = datetime(y, m, d)
        dow = dt.weekday()
        for iv_name, start_h, end_h in INTERVAL_SPEC:
            duration_min = (end_h - start_h) * 60
            avg_people = intervals.get(iv_name, 0) / duration_min
            mid_h = (start_h + end_h) / 2
            mid_dt = dt + timedelta(hours=mid_h)
            all_readings.append({
                "t": mid_dt.isoformat(), "ts": int(mid_dt.timestamp() * 1000),
                "v": round(avg_people, 1), "dow": dow, "slot": int(mid_h * 12),
                "w": 0.5, "type": "historical"
            })
    for pt in realtime_points:
        dt = datetime.fromisoformat(pt["t"])
        dow = dt.weekday()
        slot = min(dt.hour * 12 + dt.minute // 5, 287)
        all_readings.append({
            "t": dt.isoformat(), "ts": int(dt.timestamp() * 1000),
            "v": pt["v"], "dow": dow, "slot": slot,
            "w": 1.0, "type": "realtime"
        })
    return all_readings


def process_location(loc):
    """Process one location and return all its data series."""
    hist = historical_to_timeseries(loc["historical"])
    evo_est = build_evo_estimate_series(loc["historical"], loc["evo_estimates"])
    rt = read_polling_csv(loc["csv"])
    model = build_prediction_model(loc["historical"], rt)
    pred, upper, lower = generate_predictions(model, PREDICTION_DAYS)
    snap = build_model_snapshot_data(loc["historical"], rt)
    return {
        "name": loc["name"], "key": loc["key"], "max_capacity": loc["max_capacity"],
        "historical": hist, "evo_estimate": evo_est, "realtime": rt,
        "prediction": pred, "upper": upper, "lower": lower, "snapshot": snap,
    }


# ─── HTML generation ─────────────────────────────────────────────────────────

def generate_html(all_loc_data):
    now_str = datetime.now().strftime('%d.%m.%Y kl %H:%M')

    # Build tab buttons and per-location JSON data
    tab_buttons = ""
    for i, ld in enumerate(all_loc_data):
        active = ' active' if i == 0 else ''
        tab_buttons += f'<button class="tab-btn{active}" onclick="switchTab(\'{ld["key"]}\')">{ld["name"]}</button>\n    '

    # Serialize all location data into a JS object
    loc_data_js = {}
    for ld in all_loc_data:
        loc_data_js[ld["key"]] = {
            "name": ld["name"],
            "maxCapacity": ld["max_capacity"],
            "historical": ld["historical"],
            "evoEstimate": ld["evo_estimate"],
            "realtime": ld["realtime"],
            "prediction": ld["prediction"],
            "upper": ld["upper"],
            "lower": ld["lower"],
            "snapshot": ld["snapshot"],
        }

    first_key = all_loc_data[0]["key"]

    html = f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EVO Besøksdata</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #1a1a2e;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    overflow-x: hidden;
  }}
  #header {{
    padding: 16px 30px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  #header h1 {{ font-size: 22px; color: #ff6b6b; }}
  #header .subtitle {{ font-size: 13px; color: #888; }}
  #tabs {{
    padding: 0 30px;
    display: flex;
    gap: 0;
    border-bottom: 2px solid #2a2a4a;
  }}
  .tab-btn {{
    padding: 10px 24px;
    background: transparent;
    color: #888;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .tab-btn:hover {{ color: #ccc; background: rgba(255,255,255,0.03); }}
  .tab-btn.active {{
    color: #ff6b6b;
    border-bottom-color: #ff6b6b;
  }}
  #chart {{
    width: 100%;
    height: calc(100vh - 150px);
    min-height: 450px;
  }}
  #info-bar {{
    padding: 6px 30px;
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
    font-size: 12px;
    color: #aaa;
    background: #16213e;
    border-top: 1px solid #2a2a4a;
  }}
  #info-bar .legend-item {{ display: flex; align-items: center; gap: 5px; }}
  #info-bar .dot {{ width: 14px; height: 4px; border-radius: 2px; }}
  #backtest-info {{
    display: none;
    padding: 8px 30px;
    background: #1e2a45;
    color: #f0a500;
    font-size: 13px;
    border-top: 1px solid #2a2a4a;
  }}
  #backtest-info button {{
    margin-left: 12px;
    background: #333;
    color: #fff;
    border: 1px solid #555;
    padding: 2px 10px;
    border-radius: 3px;
    cursor: pointer;
  }}
</style>
</head>
<body>

<div id="header">
  <h1>EVO Besøksdata</h1>
  <span class="subtitle">Generert: {now_str}</span>
</div>

<div id="tabs">
    {tab_buttons}
</div>

<div id="info-bar">
  <div class="legend-item"><div class="dot" style="background:#5e7fa8"></div> Historisk faktisk</div>
  <div class="legend-item"><div class="dot" style="background:#f0a500;opacity:.6"></div> Evo estimat</div>
  <div class="legend-item"><div class="dot" style="background:#ff6b6b"></div> Sanntid (5-min)</div>
  <div class="legend-item"><div class="dot" style="background:#4ecdc4"></div> Mitt estimat</div>
  <div class="legend-item" style="color:#777">Klikk sanntidspunkt for tilbake-test</div>
</div>

<div id="backtest-info">
  <span id="backtest-text"></span>
  <button onclick="clearBacktest()">Fjern</button>
</div>

<div id="chart"></div>

<script>
const ALL_DATA = {json.dumps(loc_data_js)};
const GYM_OPEN = {GYM_OPEN_HOUR};
const GYM_CLOSE = {GYM_CLOSE_HOUR};
let currentKey = '{first_key}';
let originalTraceCount = 0;

// ─── Prediction engine (client-side, for backtesting) ────────────────────────
function predictFrom(clickedTimestamp, snapshot) {{
  const cutoff = clickedTimestamp;
  const available = snapshot.filter(r => r.ts <= cutoff);
  if (!available.length) return null;
  const slots = {{}};
  for (let dow = 0; dow < 7; dow++) slots[dow] = {{}};
  available.forEach(r => {{
    const daysAgo = (cutoff - r.ts) / (1000 * 86400);
    const recencyW = r.w * Math.pow(0.5, daysAgo / 14.0);
    const dow = r.dow;
    if (r.type === 'historical') {{
      for (let s = Math.max(0, r.slot - 12); s < Math.min(288, r.slot + 12); s++) {{
        if (!slots[dow][s]) slots[dow][s] = {{tw: 0, twv: 0}};
        slots[dow][s].tw += recencyW;
        slots[dow][s].twv += r.v * recencyW;
      }}
    }} else {{
      const slot = r.slot;
      if (!slots[dow][slot]) slots[dow][slot] = {{tw: 0, twv: 0}};
      slots[dow][slot].tw += recencyW;
      slots[dow][slot].twv += r.v * recencyW;
      for (let ds = -2; ds <= 2; ds++) {{
        if (ds === 0) continue;
        const ns = slot + ds;
        if (ns < 0 || ns >= 288) continue;
        const nw = recencyW * (1 - Math.abs(ds) * 0.3);
        if (!slots[dow][ns]) slots[dow][ns] = {{tw: 0, twv: 0}};
        slots[dow][ns].tw += nw;
        slots[dow][ns].twv += r.v * nw;
      }}
    }}
  }});
  const preds = [];
  let t = new Date(cutoff); t.setSeconds(0,0);
  t.setMinutes(Math.floor(t.getMinutes()/5)*5);
  const end = new Date(t.getTime() + 7*24*3600*1000);
  while (t <= end) {{
    const dow = t.getDay() === 0 ? 6 : t.getDay() - 1;
    const slot = t.getHours()*12 + Math.floor(t.getMinutes()/5);
    if (t.getHours() < GYM_OPEN) {{
      preds.push({{t: t.toISOString(), v: 0}});
    }} else if (slots[dow][slot] && slots[dow][slot].tw > 0) {{
      preds.push({{t: t.toISOString(), v: Math.round(Math.max(0, slots[dow][slot].twv / slots[dow][slot].tw)*10)/10}});
    }} else {{
      preds.push({{t: t.toISOString(), v: null}});
    }}
    t = new Date(t.getTime() + 5*60*1000);
  }}
  return preds;
}}

// ─── Render chart for a location ─────────────────────────────────────────────
function renderChart(key) {{
  const D = ALL_DATA[key];
  const MC = D.maxCapacity;

  const traceHist = {{
    x: D.historical.map(d=>d.t), y: D.historical.map(d=>d.v),
    type:'scatter', mode:'lines', name:'Historisk faktisk',
    line:{{color:'#5e7fa8',width:1.5,shape:'hv'}}, opacity:0.7,
    hovertemplate:'%{{x|%a %d.%m kl %H:%M}}<br>Snitt: %{{y:.0f}} pers<extra>Historisk</extra>'
  }};
  const traceEvo = {{
    x: D.evoEstimate.map(d=>d.t), y: D.evoEstimate.map(d=>d.v),
    type:'scatter', mode:'lines', name:'Evo estimat',
    line:{{color:'#f0a500',width:1.5,shape:'hv',dash:'dot'}}, opacity:0.6,
    hovertemplate:'%{{x|%a %d.%m kl %H:%M}}<br>Evo: %{{y:.0f}} pers<extra>Evo estimat</extra>'
  }};
  const traceRT = {{
    x: D.realtime.map(d=>d.t), y: D.realtime.map(d=>d.v),
    type:'scatter', mode:'lines+markers', name:'Sanntid (5 min)',
    line:{{color:'#ff6b6b',width:2}}, marker:{{size:4,color:'#ff6b6b'}},
    hovertemplate:'%{{x|%a %d.%m kl %H:%M}}<br>Besøkende: %{{y:.0f}}<extra>Sanntid</extra>'
  }};
  const traceUpper = {{
    x: D.upper.map(d=>d.t), y: D.upper.map(d=>d.v),
    type:'scatter', mode:'lines', name:'Øvre',
    line:{{color:'#4ecdc4',width:0}}, showlegend:false, hoverinfo:'skip'
  }};
  const traceLower = {{
    x: D.lower.map(d=>d.t), y: D.lower.map(d=>d.v),
    type:'scatter', mode:'lines', name:'Nedre',
    line:{{color:'#4ecdc4',width:0}}, fill:'tonexty',
    fillcolor:'rgba(78,205,196,0.1)', showlegend:false, hoverinfo:'skip'
  }};
  const tracePred = {{
    x: D.prediction.map(d=>d.t), y: D.prediction.map(d=>d.v),
    type:'scatter', mode:'lines', name:'Mitt estimat',
    line:{{color:'#4ecdc4',width:2,dash:'dot'}},
    hovertemplate:'%{{x|%a %d.%m kl %H:%M}}<br>Estimat: %{{y:.0f}} pers<extra>Mitt estimat</extra>'
  }};

  const firstT = D.historical.length ? D.historical[0].t : D.prediction[0].t;
  const lastT = D.prediction.length ? D.prediction[D.prediction.length-1].t : D.historical[D.historical.length-1].t;

  const traceCap = {{
    x: [firstT, lastT], y: [MC, MC],
    type:'scatter', mode:'lines', name:'Kapasitet ('+MC+')',
    line:{{color:'#ff4444',width:1,dash:'dash'}}, opacity:0.4, hoverinfo:'skip'
  }};

  const traces = [traceCap, traceEvo, traceHist, traceUpper, traceLower, tracePred, traceRT];
  originalTraceCount = traces.length;

  let ds, de;
  if (D.realtime.length) {{
    const fr = new Date(D.realtime[0].t);
    ds = new Date(fr.getTime() - 2*86400000).toISOString();
    de = lastT;
  }} else {{
    ds = firstT; de = lastT;
  }}

  const layout = {{
    paper_bgcolor:'#1a1a2e', plot_bgcolor:'#16213e',
    font:{{color:'#e0e0e0',family:'-apple-system,BlinkMacSystemFont,sans-serif'}},
    margin:{{l:55,r:25,t:10,b:45}},
    xaxis:{{
      type:'date', range:[ds,de],
      rangeslider:{{visible:true, bgcolor:'#0f1629', bordercolor:'#2a2a4a', range:[firstT,lastT], thickness:0.08}},
      gridcolor:'#2a2a4a', tickformat:'%a %d.%m\\n%H:%M', tickfont:{{size:11}}, dtick:86400000
    }},
    yaxis:{{
      title:'Antall besøkende', titlefont:{{size:13}},
      gridcolor:'#2a2a4a', range:[0,55], zeroline:false
    }},
    legend:{{x:0.01,y:0.99,bgcolor:'rgba(22,33,62,0.8)',bordercolor:'#2a2a4a',borderwidth:1,font:{{size:11}}}},
    hovermode:'x unified', dragmode:'zoom'
  }};

  Plotly.newPlot('chart', traces, layout, {{
    responsive:true, scrollZoom:true, displayModeBar:true,
    modeBarButtonsToRemove:['lasso2d','select2d'], displaylogo:false
  }});

  // Click handler for backtest
  document.getElementById('chart').on('plotly_click', function(ev) {{
    const pt = ev.points[0];
    if (pt.curveNumber !== traces.indexOf(traceRT)) return;
    const clickT = new Date(pt.x).getTime();
    const preds = predictFrom(clickT, ALL_DATA[currentKey].snapshot);
    if (!preds) return;
    const valid = preds.filter(p => p.v !== null);
    const label = new Date(pt.x).toLocaleString('no-NO',{{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}});
    clearBacktest();
    Plotly.addTraces('chart', {{
      x:valid.map(d=>d.t), y:valid.map(d=>d.v), type:'scatter', mode:'lines',
      name:'Tilbake-test fra '+label, line:{{color:'#f0a500',width:2,dash:'dash'}},
      hovertemplate:'%{{x|%a %d.%m kl %H:%M}}<br>Estimat: %{{y:.0f}} pers<extra>Tilbake-test</extra>'
    }});
    Plotly.addTraces('chart', {{
      x:[pt.x], y:[pt.y], type:'scatter', mode:'markers', name:'Klikket',
      marker:{{size:14,color:'#f0a500',symbol:'star',line:{{width:2,color:'#fff'}}}},
      showlegend:false, hoverinfo:'skip'
    }});
    document.getElementById('backtest-info').style.display='block';
    document.getElementById('backtest-text').textContent=
      'Tilbake-test fra '+label+' ('+pt.y+' pers) — estimat fra det tidspunktet';
  }});
}}

function clearBacktest() {{
  const el = document.getElementById('chart');
  while (el.data && el.data.length > originalTraceCount)
    Plotly.deleteTraces('chart', el.data.length-1);
  document.getElementById('backtest-info').style.display='none';
}}

function switchTab(key) {{
  currentKey = key;
  document.querySelectorAll('.tab-btn').forEach(b => {{
    b.classList.toggle('active', b.textContent === ALL_DATA[key].name);
  }});
  clearBacktest();
  renderChart(key);
}}

document.addEventListener('keydown', e => {{ if (e.key==='Escape') clearBacktest(); }});

// Initial render
renderChart('{first_key}');
</script>
</body>
</html>"""
    return html


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    all_loc_data = []
    for loc in LOCATIONS:
        print(f"\nProsesserer {loc['name']}...")
        data = process_location(loc)
        print(f"  Historisk: {len(data['historical'])} pkt, Evo-est: {len(data['evo_estimate'])} pkt")
        print(f"  Sanntid: {len(data['realtime'])} pkt, Prediksjon: {len(data['prediction'])} pkt")
        all_loc_data.append(data)

    print(f"\nGenererer {OUTPUT_FILE}...")
    html = generate_html(all_loc_data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"Ferdig! {OUTPUT_FILE} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
