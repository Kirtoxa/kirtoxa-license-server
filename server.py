
from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__)
LICENSE_FILE = "licenses.json"

def load_licenses():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=4)

licenses = load_licenses()

@app.route("/", methods=["GET"])
def home():
    return "Kirtoxa License Server is running."

@app.route("/admin")
def admin_panel():
    return send_from_directory(".", "index.html")

@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid")

    if not key or not hwid:
        return "invalid"

    if key in licenses:
        if licenses[key]["hwid"] == hwid:
            return "valid"
        else:
            return "hwid_mismatch"
    return "invalid"
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid")

    if not key or not hwid:
        return "invalid"

    if key in licenses:
        if licenses[key]["hwid"] == hwid:
            return "valid"
        else:
            return "hwid_mismatch"
    return "invalid"

@app.route("/admin/add_key", methods=["POST"])
def add_key():
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid", "")
    if not key:
        return "Missing key", 400
    licenses[key] = {"hwid": hwid}
    save_licenses(licenses)
    return "added"

@app.route("/admin/revoke_key", methods=["POST"])
def revoke_key():
    data = request.get_json()
    key = data.get("key")
    if key in licenses:
        del licenses[key]
        save_licenses(licenses)
        return "revoked"
    return "not found", 404

@app.route("/admin/list_keys", methods=["GET"])
def list_keys():
    return jsonify(licenses)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
