import os
import sqlite3
import threading
from collections import Counter
from datetime import datetime
from flask import Flask, render_template, jsonify
from processor import parse_logs, extract_features
from ml_model import predict
from db import init_db, insert_log, fetch_logs, DB_PATH
from alerts import check_alert
from ai_engine import simulate_command

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
init_db()

# Track watcher status for dashboard
watcher_status = {"running": False, "last_seen": None, "total_processed": 0}


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    logs = fetch_logs()
    return render_template("dashboard.html", logs=logs, status=watcher_status)


@app.route("/map")
def map_page():
    return render_template("map.html")


# ── Manual pipeline trigger ───────────────────────────────────────────────────

@app.route("/run")
def run_pipeline():
    logs = parse_logs()
    if not logs:
        return "No logs found. Make sure data/cowrie.log exists with valid JSON lines."
    for log in logs:
        ip = log.get("src_ip", "unknown")
        command = log.get("input", "")
        features = extract_features(log)
        prediction = predict(features)
        insert_log(ip, command, prediction)
        check_alert(ip, prediction)
        response = simulate_command(command)
        print(f"Attacker ({ip}): {command!r} -> {prediction} | sent: {response}")
        watcher_status["last_seen"] = datetime.now().strftime("%H:%M:%S")
        watcher_status["total_processed"] += 1
    return f"Pipeline executed! Processed {len(logs)} entries. <a href='/'>View Dashboard</a>"


# ── Live watcher status API ───────────────────────────────────────────────────

@app.route("/api/status")
def api_status():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM logs")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM logs WHERE attack_type = 'Brute Force'")
    brute = c.fetchone()[0]
    c.execute("SELECT ip, command, attack_type, timestamp FROM logs ORDER BY id DESC LIMIT 1")
    last = c.fetchone()
    conn.close()
    return jsonify({
        "total": total,
        "brute_force": brute,
        "watcher_running": watcher_status["running"],
        "last_seen": watcher_status["last_seen"],
        "last_attack": {"ip": last[0], "command": last[1], "type": last[2], "time": last[3]} if last else None
    })


# ── Chart APIs ────────────────────────────────────────────────────────────────

@app.route("/api/map")
def attack_map():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ip, attack_type FROM logs")
    rows = c.fetchall()
    conn.close()

    # Static geo fallback — replace with ip-api.com call for real geolocation
    fake_locations = {
        "1.1.1.1": (28.6139, 77.2090, "India"),
        "2.2.2.2": (19.0760, 72.8777, "India"),
        "3.3.3.3": (51.5074, -0.1278, "UK"),
    }
    points = []
    for ip, attack_type in rows:
        lat, lon, country = fake_locations.get(ip, (20.5937, 78.9629, "Unknown"))
        points.append({"ip": ip, "lat": lat, "lon": lon, "country": country, "attack_type": attack_type})
    return jsonify(points)


@app.route("/api/types")
def attack_types():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT attack_type FROM logs")
    rows = c.fetchall()
    conn.close()
    return jsonify(dict(Counter(r[0] for r in rows)))


@app.route("/api/ips")
def top_ips():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ip FROM logs")
    rows = c.fetchall()
    conn.close()
    return jsonify(dict(Counter(r[0] for r in rows).most_common(10)))


@app.route("/api/trend")
def attack_trend():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DATE(timestamp) as day, COUNT(*) FROM logs GROUP BY day ORDER BY day ASC")
    rows = c.fetchall()
    conn.close()
    return jsonify({row[0]: row[1] for row in rows})


@app.route("/api/logs")
def api_logs():
    """Returns latest 50 logs as JSON — used for live auto-refresh without page reload."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, ip, command, attack_type, timestamp FROM logs ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "ip": r[1], "command": r[2], "type": r[3], "time": r[4]} for r in rows])


if __name__ == "__main__":
    app.run(debug=True)
