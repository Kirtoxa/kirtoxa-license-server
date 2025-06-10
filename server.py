
from flask import Flask, request
import json

app = Flask(__name__)

# Load licenses from file
def load_licenses():
    try:
        with open("licenses.json", "r") as f:
            return json.load(f)
    except:
        return {}

licenses = load_licenses()

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
    else:
        return "invalid"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
