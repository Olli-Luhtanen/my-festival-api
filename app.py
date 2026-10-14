"""My Festival REST API — M10 starter (CSC Rahti).

FI: Tämä on M10-tehtävän lähtöpohja. GET /api/artists on valmiina mallina;
    toteuta loput TODO-kohdat. Aja paikallisesti:  python app.py
    ja testaa:  python test_endpoints.py http://localhost:8080
"""
import os
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

app = Flask(__name__)

# FI: Kanta kulkee kontin mukana. Polun voi vaihtaa ympäristömuuttujalla.
# EN: The database ships inside the container. Override the path with an env var.
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "myfestival.db"))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # M8: sqlite3 ei valvo FK:ita oletuksena / FKs are off by default
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def health():
    """FI: Rahti ja selain näkevät, että sovellus on pystyssä.
    EN: Lets Rahti and your browser see the app is up."""
    return jsonify(status="ok", endpoints=["/api/artists", "/api/days", "/api/stages",
                                           "/api/artists/<id>/events", "/api/timetable?day=YYYY-MM-DD",
                                           "POST /api/events", "DELETE /api/events/<id>"])


@app.get("/api/artists")
def get_artists():
    conn = get_db()
    rows = conn.execute("SELECT artist_id, name, country FROM Artist ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/days")
def get_days():
    """FI: Apuendpoint: festivaalipäivät (tarkistin hakee tästä day_id:n).
    EN: Helper endpoint: festival days (the checker reads day_id from here)."""
    conn = get_db()
    rows = conn.execute("SELECT day_id, date FROM Day ORDER BY date").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/stages")
def get_stages():
    """FI: Apuendpoint: lavat. EN: Helper endpoint: stages."""
    conn = get_db()
    rows = conn.execute("SELECT stage_id, name FROM Stage ORDER BY stage_id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/artists/<int:artist_id>/events")
def get_artist_events(artist_id):
    conn = get_db()
    artist = conn.execute(
        "SELECT artist_id FROM Artist WHERE artist_id = ?", (artist_id,)
    ).fetchone()
    if artist is None:
        conn.close()
        return jsonify(error="Artist not found"), 404

    rows = conn.execute(
        """
        SELECT e.event_id, d.date, s.name AS stage, e.start_dt
        FROM Event e
        JOIN Day d   ON d.day_id   = e.day_id
        JOIN Stage s ON s.stage_id = e.stage_id
        WHERE e.artist_id = ?
        ORDER BY e.start_dt
        """,
        (artist_id,),
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.get("/api/timetable")
def get_timetable():
    day = request.args.get("day")

    sql = """
        SELECT d.date AS date,
               s.name AS stage,
               a.name AS artist,
               time(e.start_dt) AS starts,
               time(e.end_dt)   AS ends
        FROM Event e
        JOIN Day d    ON d.day_id    = e.day_id
        JOIN Stage s  ON s.stage_id  = e.stage_id
        JOIN Artist a ON a.artist_id = e.artist_id
    """
    params = ()

    if day is not None:
        try:
            parsed = datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            return jsonify(error="day must be YYYY-MM-DD"), 400
        if parsed.strftime("%Y-%m-%d") != day:   # hylkää esim. 2025-7-5
            return jsonify(error="day must be YYYY-MM-DD"), 400
        sql += " WHERE d.date = ?"
        params = (day,)

    sql += " ORDER BY e.start_dt"

    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.post("/api/events")
def create_event():
    body = request.get_json(silent=True) or {}

    # 1) Pakolliset kentät
    required = ("artist_id", "stage_id", "day_id", "start_dt")
    missing = [k for k in required if body.get(k) is None]
    if missing:
        return jsonify(error=f"Missing field(s): {', '.join(missing)}"), 400

    # 2) Tyypit: id:t kokonaislukuja (bool on Pythonissa int, hylätään se)
    for k in ("artist_id", "stage_id", "day_id"):
        if not isinstance(body[k], int) or isinstance(body[k], bool):
            return jsonify(error=f"{k} must be an integer"), 400

    # 3) Aikaleima: YYYY-MM-DD HH:MM:SS
    try:
        start = datetime.strptime(str(body["start_dt"]), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify(error="start_dt must be in format YYYY-MM-DD HH:MM:SS"), 400

    duration = 45
    start_dt = start.strftime("%Y-%m-%d %H:%M:%S")
    end_dt = (start + timedelta(minutes=duration)).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    try:
        et = conn.execute(
            "SELECT event_type_id FROM EventType WHERE code = ?", ("performance",)
        ).fetchone()
        if et is None:
            return jsonify(error="Event type 'performance' not found"), 500

        cur = conn.execute(
            """
            INSERT INTO Event
                (event_type_id, day_id, stage_id, artist_id,
                 start_dt, end_dt, duration_min)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (et["event_type_id"], body["day_id"], body["stage_id"],
             body["artist_id"], start_dt, end_dt, duration),
        )
        conn.commit()
        new_id = cur.lastrowid

        row = conn.execute(
            """
            SELECT event_id, artist_id, stage_id, day_id,
                   start_dt, end_dt, duration_min
            FROM Event WHERE event_id = ?
            """,
            (new_id,),
        ).fetchone()
        return jsonify(dict(row)), 201

    except sqlite3.IntegrityError as e:
        conn.rollback()
        msg = str(e)
        if "UNIQUE" in msg:
            return jsonify(error="An event already exists on this day, stage and start time"), 400
        if "FOREIGN KEY" in msg:
            return jsonify(error="Invalid artist_id, stage_id or day_id: referenced row does not exist"), 400
        return jsonify(error=f"Integrity error: {msg}"), 400
    finally:
        conn.close()


@app.delete("/api/events/<int:event_id>")
def delete_event(event_id):
    conn = get_db()
    try:
        cur = conn.execute("DELETE FROM Event WHERE event_id = ?", (event_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify(error="Event not found"), 404
        return "", 204
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
