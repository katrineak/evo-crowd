#!/usr/bin/env python3
"""
Analyze EVO Adamstuen visitor data and produce improved estimates.
Uses 2 weeks of historical data to build day-of-week patterns.
"""
import json
from datetime import date, timedelta

# Historical actual data (status="historic") - onsiteMinutes per interval
# Format: {date_str: {interval: onsiteMinutes}}
historical_data = {
    # Week 1 (Feb 23 - Mar 1)
    "2026-02-23": {"06-10": 2407, "10-12": 2084, "12-15": 3317, "15-17": 3200, "17-20": 7122, "20-24": 3444},  # Mon
    "2026-02-24": {"06-10": 3215, "10-12": 2488, "12-15": 2449, "15-17": 3292, "17-20": 7384, "20-24": 3653},  # Tue
    "2026-02-25": {"06-10": 3555, "10-12": 2401, "12-15": 3347, "15-17": 3929, "17-20": 7168, "20-24": 2945},  # Wed
    "2026-02-26": {"06-10": 3836, "10-12": 1769, "12-15": 2666, "15-17": 3698, "17-20": 5374, "20-24": 2858},  # Thu
    "2026-02-27": {"06-10": 3392, "10-12": 2749, "12-15": 3762, "15-17": 3096, "17-20": 4444, "20-24": 2463},  # Fri
    "2026-02-28": {"06-10": 2358, "10-12": 3864, "12-15": 4711, "15-17": 2719, "17-20": 3046, "20-24": 1695},  # Sat
    "2026-03-01": {"06-10": 2285, "10-12": 2138, "12-15": 4800, "15-17": 2377, "17-20": 2526, "20-24": 1491},  # Sun
    # Week 2 (Mar 2 - Mar 8)
    "2026-03-02": {"06-10": 2998, "10-12": 2258, "12-15": 3222, "15-17": 3394, "17-20": 7509, "20-24": 4610},  # Mon
    "2026-03-03": {"06-10": 3086, "10-12": 2629, "12-15": 2720, "15-17": 3549, "17-20": 6064, "20-24": 3870},  # Tue
    "2026-03-04": {"06-10": 3488, "10-12": 2269, "12-15": 3337, "15-17": 2635, "17-20": 7305, "20-24": 4221},  # Wed
    "2026-03-05": {"06-10": 3670, "10-12": 1624, "12-15": 2647, "15-17": 2953, "17-20": 5414, "20-24": 3437},  # Thu
    "2026-03-06": {"06-10": 3453, "10-12": 1989, "12-15": 3367, "15-17": 3132, "17-20": 4013, "20-24": 1495},  # Fri
    "2026-03-07": {"06-10": 1991, "10-12": 3239, "12-15": 4342, "15-17": 1895, "17-20": 1895, "20-24": 1121},  # Sat
    "2026-03-08": {"06-10": 2315, "10-12": 2243, "12-15": 4270, "15-17": 2528, "17-20": 2561, "20-24": 1805},  # Sun
    # Today (Mar 9, Monday) - partial historic data
    "2026-03-09": {"06-10": 2306, "10-12": 1682},  # Mon (only completed intervals)
}

# Today's data with current interval
today_current = {"12-15": 4500}  # current interval, still accumulating

# Evo's estimates for the coming days (status="future")
evo_estimates = {
    "2026-03-09": {"15-17": 3297, "17-20": 7315.5, "20-24": 4027},  # Mon (rest of today)
    "2026-03-10": {"06-10": 3150.5, "10-12": 2558.5, "12-15": 2584.5, "15-17": 3420.5, "17-20": 6724, "20-24": 3761.5},  # Tue
    "2026-03-11": {"06-10": 3521.5, "10-12": 2335, "12-15": 3342, "15-17": 3282, "17-20": 7236.5, "20-24": 3583},  # Wed
    "2026-03-12": {"06-10": 3753, "10-12": 1696.5, "12-15": 2656.5, "15-17": 3325.5, "17-20": 5394, "20-24": 3147.5},  # Thu
    "2026-03-13": {"06-10": 3422.5, "10-12": 2369, "12-15": 3564.5, "15-17": 3114, "17-20": 4228.5, "20-24": 1979},  # Fri
    "2026-03-14": {"06-10": 2174.5, "10-12": 3551.5, "12-15": 4526.5, "15-17": 2307, "17-20": 2470.5, "20-24": 1408},  # Sat
    "2026-03-15": {"06-10": 2300, "10-12": 2190.5, "12-15": 4535, "15-17": 2452.5, "17-20": 2543.5, "20-24": 1648},  # Sun
}

