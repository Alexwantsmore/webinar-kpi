"""Fetch 30 days of Garmin Connect health data and save to CSV files.

Credentials are read from environment variables GARMIN_EMAIL and GARMIN_PASSWORD
to avoid writing them to disk.
"""

import csv
import os
import sys
import warnings
from datetime import date, timedelta
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

import garth
from garth.data import BodyBatteryData, DailySleepData, HRVData
from garth.stats import DailyHRV, DailyStress

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "garmin_data"
PERIOD_DAYS = 30


def login() -> None:
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    if not email or not password:
        print("ERROR: set GARMIN_EMAIL and GARMIN_PASSWORD env vars", file=sys.stderr)
        sys.exit(1)
    print(f"Logging in as {email}...")
    mfa_code = os.environ.get("GARMIN_MFA")
    if mfa_code:
        garth.login(email, password, prompt_mfa=lambda: mfa_code)
    else:
        garth.login(email, password)
    print(f"Logged in. User: {garth.client.username}")


def fmt_secs_to_hours(secs):
    if secs is None:
        return ""
    return round(secs / 3600, 2)


def fetch_sleep(end_day: date, days: int) -> list[dict]:
    rows = []
    for i in range(days):
        day = end_day - timedelta(days=i)
        try:
            data = DailySleepData.get(day)
        except Exception as e:
            print(f"  sleep {day}: error {e}")
            continue
        if not data:
            continue
        dto = data.daily_sleep_dto
        scores = dto.sleep_scores
        spo2 = data.wellness_sp_o2_sleep_summary_dto
        rows.append({
            "calendar_date": dto.calendar_date.isoformat(),
            "sleep_score": scores.overall.value if scores and scores.overall else None,
            "sleep_score_qualifier": scores.overall.qualifier_key if scores and scores.overall else None,
            "total_sleep_hours": fmt_secs_to_hours(dto.sleep_time_seconds),
            "deep_sleep_hours": fmt_secs_to_hours(dto.deep_sleep_seconds),
            "light_sleep_hours": fmt_secs_to_hours(dto.light_sleep_seconds),
            "rem_sleep_hours": fmt_secs_to_hours(dto.rem_sleep_seconds),
            "awake_hours": fmt_secs_to_hours(dto.awake_sleep_seconds),
            "awake_count": dto.awake_count,
            "sleep_start_local": dto.sleep_start.isoformat() if dto.sleep_start_timestamp_local else None,
            "sleep_end_local": dto.sleep_end.isoformat() if dto.sleep_end_timestamp_local else None,
            "avg_sleep_stress": dto.avg_sleep_stress,
            "resting_heart_rate": data.resting_heart_rate,
            "body_battery_change": data.body_battery_change,
            "avg_spo2": dto.average_sp_o2_value,
            "lowest_spo2": dto.lowest_sp_o2_value,
            "highest_spo2": dto.highest_sp_o2_value,
            "avg_respiration": dto.average_respiration_value,
            "sleep_need_minutes": data.sleep_need_minutes,
        })
        print(f"  sleep {dto.calendar_date}: score={scores.overall.value if scores and scores.overall else 'n/a'}")
    return sorted(rows, key=lambda r: r["calendar_date"])


def fetch_body_battery(end_day: date, days: int) -> list[dict]:
    rows = []
    for i in range(days):
        day = end_day - timedelta(days=i)
        try:
            datasets = BodyBatteryData.get(day)
        except Exception as e:
            print(f"  bb {day}: error {e}")
            continue
        if not datasets:
            continue
        all_readings = []
        charged_total = 0
        drained_total = 0
        for d in datasets:
            all_readings.extend(d.body_battery_readings)
            if d.event:
                if getattr(d.event, "body_battery_impact", None) is not None:
                    impact = d.event.body_battery_impact
                    if impact > 0:
                        charged_total += impact
                    else:
                        drained_total += impact
        if not all_readings:
            continue
        all_readings.sort(key=lambda r: r.timestamp)
        levels = [r.level for r in all_readings]
        rows.append({
            "calendar_date": day.isoformat(),
            "level_start": all_readings[0].level,
            "level_end": all_readings[-1].level,
            "level_min": min(levels),
            "level_max": max(levels),
            "charged_total": charged_total if charged_total else None,
            "drained_total": drained_total if drained_total else None,
            "readings_count": len(all_readings),
        })
        print(f"  bb {day}: start={all_readings[0].level} end={all_readings[-1].level} min={min(levels)} max={max(levels)}")
    return sorted(rows, key=lambda r: r["calendar_date"])


