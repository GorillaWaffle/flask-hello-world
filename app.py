from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes

@app.route("/proxy/submit", methods=["POST"])
def proxy_submit():
    ipa = request.files.get("ipa")
    mobileprovision = request.files.get("mobileprovision")
    p12 = request.files.get("p12")
    password = request.form.get("password")

    # Validate inputs
    if not ipa or not mobileprovision or not p12:
        return jsonify({"error": "Missing one or more files: ipa, mobileprovision, p12"}), 400
    if password is None:
        return jsonify({"error": "Missing password"}), 400

    # Reset stream position to start for each file
    ipa.stream.seek(0)
    mobileprovision.stream.seek(0)
    p12.stream.seek(0)

    files = {
        "ipa": (ipa.filename, ipa.stream, ipa.mimetype),
        "mobileprovision": (mobileprovision.filename, mobileprovision.stream, mobileprovision.mimetype),
        "p12": (p12.filename, p12.stream, p12.mimetype),
    }
    data = {"password": password}

    try:
        resp = requests.post("https://signer.apptesters.org/submit", files=files, data=data)
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "text/plain")
        )
    except requests.RequestException as e:
        return jsonify({"error": "Failed to forward request", "details": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
