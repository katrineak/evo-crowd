#!/usr/bin/env python3
"""
EVO Adamstuen - Historical visitor charts.
Creates a multi-panel chart showing visitor patterns per day of week.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import date

# Historical actual data - onsiteMinutes per interval
historical_data = {
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
}

interval_durations = {"06-10": 240, "10-12": 120, "12-15": 180, "15-17": 120, "17-20": 180, "20-24": 240}
intervals = ["06-10", "10-12", "12-15", "15-17", "17-20", "20-24"]

# Midpoint hours for each interval (for smoother plotting)
interval_midpoints = [8, 11, 13.5, 16, 18.5, 22]
# Start/end for step plot
interval_edges = [6, 10, 12, 15, 17, 20, 24]

day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_names_no = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]

def to_people(onsite_min, interval):
    return onsite_min / interval_durations[interval]

def day_of_week(date_str):
    y, m, d = map(int, date_str.split("-"))
    return date(y, m, d).strftime("%A")

# Group by day of week
by_dow = {d: [] for d in day_names}
for date_str, data in historical_data.items():
    dow = day_of_week(date_str)
    by_dow[dow].append((date_str, data))

# ===== CHART 1: All 14 days as step chart =====
fig, axes = plt.subplots(2, 1, figsize=(16, 12))
fig.suptitle('EVO Adamstuen - Historiske besøksdata (23. feb - 8. mars 2026)',
             fontsize=16, fontweight='bold', y=0.98)

# Chart 1a: Weekdays
ax1 = axes[0]
colors_weekday = {
    'Monday': '#e63946',
    'Tuesday': '#457b9d',
    'Wednesday': '#2a9d8f',
    'Thursday': '#e9c46a',
    'Friday': '#f4a261',
}

week1_dates = ["2026-02-23", "2026-02-24", "2026-02-25", "2026-02-26", "2026-02-27"]
week2_dates = ["2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05", "2026-03-06"]

for dates, linestyle, week_label in [(week1_dates, '--', 'Uke 9'), (week2_dates, '-', 'Uke 10')]:
    for date_str in dates:
        dow = day_of_week(date_str)
        data = historical_data[date_str]
        people = [to_people(data[iv], iv) for iv in intervals]

        # Create step plot data
        x_step = []
        y_step = []
        for j, iv in enumerate(intervals):
            x_step.extend([interval_edges[j], interval_edges[j+1]])
            y_step.extend([people[j], people[j]])

        color = colors_weekday[dow]
        dow_i = day_names.index(dow)
        label = f"{day_names_no[dow_i]} {date_str[5:]}"
        alpha = 0.5 if linestyle == '--' else 0.9
        lw = 1.5 if linestyle == '--' else 2.5
        ax1.plot(x_step, y_step, color=color, linestyle=linestyle, linewidth=lw,
                alpha=alpha, label=label)

ax1.axhline(y=35, color='red', linestyle=':', alpha=0.5, linewidth=1)
ax1.text(6.2, 36, 'Maks kapasitet (35)', color='red', fontsize=9, alpha=0.7)
ax1.set_xlim(6, 24)
ax1.set_ylim(0, 50)
ax1.set_xlabel('Klokkeslett', fontsize=12)
ax1.set_ylabel('Antall besøkende', fontsize=12)
ax1.set_title('Hverdager (Man-Fre)', fontsize=14)
ax1.set_xticks(range(6, 25, 2))
ax1.set_xticklabels([f'{h:02d}:00' for h in range(6, 25, 2)])
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper left', fontsize=8, ncol=2)

# Chart 1b: Weekends
ax2 = axes[1]
colors_weekend = {
    'Saturday': '#9b59b6',
    'Sunday': '#3498db',
}

weekend1_dates = ["2026-02-28", "2026-03-01"]
weekend2_dates = ["2026-03-07", "2026-03-08"]

for dates, linestyle, week_label in [(weekend1_dates, '--', 'Uke 9'), (weekend2_dates, '-', 'Uke 10')]:
    for date_str in dates:
        dow = day_of_week(date_str)
        data = historical_data[date_str]
        people = [to_people(data[iv], iv) for iv in intervals]

        x_step = []
        y_step = []
        for j, iv in enumerate(intervals):
            x_step.extend([interval_edges[j], interval_edges[j+1]])
            y_step.extend([people[j], people[j]])

        color = colors_weekend[dow]
        dow_i = day_names.index(dow)
        label = f"{day_names_no[dow_i]} {date_str[5:]}"
        alpha = 0.5 if linestyle == '--' else 0.9
        lw = 1.5 if linestyle == '--' else 2.5
        ax2.plot(x_step, y_step, color=color, linestyle=linestyle, linewidth=lw,
                alpha=alpha, label=label)

ax2.axhline(y=35, color='red', linestyle=':', alpha=0.5, linewidth=1)
ax2.text(6.2, 36, 'Maks kapasitet (35)', color='red', fontsize=9, alpha=0.7)
ax2.set_xlim(6, 24)
ax2.set_ylim(0, 50)
ax2.set_xlabel('Klokkeslett', fontsize=12)
ax2.set_ylabel('Antall besøkende', fontsize=12)
ax2.set_title('Helg (Lør-Søn)', fontsize=14)
ax2.set_xticks(range(6, 25, 2))
ax2.set_xticklabels([f'{h:02d}:00' for h in range(6, 25, 2)])
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper left', fontsize=8, ncol=2)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('/Users/k/Claude/evo-crowd/historical_visitors.png', dpi=150, bbox_inches='tight')
print("Saved: historical_visitors.png")

# ===== CHART 2: Average pattern per day of week with range =====
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 7))
fig2.suptitle('EVO Adamstuen - Gjennomsnittlig besøksmønster per ukedag',
              fontsize=16, fontweight='bold', y=0.98)

# Weekdays average with range
ax3 = axes2[0]
for dow in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
    entries = by_dow[dow]
    if len(entries) < 2:
        continue
    dow_i = day_names.index(dow)

    avg_people = []
    min_people = []
    max_people = []
    for iv in intervals:
        vals = [to_people(e[1][iv], iv) for e in entries]
        avg_people.append(sum(vals) / len(vals))
        min_people.append(min(vals))
        max_people.append(max(vals))

    # Step plot for average
    x_step = []
    y_avg = []
    y_min = []
    y_max = []
    for j in range(len(intervals)):
        x_step.extend([interval_edges[j], interval_edges[j+1]])
        y_avg.extend([avg_people[j], avg_people[j]])
        y_min.extend([min_people[j], min_people[j]])
        y_max.extend([max_people[j], max_people[j]])

    color = colors_weekday[dow]
    ax3.plot(x_step, y_avg, color=color, linewidth=2.5, label=day_names_no[dow_i])
    ax3.fill_between(x_step, y_min, y_max, color=color, alpha=0.1)

ax3.axhline(y=35, color='red', linestyle=':', alpha=0.5, linewidth=1)
ax3.set_xlim(6, 24)
ax3.set_ylim(0, 50)
ax3.set_xlabel('Klokkeslett', fontsize=12)
ax3.set_ylabel('Antall besøkende', fontsize=12)
ax3.set_title('Hverdager - Snitt med min/maks-område', fontsize=13)
ax3.set_xticks(range(6, 25, 2))
ax3.set_xticklabels([f'{h:02d}:00' for h in range(6, 25, 2)])
ax3.grid(True, alpha=0.3)
ax3.legend(loc='upper left', fontsize=9)

# Weekends average with range
ax4 = axes2[1]
for dow in ['Saturday', 'Sunday']:
    entries = by_dow[dow]
    if len(entries) < 2:
        continue
    dow_i = day_names.index(dow)

    avg_people = []
    min_people = []
    max_people = []
    for iv in intervals:
        vals = [to_people(e[1][iv], iv) for e in entries]
        avg_people.append(sum(vals) / len(vals))
        min_people.append(min(vals))
        max_people.append(max(vals))

    x_step = []
    y_avg = []
    y_min = []
    y_max = []
    for j in range(len(intervals)):
        x_step.extend([interval_edges[j], interval_edges[j+1]])
        y_avg.extend([avg_people[j], avg_people[j]])
        y_min.extend([min_people[j], min_people[j]])
        y_max.extend([max_people[j], max_people[j]])

    color = colors_weekend[dow]
    ax4.plot(x_step, y_avg, color=color, linewidth=2.5, label=day_names_no[dow_i])
    ax4.fill_between(x_step, y_min, y_max, color=color, alpha=0.15)

ax4.axhline(y=35, color='red', linestyle=':', alpha=0.5, linewidth=1)
ax4.set_xlim(6, 24)
ax4.set_ylim(0, 50)
ax4.set_xlabel('Klokkeslett', fontsize=12)
ax4.set_ylabel('Antall besøkende', fontsize=12)
ax4.set_title('Helg - Snitt med min/maks-område', fontsize=13)
ax4.set_xticks(range(6, 25, 2))
ax4.set_xticklabels([f'{h:02d}:00' for h in range(6, 25, 2)])
ax4.grid(True, alpha=0.3)
ax4.legend(loc='upper left', fontsize=9)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('/Users/k/Claude/evo-crowd/average_pattern.png', dpi=150, bbox_inches='tight')
print("Saved: average_pattern.png")

# ===== CHART 3: Heatmap showing all 14 days =====
fig3, ax5 = plt.subplots(figsize=(14, 8))

dates_sorted = sorted(historical_data.keys())
heatmap_data = []
date_labels = []

for date_str in dates_sorted:
    dow = day_of_week(date_str)
    dow_i = day_names.index(dow)
    date_labels.append(f"{day_names_no[dow_i][:3]} {date_str[5:]}")
    row = [to_people(historical_data[date_str][iv], iv) for iv in intervals]
    heatmap_data.append(row)

heatmap_array = np.array(heatmap_data)

im = ax5.imshow(heatmap_array, cmap='YlOrRd', aspect='auto', vmin=0, vmax=45)

ax5.set_xticks(range(len(intervals)))
ax5.set_xticklabels([f'kl {iv}' for iv in intervals], fontsize=11)
ax5.set_yticks(range(len(date_labels)))
ax5.set_yticklabels(date_labels, fontsize=10)

# Add text annotations
for i in range(len(date_labels)):
    for j in range(len(intervals)):
        val = heatmap_array[i, j]
        color = 'white' if val > 25 else 'black'
        ax5.text(j, i, f'{val:.0f}', ha='center', va='center', color=color, fontsize=11, fontweight='bold')

cbar = plt.colorbar(im, ax=ax5, label='Antall besøkende')
ax5.set_title('EVO Adamstuen - Besøkende per tidsintervall (siste 14 dager)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/k/Claude/evo-crowd/heatmap.png', dpi=150, bbox_inches='tight')
print("Saved: heatmap.png")

print("\nAlle 3 grafer lagret!")
