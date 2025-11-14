# QR Attendance Tracker — Option B (Flask server + Student HTTP client)

This folder contains a working server and student client for the QR Attendance Tracker (Option B).

Files created:
- server.py              : Flask backend (create_session, submit_attendance, qr PNG endpoint, attendance listing)
- student_client.py      : Student CLI that posts attendance and supports offline queueing and auto-sync
- requirements.txt       : Python dependencies
- server_sessions.json   : server database (sessions + attendance)

Quick start (local demo)
1. Create a virtualenv (recommended) and install deps:
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

2. Start server (runs on port 5000):
    python3 server.py

3. Create a session (Professor) — example using curl:
    curl -X POST http://localhost:5000/create_session -H "Content-Type: application/json" -d '{"course":"Networks","duration_minutes":20}'

   The server responds with JSON containing "session_id" and "qr_payload" (payload_b64 + signature).

4. Optionally download PNG QR:
    Open in browser: http://localhost:5000/qr/<session_id>.png
   (Requires qrcode library; otherwise use the qr_payload JSON string and any QR generator.)

5. Run student client:
    python3 student_client.py --student-id 2022IMT-048 --server http://localhost:5000 --network offline

   Paste the qr_payload JSON you received from /create_session into the student CLI when choosing "Paste QR payload JSON".
   If offline, the submission will be queued in ~/offline_attendance_queue.json. Toggle network to online to auto-sync.

Notes:
- server_sessions.json will contain sessions and attendance records.
- HMAC-SHA256 signature verification is performed on the server (server_secret stored per-session).
- Duplicate submissions (same student_id + session_id) are rejected.
