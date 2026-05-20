import os
import sqlite3
from collections import Counter, defaultdict
from flask import Flask, render_template, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "honeypot.db")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))


def get_conn():
    return sqlite3.connect(DB_PATH)


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, ip, command, attack_type FROM logs ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template("dashboard.html", logs=data)


# ── API: Attack Map ───────────────────────────────────────────────────────────

@app.route("/api/map")
def attack_map():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT ip, attack_type FROM logs")
    rows = c.fetchall()
    conn.close()

    fake_locations = {
        "1.1.1.1": (28.6139, 77.2090, "India"),
        "2.2.2.2": (19.0760, 72.8777, "India"),
        "3.3.3.3": (51.5074, -0.1278, "UK"),
    }

    points = []
    for ip, attack_type in rows:
        lat, lon, country = fake_locations.get(ip, (20.5937, 78.9629, "Unknown"))
        points.append({
            "ip": ip,
            "lat": lat,
            "lon": lon,
            "country": country,          # Fix: map.js references item.country
            "attack_type": attack_type
        })

    return jsonify(points)


# ── API: Attack Types (pie chart) ─────────────────────────────────────────────

@app.route("/api/types")
def attack_types():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT attack_type FROM logs")
    rows = c.fetchall()
    conn.close()

    counts = Counter(r[0] for r in rows)
    return jsonify(dict(counts))


# ── API: Top IPs (bar chart) ──────────────────────────────────────────────────

@app.route("/api/ips")
def top_ips():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT ip FROM logs")
    rows = c.fetchall()
    conn.close()

    counts = Counter(r[0] for r in rows)
    top10 = dict(counts.most_common(10))
    return jsonify(top10)


# ── API: Attack Trend (line chart) ────────────────────────────────────────────

@app.route("/api/trend")
def attack_trend():
    conn = get_conn()
    c = conn.cursor()
    # Group by date portion of timestamp
    c.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as cnt
        FROM logs
        GROUP BY day
        ORDER BY day ASC
    """)
    rows = c.fetchall()
    conn.close()

    trend = {row[0]: row[1] for row in rows}
    return jsonify(trend)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5001)
