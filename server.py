from flask import Flask, request, jsonify, send_from_directory
import json, time, os

app = Flask(__name__, static_folder='.')

LICENSE_FILE = 'licenses.json'

if not os.path.exists(LICENSE_FILE):
    with open(LICENSE_FILE, 'w') as f:
        json.dump({}, f, indent=2)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    key = data.get('key')
    hwid = data.get('hwid')
    now = int(time.time())

    with open(LICENSE_FILE) as f:
        licenses = json.load(f)

    if key in licenses:
        entry = licenses[key]
        if entry.get('revoked'):
            return jsonify({"status": "revoked"})
        if entry.get('expires') and now > entry['expires']:
            return jsonify({"status": "expired"})
        if 'hwid' not in entry:
            licenses[key]['hwid'] = hwid
        elif entry['hwid'] != hwid:
            return jsonify({"status": "hwid_mismatch"})

        with open(LICENSE_FILE, 'w') as f:
            json.dump(licenses, f, indent=2)
        return jsonify({"status": "valid"})
    return jsonify({"status": "invalid"})