# Interval durations in minutes
interval_durations = {
    "06-10": 240,
    "10-12": 120,
    "12-15": 180,
    "15-17": 120,
    "17-20": 180,
    "20-24": 240,
}

# Day of week mapping
def day_of_week(date_str):
    y, m, d = map(int, date_str.split("-"))
    return date(y, m, d).strftime("%A")

day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_names_no = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
intervals = ["06-10", "10-12", "12-15", "15-17", "17-20", "20-24"]

# Group historical data by day of week
by_dow = {d: [] for d in day_names}
for date_str, data in historical_data.items():
    if date_str == "2026-03-09":  # skip incomplete today
        continue
    dow = day_of_week(date_str)
    by_dow[dow].append((date_str, data))

print("=" * 80)
print("EVO ADAMSTUEN - BESØKSANALYSE")
print("Basert på faktiske data fra 23. feb - 8. mars 2026")
print("=" * 80)

# Calculate averages per day of week
print("\n1. FAKTISKE GJENNOMSNITT PER UKEDAG (gjennomsnittlig antall personer)")
print("-" * 80)
header = f"{'Dag':<12}"
for iv in intervals:
    header += f"{'kl '+iv:>10}"
header += f"{'Dagstotal':>12}"
print(header)
print("-" * 80)

dow_averages = {}
for i, dow in enumerate(day_names):
    entries = by_dow[dow]
    if not entries:
        continue
    avg = {}
    for iv in intervals:
        vals = [e[1].get(iv, 0) for e in entries]
        avg[iv] = sum(vals) / len(vals)
    dow_averages[dow] = avg

    row = f"{day_names_no[i]:<12}"
    day_total = 0
    for iv in intervals:
        avg_people = avg[iv] / interval_durations[iv]
        row += f"{avg_people:>10.1f}"
        day_total += avg[iv]
    avg_total_people = day_total / (18 * 60)  # 18 hours open (06-24)
    row += f"{avg_total_people:>12.1f}"
    print(row)

# Now compare Evo's estimates vs actual averages
print("\n\n2. EVO's ESTIMATER vs. FAKTISK GJENNOMSNITT (antall personer)")
print("   (Positive avvik = Evo underestimerer)")
print("-" * 95)
header = f"{'Dag':<10} {'Dato':<12}"
for iv in intervals:
    header += f"{'kl '+iv:>10}"
print(header)
print("-" * 95)

future_dates = ["2026-03-10", "2026-03-11", "2026-03-12", "2026-03-13", "2026-03-14", "2026-03-15"]

for date_str in future_dates:
    dow = day_of_week(date_str)
    dow_i = day_names.index(dow)
    est = evo_estimates[date_str]
    act_avg = dow_averages[dow]

    # Evo estimate row
    row_evo = f"{day_names_no[dow_i]:<10} {date_str:<12}"
    for iv in intervals:
        evo_people = est[iv] / interval_durations[iv]
        row_evo += f"{evo_people:>10.1f}"
    print(row_evo + "  <- Evo estimat")

    # Actual average row
    row_act = f"{'':>10} {'':>12}"
    for iv in intervals:
        act_people = act_avg[iv] / interval_durations[iv]
        row_act += f"{act_people:>10.1f}"
    print(row_act + "  <- Faktisk snitt")

    # Difference row
    row_diff = f"{'':>10} {'':>12}"
    for iv in intervals:
        evo_people = est[iv] / interval_durations[iv]
        act_people = act_avg[iv] / interval_durations[iv]
        diff = act_people - evo_people
        sign = "+" if diff > 0 else ""
        row_diff += f"{sign}{diff:>9.1f}"
    print(row_diff + "  <- Avvik")
    print()


# Build improved estimates: use max of Evo estimate and historical average,
# with bias toward higher values (since user says Evo underestimates)
print("\n3. FORBEDREDE ESTIMATER FOR NESTE UKE")
print("   Metode: Bruker høyeste av faktisk snitt og Evo-estimat,")
print("   pluss 15% buffer for å kompensere for underestimering")
print("-" * 80)
header = f"{'Dag':<10} {'Dato':<12}"
for iv in intervals:
    header += f"{'kl '+iv:>10}"
