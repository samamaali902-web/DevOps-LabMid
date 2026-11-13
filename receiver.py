from flask import Flask, request, jsonify
import json
import os
from pathlib import Path

app = Flask(__name__)

REPORT_FILE = Path(__file__).parent / "test-report.json"


@app.route("/", methods=["GET"])
def home():
    return "Assignment Report Receiver is running!"


@app.route("/report", methods=["POST"])
def receive_report():

    secret = os.environ.get("REPORT_TOKEN")

    if not secret:
        return jsonify({"error": "REPORT_TOKEN is not configured"}), 503

    received_token = request.headers.get("X-Report-Token")

    if received_token != secret:
        return jsonify({"error": "Unauthorized request"}), 401

    report = request.get_json(silent=True)

    if not isinstance(report, dict):
        return jsonify({"error": "Invalid JSON report"}), 400

    required_fields = [
        "repository",
        "branch",
        "commit_sha",
        "run_id",
        "timestamp",
        "tests",
        "total",
        "passed",
        "failed",
        "status"
    ]

    missing = [field for field in required_fields if field not in report]

    if missing:
        return jsonify({"error": "Missing fields", "fields": missing}), 400

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return jsonify({
        "message": "Report received successfully",
        "saved_file": str(REPORT_FILE)
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)