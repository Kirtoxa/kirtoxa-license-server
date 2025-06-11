
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses (
        key TEXT PRIMARY KEY,
        hwid TEXT,
        expiration TEXT
    )''')
    conn.commit()
    conn.close()

@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid")
    if not key or not hwid:
        return jsonify({"valid": False, "reason": "Missing key or HWID"})

    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute("SELECT hwid, expiration FROM licenses WHERE key = ?", (key,))
    row = c.fetchone()
    if not row:
        return jsonify({"valid": False, "reason": "Key not found"})
    db_hwid, expiration = row

    now = datetime.datetime.utcnow()
    if expiration:
        try:
            if now > datetime.datetime.strptime(expiration, "%Y-%m-%d %H:%M:%S"):
                return jsonify({"valid": False, "reason": "Key expired"})
        except ValueError:
            return jsonify({"valid": False, "reason": "Invalid expiration format"})

    if not db_hwid:
        c.execute("UPDATE licenses SET hwid = ? WHERE key = ?", (hwid, key))
        conn.commit()
        conn.close()
        return jsonify({"valid": True, "reason": "HWID bound"})
    elif db_hwid != hwid:
        return jsonify({"valid": False, "reason": "HWID mismatch"})
    else:
        return jsonify({"valid": True, "reason": "Valid key"})

@app.route("/add", methods=["POST"])
def add_key():
    data = request.get_json()
    key = data.get("key")
    expiration = data.get("expiration")
    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO licenses (key, hwid, expiration) VALUES (?, ?, ?)", (key, None, expiration))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/revoke", methods=["POST"])
def revoke_key():
    data = request.get_json()
    key = data.get("key")
    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute("DELETE FROM licenses WHERE key = ?", (key,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/list", methods=["GET"])
def list_keys():
    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute("SELECT key, hwid, expiration FROM licenses")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"key": r[0], "hwid": r[1], "expiration": r[2]} for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
