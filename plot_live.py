#!/usr/bin/env python3
"""
EVO Adamstuen - Live visitor chart.
Reads from visitor_log.csv and generates an updated chart.
Shows today's real-time data vs historical average for the same day of week.
Run this whenever you want an updated chart.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import csv
import os
from datetime import datetime, date, timedelta

LOG_FILE = '/Users/k/Claude/evo-crowd/visitor_log.csv'
OUTPUT_FILE = '/Users/k/Claude/evo-crowd/live_visitors.png'

# Historical averages per day-of-week (from our analysis)
# Format: {day_name: {interval: avg_people}}
historical_avg = {
    "Monday":    {"06-10": 11.3, "10-12": 18.1, "12-15": 18.2, "15-17": 27.5, "17-20": 40.6, "20-24": 16.8},
    "Tuesday":   {"06-10": 13.1, "10-12": 21.3, "12-15": 14.4, "15-17": 28.5, "17-20": 37.4, "20-24": 15.7},
    "Wednesday": {"06-10": 14.7, "10-12": 19.5, "12-15": 18.6, "15-17": 27.4, "17-20": 40.2, "20-24": 14.9},
    "Thursday":  {"06-10": 15.6, "10-12": 14.1, "12-15": 14.8, "15-17": 27.7, "17-20": 30.0, "20-24": 13.1},
    "Friday":    {"06-10": 14.3, "10-12": 19.7, "12-15": 19.8, "15-17": 25.9, "17-20": 23.5, "20-24": 8.2},
    "Saturday":  {"06-10": 9.1,  "10-12": 29.6, "12-15": 25.1, "15-17": 19.2, "17-20": 13.7, "20-24": 5.9},
    "Sunday":    {"06-10": 9.6,  "10-12": 18.3, "12-15": 25.2, "15-17": 20.4, "17-20": 14.1, "20-24": 6.9},
}

# Historical max per day-of-week
historical_max = {
    "Monday":    {"06-10": 12.5, "10-12": 18.8, "12-15": 17.9, "15-17": 28.3, "17-20": 41.7, "20-24": 19.2},
    "Tuesday":   {"06-10": 13.4, "10-12": 21.9, "12-15": 15.1, "15-17": 29.6, "17-20": 41.0, "20-24": 16.1},
    "Wednesday": {"06-10": 14.8, "10-12": 20.0, "12-15": 18.5, "15-17": 32.7, "17-20": 40.6, "20-24": 17.6},
    "Thursday":  {"06-10": 16.0, "10-12": 14.7, "12-15": 14.8, "15-17": 30.8, "17-20": 30.1, "20-24": 14.3},
    "Friday":    {"06-10": 14.4, "10-12": 22.9, "12-15": 20.9, "15-17": 25.8, "17-20": 24.7, "20-24": 10.3},
    "Saturday":  {"06-10": 9.8,  "10-12": 32.2, "12-15": 26.2, "15-17": 22.7, "17-20": 16.9, "20-24": 7.1},
    "Sunday":    {"06-10": 9.5,  "10-12": 18.7, "12-15": 26.7, "15-17": 21.1, "17-20": 14.2, "20-24": 7.5},
}

intervals = ["06-10", "10-12", "12-15", "15-17", "17-20", "20-24"]
interval_edges = [6, 10, 12, 15, 17, 20, 24]
day_names_no = {"Monday": "Mandag", "Tuesday": "Tirsdag", "Wednesday": "Onsdag",
                "Thursday": "Torsdag", "Friday": "Fredag", "Saturday": "Lørdag", "Sunday": "Søndag"}

def read_log():
    """Read polling log and return data grouped by date."""
    if not os.path.exists(LOG_FILE):
        return {}

    by_date = {}
    with open(LOG_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            date_str = ts.strftime('%Y-%m-%d')
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append({
                'time': ts,
                'hour': ts.hour + ts.minute / 60.0,
                'current': int(row['current']),
                'max_capacity': int(row['max_capacity']),
            })

    return by_date

def generate_chart():
    data = read_log()
    if not data:
        print("No polling data yet.")
        return

    # Get all dates with data
    dates_with_data = sorted(data.keys())

    # Create a chart for each day that has data
    n_days = len(dates_with_data)
    if n_days == 0:
        print("No data to plot")
        return

    # Layout: up to 3 columns
    n_cols = min(n_days, 3)
    n_rows = (n_days + n_cols - 1) // n_cols
    fig_height = max(5, 5 * n_rows)
    fig_width = min(18, 6 * n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height), squeeze=False)
    fig.suptitle('EVO Adamstuen - Sanntidsbesøk (5-min oppløsning)',
                 fontsize=16, fontweight='bold', y=0.98)

    for idx, date_str in enumerate(dates_with_data):
        row = idx // n_cols
        col = idx % n_cols
        ax = axes[row][col]

        day_data = data[date_str]
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        dow = dt.strftime('%A')
        dow_no = day_names_no.get(dow, dow)

        hours = [d['hour'] for d in day_data]
        visitors = [d['current'] for d in day_data]

        # Plot real-time data
        ax.plot(hours, visitors, 'o-', color='#e63946', linewidth=2, markersize=4,
                label='Faktisk (sanntid)', zorder=5)

        # Plot Evo's historical average as step function (background)
        if dow in historical_avg:
            avg = historical_avg[dow]
            mx = historical_max[dow]
            x_step = []
            y_avg_step = []
            y_max_step = []
            for j, iv in enumerate(intervals):
                x_step.extend([interval_edges[j], interval_edges[j+1]])
                y_avg_step.extend([avg[iv], avg[iv]])
                y_max_step.extend([mx[iv], mx[iv]])

            ax.fill_between(x_step, 0, y_avg_step, color='#457b9d', alpha=0.15, label='Evo snitt (historisk)')
            ax.plot(x_step, y_avg_step, color='#457b9d', linewidth=1.5, linestyle='--', alpha=0.7)
            ax.plot(x_step, y_max_step, color='#457b9d', linewidth=1, linestyle=':', alpha=0.5, label='Historisk maks')

        # Capacity line
        ax.axhline(y=35, color='red', linestyle=':', alpha=0.4, linewidth=1)

        ax.set_xlim(5, 24.5)
        ax.set_ylim(0, max(50, max(visitors) + 5 if visitors else 50))
        ax.set_xlabel('Klokkeslett', fontsize=10)
        ax.set_ylabel('Besøkende', fontsize=10)
        ax.set_title(f'{dow_no} {date_str}', fontsize=13, fontweight='bold')
        ax.set_xticks(range(6, 25, 2))
        ax.set_xticklabels([f'{h:02d}' for h in range(6, 25, 2)])
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=8)

        # Add current count annotation for the last data point
        if visitors:
            last_h = hours[-1]
            last_v = visitors[-1]
            ax.annotate(f'{last_v} pers',
                       xy=(last_h, last_v),
                       xytext=(last_h + 0.5, last_v + 3),
                       fontsize=10, fontweight='bold', color='#e63946',
                       arrowprops=dict(arrowstyle='->', color='#e63946', lw=1.5))

    # Hide unused axes
    for idx in range(n_days, n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row][col].set_visible(False)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches='tight')
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Data points: {sum(len(v) for v in data.values())} across {n_days} day(s)")

    # Print summary
    for date_str in dates_with_data:
        day_data = data[date_str]
        visitors = [d['current'] for d in day_data]
        times = [d['time'].strftime('%H:%M') for d in day_data]
        print(f"\n  {date_str}: {len(day_data)} målinger")
        print(f"    Min: {min(visitors)} | Maks: {max(visitors)} | Snitt: {sum(visitors)/len(visitors):.1f}")
        print(f"    Tidsrom: {times[0]} - {times[-1]}")

if __name__ == '__main__':
    generate_chart()
