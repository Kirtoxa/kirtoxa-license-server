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

@app.route('/admin/add_key', methods=['POST'])
def add_key():
    data = request.get_json()
    key = data['key']
    expires = data.get('expires', None)

    with open(LICENSE_FILE) as f:
        licenses = json.load(f)

    licenses[key] = {
        "created": int(time.time()),
        "expires": expires,
        "revoked": False
    }

    with open(LICENSE_FILE, 'w') as f:
        json.dump(licenses, f, indent=2)

    return jsonify({"status": "added"})

@app.route('/admin/revoke_key', methods=['POST'])
def revoke_key():
    data = request.get_json()
    key = data['key']

    with open(LICENSE_FILE) as f:
        licenses = json.load(f)

    if key in licenses:
        licenses[key]['revoked'] = True
        with open(LICENSE_FILE, 'w') as f:
            json.dump(licenses, f, indent=2)
        return jsonify({"status": "revoked"})
    return jsonify({"status": "not_found"})

@app.route('/admin/reset_hwid', methods=['POST'])
def reset_hwid():
    data = request.get_json()
    key = data['key']

    with open(LICENSE_FILE) as f:
        licenses = json.load(f)

    if key in licenses and 'hwid' in licenses[key]:
        del licenses[key]['hwid']
        with open(LICENSE_FILE, 'w') as f:
            json.dump(licenses, f, indent=2)
        return jsonify({"status": "reset"})
    return jsonify({"status": "not_found"})

@app.route('/admin/list_keys', methods=['GET'])
def list_keys():
    with open(LICENSE_FILE) as f:
        licenses = json.load(f)

    response = []
    for key, info in licenses.items():
        status = "revoked" if info.get("revoked") else "valid"
        if info.get("expires") and time.time() > info["expires"]:
            status = "expired"
        response.append({
            "key": key,
            "hwid": info.get("hwid"),
            "expires": info.get("expires"),
            "status": status
        })
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
