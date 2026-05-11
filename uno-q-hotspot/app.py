"""ScAIdev captive-portal landing app for the Arduino UNO Q (Linux side).

Same lesson as the MCU demos, but because we're on real Linux we can do
things bare microcontrollers can't:
  - log each visitor with their User-Agent, Accept-Language, and the MAC
    address the kernel sees them coming from
  - resolve the MAC's OUI to a vendor name ("hey, an Apple device joined")
  - show all of that back on the landing page, live, as a "here is what
    the network sees about you just by joining" demonstration

NO credentials are ever requested. NO traffic content is captured. We log
only metadata that the OS would log anyway.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time
from collections import deque
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request


BASE_DIR    = Path(__file__).resolve().parent
STATE_FILE  = BASE_DIR / "state.json"
RECENT_MAX  = 50

app = Flask(__name__)
state_lock = threading.Lock()


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"total_visitors": 0, "recent": []}


def save_state(state: dict) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    tmp.replace(STATE_FILE)


def mac_for_ip(ip: str) -> str | None:
    """Look up the MAC address the kernel has cached for a given IP."""
    try:
        out = subprocess.check_output(["ip", "neigh", "show", ip], text=True, timeout=1)
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    m = re.search(r"lladdr ([0-9a-f:]{17})", out)
    return m.group(1) if m else None


def vendor_for_mac(mac: str) -> str:
    """Crude vendor guess from the OUI (first three bytes).

    A real implementation would query the IEEE OUI database. We ship a tiny
    hand-picked table so the demo "works offline" for the most common
    consumer devices an audience is likely to bring.
    """
    if not mac:
        return "unknown"
    oui = mac[:8].upper().replace(":", "")
    table = {
        "001451": "Apple",  "B8782E": "Apple",     "F0DBE2": "Apple",
        "DCA632": "Raspberry Pi",
        "001A11": "Google", "F4F5D8": "Google",
        "001E10": "Huawei",
        "002241": "Samsung","E8508B": "Samsung",
        "0017F2": "Apple",
        "B827EB": "Raspberry Pi Foundation",
    }
    return table.get(oui, "unknown")


def gather_visitor_info() -> dict:
    ip   = request.remote_addr or "?"
    mac  = mac_for_ip(ip)
    return {
        "timestamp":    time.strftime("%Y-%m-%d %H:%M:%S"),
        "ip":           ip,
        "mac":          mac,
        "vendor":       vendor_for_mac(mac) if mac else "unknown",
        "user_agent":   request.headers.get("User-Agent", ""),
        "language":     request.headers.get("Accept-Language", ""),
        "platform":     request.headers.get("Sec-Ch-Ua-Platform", ""),
    }


@app.route("/")
def root():
    info = gather_visitor_info()
    with state_lock:
        state = load_state()
        state["total_visitors"] += 1
        state["recent"].insert(0, info)
        state["recent"] = state["recent"][:RECENT_MAX]
        save_state(state)
        total = state["total_visitors"]
    app.logger.info("Visit #%d from %s (%s)", total, info["ip"], info["vendor"])
    return render_template("index.html", info=info, total=total)


@app.route("/status")
def status():
    with state_lock:
        state = load_state()
    return jsonify({
        "ssid":           os.environ.get("SCAIDEV_SSID", "ScAIdev"),
        "total_visitors": state["total_visitors"],
        "recent":         state["recent"][:10],
    })


# Captive-portal probe URLs. Returning a 302 here tells each OS "you are
# behind a captive portal" and they auto-pop the landing page.
CAPTIVE_PROBES = [
    "/generate_204",
    "/gen_204",
    "/hotspot-detect.html",
    "/library/test/success.html",
    "/connecttest.txt",
    "/ncsi.txt",
    "/redirect",
]

for _probe in CAPTIVE_PROBES:
    app.add_url_rule(_probe, _probe, lambda: redirect("/", code=302))


@app.errorhandler(404)
def not_found(_e):
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