def fetch_hrv(end_day: date, days: int) -> list[dict]:
    try:
        daily_list = DailyHRV.list(end=end_day, period=days)
    except Exception as e:
        print(f"  hrv list error: {e}")
        daily_list = []
    rows = []
    for d in daily_list:
        baseline = d.baseline
        rows.append({
            "calendar_date": d.calendar_date.isoformat(),
            "weekly_avg": d.weekly_avg,
            "last_night_avg": d.last_night_avg,
            "last_night_5min_high": d.last_night_5_min_high,
            "status": d.status,
            "baseline_low_upper": baseline.low_upper if baseline else None,
            "baseline_balanced_low": baseline.balanced_low if baseline else None,
            "baseline_balanced_upper": baseline.balanced_upper if baseline else None,
            "baseline_marker_value": baseline.marker_value if baseline else None,
            "feedback": d.feedback_phrase,
        })
        print(f"  hrv {d.calendar_date}: last_night={d.last_night_avg} weekly={d.weekly_avg} status={d.status}")
    return sorted(rows, key=lambda r: r["calendar_date"])


def fetch_stress(end_day: date, days: int) -> list[dict]:
    try:
        daily_list = DailyStress.list(end=end_day, period=days)
    except Exception as e:
        print(f"  stress list error: {e}")
        daily_list = []
    rows = []
    for d in daily_list:
        cal_date = getattr(d, "calendar_date", None)
        if cal_date is None:
            continue
        rows.append({
            "calendar_date": cal_date.isoformat() if hasattr(cal_date, "isoformat") else str(cal_date),
            "overall_stress_level": d.overall_stress_level,
            "rest_minutes": (d.rest_stress_duration or 0) // 60,
            "low_minutes": (d.low_stress_duration or 0) // 60,
            "medium_minutes": (d.medium_stress_duration or 0) // 60,
            "high_minutes": (d.high_stress_duration or 0) // 60,
        })
        print(f"  stress {cal_date}: avg={d.overall_stress_level}")
    return sorted(rows, key=lambda r: r["calendar_date"])


def write_csv(filename: str, rows: list[dict]) -> int:
    path = OUTPUT_DIR / filename
    if not rows:
        path.write_text("")
        return 0
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    login()

    end_day = date.today()
    print(f"\nFetching {PERIOD_DAYS} days ending {end_day}")

    print("\n[1/4] Sleep data...")
    sleep_rows = fetch_sleep(end_day, PERIOD_DAYS)
    print("\n[2/4] Body Battery...")
    bb_rows = fetch_body_battery(end_day, PERIOD_DAYS)
    print("\n[3/4] HRV...")
    hrv_rows = fetch_hrv(end_day, PERIOD_DAYS)
    print("\n[4/4] Stress...")
    stress_rows = fetch_stress(end_day, PERIOD_DAYS)

    print("\n=== Summary ===")
    summary = [
        ("sleep.csv", write_csv("sleep.csv", sleep_rows)),
        ("body_battery.csv", write_csv("body_battery.csv", bb_rows)),
        ("hrv.csv", write_csv("hrv.csv", hrv_rows)),
        ("stress.csv", write_csv("stress.csv", stress_rows)),
    ]
    for fname, count in summary:
        print(f"  {fname}: {count} rows")


if __name__ == "__main__":
    main()
