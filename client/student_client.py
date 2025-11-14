#!/usr/bin/env python3
"""
student_client.py

Student CLI that submits attendance to Flask server (Option B).
Features:
- Offline queueing to ~/offline_attendance_queue.json
- Submit immediately when online
- Auto-sync queued submissions when toggled online
- Can accept QR payload JSON pasted from Professor or fetch PNG then decode (manual)

Run:
    pip install -r requirements.txt
    python3 student_client.py --student-id 2022IMT-048 --server http://localhost:5000 --network offline
"""
import argparse, json, base64, requests, time
from pathlib import Path
from datetime import datetime, timezone

OFFLINE_PATH = Path.home() / "offline_attendance_queue.json"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def ensure_offline():
    if not OFFLINE_PATH.exists():
        OFFLINE_PATH.write_text(json.dumps([], indent=2))

def load_offline():
    ensure_offline()
    with open(OFFLINE_PATH, "r") as f:
        return json.load(f)

def save_offline(q):
    with open(OFFLINE_PATH, "w") as f:
        json.dump(q, f, indent=2)

def submit_to_server(server_url, submission):
    url = server_url.rstrip("/") + "/submit_attendance"
    try:
        r = requests.post(url, json=submission, timeout=5)
        return r.status_code, r.json()
    except Exception as e:
        return None, {"error": str(e)}

def auto_sync(server_url, student_id):
    q = load_offline()
    if not q:
        print("[*] Offline queue empty.")
        return
    remaining = []
    print(f"[*] Attempting to sync {len(q)} queued submissions...")
    for sub in q:
        if sub.get("student_id") != student_id:
            remaining.append(sub)
            continue
        code, resp = submit_to_server(server_url, sub)
        if code == 201 and resp.get("status") == "accepted":
            print(f"[+] Synced submission for session {sub['session_id']}")
        else:
            # keep if network error or invalid
            if code is None:
                print("[!] Network error while syncing:", resp.get("error"))
                remaining.append(sub)
            else:
                reason = resp.get("reason") or resp.get("error") or str(resp)
                print("[!] Server rejected during sync:", reason)
                # if duplicate, drop; else keep
                if reason == "duplicate submission":
                    print("[i] Dropping duplicate.")
                else:
                    remaining.append(sub)
    save_offline(remaining)
    print("[*] Sync finished. Remaining in queue:", len(remaining))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--student-id", required=True)
    p.add_argument("--server", default="http://localhost:5000")
    p.add_argument("--network", choices=["online", "offline"], default="online")
    args = p.parse_args()
    online = True if args.network == "online" else False
    ensure_offline()
    print(f"Student CLI started (student_id={args.student_id}) server={args.server} network={online}")
    while True:
        print("\\nOptions:\\n 1) Paste QR payload JSON\\n 2) Toggle network\\n 3) Show offline queue\\n 4) Force sync\\n 5) Exit")
        c = input("Choose: ").strip()
        if c == "1":
            qr = input("Paste QR payload JSON: ").strip()
            if not qr:
                continue
            try:
                qr_obj = json.loads(qr)
                payload_b64 = qr_obj["payload_b64"]
                signature = qr_obj["signature"]
                payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
            except Exception as e:
                print("Invalid payload:", e)
                continue
            submission = {
                "student_id": args.student_id,
                "session_id": json.loads(payload_json)["session_id"],
                "payload": payload_json,
                "signature": signature,
                "submitted_at": now_iso()
            }
            if not online:
                q = load_offline()
                q.append(submission)
                save_offline(q)
                print("[+] Saved to offline queue.")
            else:
                code, resp = submit_to_server(args.server, submission)
                if code == 201 and resp.get("status") == "accepted":
                    print("[+] Submission accepted. latency:", resp.get("latency_seconds"))
                else:
                    print("[!] Submission failed:", resp)
        elif c == "2":
            online = not online
            print("Network toggled. Now online=", online)
            if online:
                auto_sync(args.server, args.student_id)
        elif c == "3":
            q = load_offline()
            print(json.dumps(q, indent=2))
        elif c == "4":
            if online:
                auto_sync(args.server, args.student_id)
            else:
                print("Currently offline. Toggle to online to sync.")
        elif c == "5":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
