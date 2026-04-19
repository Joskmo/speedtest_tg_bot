"""Persistent JSON storage for speed measurements."""

import json
import os
import time

DATA_PATH = os.getenv("DATA_PATH", "/data/speedtest_data.json")
MAX_AGE_HOURS = 24


def load_data(path: str = DATA_PATH) -> list:
    """Load measurements from JSON file."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_data(data: list, path: str = DATA_PATH) -> None:
    """Save measurements to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))


def add_measurement(
    source: str,
    download: float,
    upload: float | None = None,
    ping: float | None = None,
    path: str = DATA_PATH,
) -> None:
    """Add a new measurement and cleanup old data."""
    data = load_data(path)
    entry = {
        "t": int(time.time()),
        "s": source,
        "d": round(download, 2),
    }
    if upload is not None:
        entry["u"] = round(upload, 2)
    if ping is not None:
        entry["p"] = round(ping, 2)
    data.append(entry)
    cutoff = time.time() - (MAX_AGE_HOURS * 3600)
    data = [m for m in data if m["t"] >= cutoff]
    save_data(data, path)


def get_recent_hours(hours: int = 24, path: str = DATA_PATH) -> list:
    """Return hourly aggregated data for the last N hours."""
    data = load_data(path)
    if not data:
        return []

    now = time.time()
    current_hour_start = now - (now % 3600)
    window_start = current_hour_start - ((hours - 1) * 3600)

    buckets = {}
    for m in data:
        ts = m["t"]
        if ts < window_start:
            continue
        bucket_ts = int(ts // 3600) * 3600
        if bucket_ts not in buckets:
            buckets[bucket_ts] = {"dl": [], "ul": []}
        buckets[bucket_ts]["dl"].append(m["d"])
        if "u" in m:
            buckets[bucket_ts]["ul"].append(m["u"])

    result = []
    for bucket_ts in sorted(buckets.keys()):
        dl_vals = buckets[bucket_ts]["dl"]
        ul_vals = buckets[bucket_ts]["ul"]
        result.append(
            {
                "time": bucket_ts,
                "dl": sum(dl_vals) / len(dl_vals) if dl_vals else None,
                "ul": sum(ul_vals) / len(ul_vals) if ul_vals else None,
            }
        )
    return result
