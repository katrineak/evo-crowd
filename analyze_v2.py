#!/usr/bin/env python3
"""
EVO Adamstuen - Forbedret besøksanalyse.
Bygger mer realistiske estimater ved å bruke maksverdier og trenddata
i stedet for bare gjennomsnitt.
"""
from datetime import date

# Historical actual data - onsiteMinutes per interval
historical_data = {
    "2026-02-23": {"06-10": 2407, "10-12": 2084, "12-15": 3317, "15-17": 3200, "17-20": 7122, "20-24": 3444},  # Mon
    "2026-02-24": {"06-10": 3215, "10-12": 2488, "12-15": 2449, "15-17": 3292, "17-20": 7384, "20-24": 3653},  # Tue
    "2026-02-25": {"06-10": 3555, "10-12": 2401, "12-15": 3347, "15-17": 3929, "17-20": 7168, "20-24": 2945},  # Wed
    "2026-02-26": {"06-10": 3836, "10-12": 1769, "12-15": 2666, "15-17": 3698, "17-20": 5374, "20-24": 2858},  # Thu
    "2026-02-27": {"06-10": 3392, "10-12": 2749, "12-15": 3762, "15-17": 3096, "17-20": 4444, "20-24": 2463},  # Fri
    "2026-02-28": {"06-10": 2358, "10-12": 3864, "12-15": 4711, "15-17": 2719, "17-20": 3046, "20-24": 1695},  # Sat
    "2026-03-01": {"06-10": 2285, "10-12": 2138, "12-15": 4800, "15-17": 2377, "17-20": 2526, "20-24": 1491},  # Sun
    "2026-03-02": {"06-10": 2998, "10-12": 2258, "12-15": 3222, "15-17": 3394, "17-20": 7509, "20-24": 4610},  # Mon
    "2026-03-03": {"06-10": 3086, "10-12": 2629, "12-15": 2720, "15-17": 3549, "17-20": 6064, "20-24": 3870},  # Tue
    "2026-03-04": {"06-10": 3488, "10-12": 2269, "12-15": 3337, "15-17": 2635, "17-20": 7305, "20-24": 4221},  # Wed
    "2026-03-05": {"06-10": 3670, "10-12": 1624, "12-15": 2647, "15-17": 2953, "17-20": 5414, "20-24": 3437},  # Thu
    "2026-03-06": {"06-10": 3453, "10-12": 1989, "12-15": 3367, "15-17": 3132, "17-20": 4013, "20-24": 1495},  # Fri
    "2026-03-07": {"06-10": 1991, "10-12": 3239, "12-15": 4342, "15-17": 1895, "17-20": 1895, "20-24": 1121},  # Sat
    "2026-03-08": {"06-10": 2315, "10-12": 2243, "12-15": 4270, "15-17": 2528, "17-20": 2561, "20-24": 1805},  # Sun
}

interval_durations = {"06-10": 240, "10-12": 120, "12-15": 180, "15-17": 120, "17-20": 180, "20-24": 240}
intervals = ["06-10", "10-12", "12-15", "15-17", "17-20", "20-24"]
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_names_no = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]

def to_people(onsite_min, interval):
    """Convert onsiteMinutes to average number of people in that interval."""
    return onsite_min / interval_durations[interval]

def day_of_week(date_str):
    y, m, d = map(int, date_str.split("-"))
    return date(y, m, d).strftime("%A")

# Group by day of week
by_dow = {d: [] for d in day_names}
for date_str, data in historical_data.items():
    dow = day_of_week(date_str)
    by_dow[dow].append((date_str, data))

print("=" * 80)
print("  EVO ADAMSTUEN - FORBEDRET BESØKSESTIMAT")
print("  Basert på faktiske data 23. feb - 8. mars 2026")
print("=" * 80)

# ===== Section 1: Why Evo underestimates =====
print("\n")
print("HVORFOR EVO UNDERESTIMERER:")
print("-" * 80)
print("""
Evo beregner gjennomsnittet fra de siste 14 dagene per ukedag. Dette gir
systematiske avvik fordi:

1. GJENNOMSNITT vs. TOPP: Intervallet «17-20» viser snitt over 3 timer.
   Faktisk antall på det travleste tidspunktet (f.eks. kl 18:00) kan
   være 30-50% høyere enn gjennomsnittet for hele intervallet.

2. DAG-TIL-DAG VARIASJON: Med bare 2 datapunkter per ukedag gir
   gjennomsnittet et usikkert estimat. Den travligste av de to dagene
   kan ha 20-40% flere enn snittet.

3. VOKSENDE TREND: Mandager økte 11% fra uke 1 til uke 2.
""")

# ===== Section 2: Improved estimates =====
print("\nFORBEDREDE ESTIMATER FOR 10-15 MARS 2026")
print("(Gjennomsnittlig antall personer i intervallet)")
print("=" * 80)
print()

