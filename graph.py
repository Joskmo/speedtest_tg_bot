"""Generate 24-hour speed chart from aggregated measurements."""

import io
from datetime import datetime

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

matplotlib.use("Agg")


def generate_chart(
    speedtest_data: list,
    wget_data: list,
) -> io.BytesIO:
    """Create a line chart with two independent source curves.

    Returns a BytesIO buffer with the chart image.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    _plot_curve(ax, speedtest_data, "b-o", "Speedtest")
    _plot_curve(ax, wget_data, "g-s", "Wget")

    if not speedtest_data and not wget_data:
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

    ax.set_ylabel("Download (Mbit/s)")
    ax.set_title("Network Speed (24h)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)

    return buf


def _plot_curve(ax, data: list, style: str, label: str) -> None:
    """Plot a single curve if data is available."""
    if not data:
        return

    times = []
    values = []
    for entry in data:
        dt = datetime.fromtimestamp(entry["time"])
        if entry["dl"] is not None:
            times.append(dt)
            values.append(entry["dl"])

    if times:
        ax.plot(times, values, style, label=label, markersize=4)