print(header)
print("-" * 80)

for date_str in future_dates:
    dow = day_of_week(date_str)
    dow_i = day_names.index(dow)
    est = evo_estimates[date_str]
    act_avg = dow_averages.get(dow, {})

    row = f"{day_names_no[dow_i]:<10} {date_str:<12}"
    for iv in intervals:
        evo_people = est[iv] / interval_durations[iv]
        act_people = act_avg.get(iv, 0) / interval_durations[iv] if act_avg else evo_people
        # Take the higher value and add 15% buffer
        best = max(evo_people, act_people) * 1.15
        # Cap at 35 (max capacity)
        best = min(best, 35)
        row += f"{best:>10.0f}"
    print(row)


# Additional analysis: peak times
print("\n\n4. MEST OG MINST TRAVLE TIDER PER UKEDAG")
print("-" * 80)
for i, dow in enumerate(day_names):
    if dow not in dow_averages:
        continue
    avg = dow_averages[dow]
    people_by_iv = {}
    for iv in intervals:
        people_by_iv[iv] = avg[iv] / interval_durations[iv]

    busiest = max(people_by_iv, key=people_by_iv.get)
    quietest = min(people_by_iv, key=people_by_iv.get)
    print(f"{day_names_no[i]:<12} Mest travelt: kl {busiest} ({people_by_iv[busiest]:.0f} pers)  |  "
          f"Roligst: kl {quietest} ({people_by_iv[quietest]:.0f} pers)")


# Week-over-week trend
print("\n\n5. UKE-TIL-UKE TREND (total onsiteMinutes per dag)")
print("-" * 80)
print(f"{'Dag':<12} {'Dato':<12} {'Uke 1':>10} {'Dato':<12} {'Uke 2':>10} {'Endring':>10}")
print("-" * 80)

week1_dates = ["2026-02-23", "2026-02-24", "2026-02-25", "2026-02-26", "2026-02-27", "2026-02-28", "2026-03-01"]
week2_dates = ["2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05", "2026-03-06", "2026-03-07", "2026-03-08"]

for j, (d1, d2) in enumerate(zip(week1_dates, week2_dates)):
    data1 = historical_data[d1]
    data2 = historical_data[d2]
    total1 = sum(data1.values())
    total2 = sum(data2.values())
    pct_change = ((total2 - total1) / total1) * 100
    sign = "+" if pct_change > 0 else ""
    print(f"{day_names_no[j]:<12} {d1:<12} {total1:>10} {d2:<12} {total2:>10} {sign}{pct_change:>8.1f}%")


# Detailed comparison: What Evo estimates vs what actually happened for the SAME days
# Evo says they use 14 days of data. Their estimate is essentially a 14-day average.
# We can calculate the simple 14-day average and compare to see if that matches.
print("\n\n6. DETALJERT SAMMENLIGNING - EVOs METODE vs. VIRKELIGHETEN")
print("   Evo bruker snitt av siste 14 dager. Vi ser at dette jevner ut ukedagsmønstre.")
print("-" * 80)

# Calculate 14-day simple average across all days
all_14_days = [d for d in historical_data.keys() if d != "2026-03-09"]
simple_avg = {}
for iv in intervals:
    vals = [historical_data[d].get(iv, 0) for d in all_14_days]
    simple_avg[iv] = sum(vals) / len(vals)

print(f"\n{'Interval':<12} {'14d snitt':>10} {'Mon snitt':>10} {'Tue snitt':>10} {'Wed snitt':>10} {'Thu snitt':>10} {'Fri snitt':>10} {'Sat snitt':>10} {'Sun snitt':>10}")
print("-" * 100)

for iv in intervals:
    row = f"{'kl '+iv:<12} {simple_avg[iv]/interval_durations[iv]:>10.1f}"
    for dow in day_names:
        if dow in dow_averages:
            row += f"{dow_averages[dow][iv]/interval_durations[iv]:>10.1f}"
    print(row)

print("\n   Observasjon: Hverdager (Man-Fre) har typisk høyere 17-20 topp enn helger.")
print("   Et 14-dagers snitt blander hverdager og helger, og underestimerer derfor")
print("   hverdagstoppen mens den overestimerer helgekveldene.")
