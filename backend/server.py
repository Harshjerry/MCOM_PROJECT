#!/usr/bin/env python3
"""
server.py

Flask backend for QR Attendance Tracker (Option B)
Endpoints:
 - POST /create_session        -> create a session (professor)
 - GET  /qr/<session_id>.png   -> return PNG QR for session (optional)
 - POST /submit_attendance     -> accept student submissions
 - GET  /attendance/<session_id> -> list accepted attendance

Storage: server_sessions.json (sessions + attendance)
Security: HMAC-SHA256 signature verification using server_secret stored per-session

Run:
    pip install -r requirements.txt
    python3 server.py
"""
from flask import Flask, request, jsonify, send_file, abort
import json, uuid, secrets, hmac, hashlib, base64, io
from datetime import datetime, timezone
from pathlib import Path

try:
    import qrcode
except Exception:
    qrcode = None

APP = Flask(__name__)
DB_PATH = Path("server_sessions.json")
def ensure_db():
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"sessions": [], "attendance": []}, indent=2))

def load_db():
    ensure_db()
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def make_signature(secret: str, message: str) -> str:
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

def verify_signature(secret: str, message: str, signature: str) -> bool:
    expected = make_signature(secret, message)
    return hmac.compare_digest(expected, signature)

@APP.route("/create_session", methods=["POST"])
def create_session():
    data = request.get_json(force=True)
    course = data.get("course", "Course-101")
    duration = int(data.get("duration_minutes", 15))
    session_id = str(uuid.uuid4())
    start_time = now_iso()
    payload_obj = {"session_id": session_id, "start_time": start_time, "course": course, "duration_minutes": duration}
    payload_json = json.dumps(payload_obj, sort_keys=True)
    server_secret = secrets.token_hex(16)
    signature = make_signature(server_secret, payload_json)
    session = {
        "session_id": session_id,
        "start_time": start_time,
        "payload": payload_json,
        "signature": signature,
        "server_secret": server_secret,
        "generated_at": now_iso()
    }
    db = load_db()
    db["sessions"].append(session)
    save_db(db)
    # Build QR payload
    b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
    qr_payload = {"payload_b64": b64, "signature": signature}
    response = {"session_id": session_id, "qr_payload": qr_payload}
    return jsonify(response), 201

@APP.route("/qr/<session_id>.png", methods=["GET"])
def qr_png(session_id):
    db = load_db()
    sessions = {s["session_id"]: s for s in db.get("sessions", [])}
    if session_id not in sessions:
        abort(404, "session not found")
    session = sessions[session_id]
    payload_json = session["payload"]
    signature = session["signature"]
    b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
    qr_content = json.dumps({"payload_b64": b64, "signature": signature})
    if qrcode is None:
        abort(501, "qrcode library not installed")
    img = qrcode.make(qr_content)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name=f"qr_{session_id[:8]}.png")

@APP.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    submission = request.get_json(force=True)
    # basic validation
    required = ["student_id", "session_id", "payload", "signature", "submitted_at"]
    for r in required:
        if r not in submission:
            return jsonify({"status": "error", "reason": f"missing {r}"}), 400
    db = load_db()
    sessions = {s["session_id"]: s for s in db.get("sessions", [])}
    sid = submission["session_id"]
    if sid not in sessions:
        return jsonify({"status": "error", "reason": "unknown session_id"}), 404
    session = sessions[sid]
    payload = session["payload"]
    secret = session["server_secret"]
    if not verify_signature(secret, payload, submission.get("signature", "")):
        return jsonify({"status": "error", "reason": "invalid signature"}), 403
    # duplication
    attendance = db.get("attendance", [])
    key = (submission["student_id"], sid)
    seen = {(a["student_id"], a["session_id"]) for a in attendance}
    if key in seen:
        return jsonify({"status": "error", "reason": "duplicate submission"}), 409
    # latency
    start = datetime.fromisoformat(session["start_time"])
    submitted = datetime.fromisoformat(submission["submitted_at"])
    latency = (submitted - start).total_seconds()
    record = dict(submission)
    record["latency_seconds"] = latency
    attendance.append(record)
    db["attendance"] = attendance
    save_db(db)
    return jsonify({"status": "accepted", "latency_seconds": latency}), 201

@APP.route("/attendance/<session_id>", methods=["GET"])
def get_attendance(session_id):
    db = load_db()
    attendance = [a for a in db.get("attendance", []) if a["session_id"] == session_id]
    return jsonify({"session_id": session_id, "attendance": attendance})

if __name__ == "__main__":
    ensure_db()
    print("Starting server on http://0.0.0.0:5000")
    APP.run(host="0.0.0.0", port=5000, debug=True)
