"""Speed measurement methods: speedtest-cli and wget."""

import re
import subprocess

import speedtest


def measure_speedtest() -> dict | None:
    """Measure speed using speedtest-cli.

    Returns dict with download, upload, ping or None on failure.
    """
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping
        return {
            "download": round(download, 2),
            "upload": round(upload, 2),
            "ping": round(ping, 2),
        }
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def measure_wget() -> dict | None:
    """Measure download speed using wget to Selectel speedtest.

    Returns dict with download or None on failure.
    """
    try:
        result = subprocess.run(
            ["wget", "-O", "/dev/null", "https://speedtest.selectel.ru/1GB"],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        output = result.stderr
        match = re.search(r"\(([\d.]+)\s*(KB/s|MB/s|GB/s)\)", output)
        if not match:
            return None
        speed = float(match.group(1))
        unit = match.group(2)
        if unit == "KB/s":
            speed *= 0.008
        elif unit == "MB/s":
            speed *= 8
        elif unit == "GB/s":
            speed *= 8000
        return {"download": round(speed, 2)}
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def measure_all() -> list:
    """Run both measurements sequentially.

    Returns list of results (each is dict or None).
    """
    return [measure_speedtest(), measure_wget()]