future_dates = {
    "2026-03-10": "Tuesday",
    "2026-03-11": "Wednesday",
    "2026-03-12": "Thursday",
    "2026-03-13": "Friday",
    "2026-03-14": "Saturday",
    "2026-03-15": "Sunday",
}

for date_str, dow in future_dates.items():
    dow_i = day_names.index(dow)
    entries = by_dow[dow]

    print(f"  {day_names_no[dow_i].upper()} {date_str}")
    print(f"  {'Tidsrom':<12} {'Evo est.':>10} {'Mitt est.':>10} {'Realistisk':>12}  Kommentar")
    print(f"  {'-'*68}")

    for iv in intervals:
        vals = [to_people(e[1][iv], iv) for e in entries]
        evo_avg = sum(vals) / len(vals)
        high = max(vals)

        # Use the higher of the two observed values as base,
        # since with only 2 data points, the max is a better
        # predictor when user says it underestimates
        my_est = high

        # "Realistisk topp" = what you'll likely see at the busiest
        # moment within the interval (~20-30% above interval average)
        realistic_peak = my_est * 1.25
        realistic_peak = min(realistic_peak, 45)  # physical space limit

        comment = ""
        if realistic_peak >= 35:
            comment = "VELDIG FULLT"
        elif realistic_peak >= 25:
            comment = "Travelt"
        elif realistic_peak >= 15:
            comment = "Moderat"
        else:
            comment = "Rolig"

        print(f"  kl {iv:<8} {evo_avg:>9.0f}p  {my_est:>9.0f}p  {realistic_peak:>9.0f}p   {comment}")

    print()


# ===== Section 3: Practical recommendations =====
print("\n" + "=" * 80)
print("  PRAKTISKE ANBEFALINGER")
print("=" * 80)

print("""
  BESTE TRENINGSTIDER (roligst):
  ┌──────────────┬────────────────────────────────────────┐
  │ Hverdager    │ kl 06-10 (10-15 pers) eller           │
  │              │ kl 20-24 (13-17 pers)                  │
  ├──────────────┼────────────────────────────────────────┤
  │ Lørdag       │ kl 06-10 (9 pers) eller               │
  │              │ kl 20-24 (6 pers)                      │
  ├──────────────┼────────────────────────────────────────┤
  │ Søndag       │ kl 06-10 (10 pers) eller              │
  │              │ kl 20-24 (7 pers)                      │
  └──────────────┴────────────────────────────────────────┘

  UNNGÅ:
  - Man/Ons kl 17-20: Gjennomsnitt 40+ pers, topp opptil 50+!
  - Tirsdag kl 17-20: Gjennomsnitt 37 pers, topp opptil 47
  - Lørdag kl 10-12: Gjennomsnitt 30 pers, topp opptil 37
""")

# ===== Section 4: Day-by-day detail with variance =====
print("\nDETALJERT DATA PER UKEDAG (siste 2 uker)")
print("=" * 80)

for i, dow in enumerate(day_names):
    entries = by_dow[dow]
    if not entries:
        continue

    print(f"\n  {day_names_no[i]} ({entries[0][0]} og {entries[1][0]})")
    print(f"  {'Tidsrom':<12} {'Uke 1':>8} {'Uke 2':>8} {'Snitt':>8} {'Maks':>8} {'Endring':>9}")
    print(f"  {'-'*56}")

    for iv in intervals:
        v1 = to_people(entries[0][1][iv], iv)
        v2 = to_people(entries[1][1][iv], iv)
        avg = (v1 + v2) / 2
        mx = max(v1, v2)
        pct = ((v2 - v1) / v1) * 100 if v1 > 0 else 0
        sign = "+" if pct > 0 else ""
        print(f"  kl {iv:<8} {v1:>7.0f}p {v2:>7.0f}p {avg:>7.0f}p {mx:>7.0f}p {sign}{pct:>7.0f}%")


# ===== Section 5: Summary table for fridge =====
print("\n\n" + "=" * 80)
print("  OPPSUMMERINGSTABELL - FORVENTET ANTALL BESØKENDE")
print("  (Mitt beste estimat - høyere enn Evo)")
print("=" * 80)
print()
header = f"  {'':>12}"
for iv in intervals:
    header += f"  {'kl '+iv:>7}"
print(header)
print(f"  {'-'*60}")

for date_str, dow in future_dates.items():
    dow_i = day_names.index(dow)
    entries = by_dow[dow]
    row = f"  {day_names_no[dow_i]:<12}"
    for iv in intervals:
        vals = [to_people(e[1][iv], iv) for e in entries]
        est = max(vals)
        row += f"  {est:>7.0f}"
    print(row)

print()
print("  Tallene over er konservativt høye estimater (maks av de to siste")
print("  observerte verdiene for tilsvarende ukedag). På det travleste")
print("  tidspunktet innenfor hvert intervall kan det reelle antallet")
print("  være ~25% høyere enn disse tallene.")
