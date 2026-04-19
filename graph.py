"""Generate 24-hour speed chart from aggregated measurements."""

import io
from datetime import datetime

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

matplotlib.use("Agg")


def generate_chart(hourly_data: list) -> io.BytesIO:
    """Create a line chart from hourly aggregated data.

    Returns a BytesIO buffer with the chart image.
    """
    times = []
    dl_values = []
    ul_values = []

    for entry in hourly_data:
        dt = datetime.fromtimestamp(entry["time"])
        times.append(dt)
        dl_values.append(entry["dl"])
        ul_values.append(entry["ul"])

    fig, ax = plt.subplots(figsize=(10, 5))

    has_dl = any(v is not None for v in dl_values)
    has_ul = any(v is not None for v in ul_values)

    if has_dl:
        dl_times = [t for t, v in zip(times, dl_values) if v is not None]
        dl_vals = [v for v in dl_values if v is not None]
        ax.plot(dl_times, dl_vals, "b-o", label="Download", markersize=4)

    if has_ul:
        ul_times = [t for t, v in zip(times, ul_values) if v is not None]
        ul_vals = [v for v in ul_values if v is not None]
        ax.plot(ul_times, ul_vals, "r-o", label="Upload", markersize=4)

    if not has_dl and not has_ul:
        ax.text(
            0.5,
            0.5,
            "No data",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=14,
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    fig.autofmt_xdate()

    ax.set_ylabel("Mbit/s")
    ax.set_title("Network Speed (24h)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)

    return buf
