                 ┌───────────────────────────┐
                 │      Professor Client      │
                 └──────────────┬────────────┘
                                │
                                │  POST /create_session
                                ▼
                     ┌───────────────────────────────┐
                     │           Flask Server         │
                     ├────────────────────────────────┤
                     │ • Generate session_id          │
                     │ • Create server_secret         │
                     │ • Build payload_json           │
                     │ • Compute HMAC signature       │
                     │ • Store session in DB          │
                     └───────────────┬────────────────┘
                                     │  QR JSON (payload_b64 + signature)
                                     ▼
                         ┌──────────────────────────────┐
                         │           QR Code             │
                         │  (PNG or JSON for sharing)    │
                         └───────────────┬──────────────┘
                                         │  Student scans
                                         ▼
                           ┌───────────────────────────┐
                           │       Student Client       │
                           ├───────────────────────────┤
                           │ Decodes QR payload         │
                           │ Builds submission JSON     │
                           └──────────────┬────────────┘
                                          │
                           ┌──────────────┴──────────────┐
                           │           Network?           │
                           └───────┬───────────┬─────────┘
                                   │           │
                                   ▼           ▼
                          ONLINE (Direct)   OFFLINE
                     ┌──────────────────┐   ┌─────────────────────────┐
                     │ POST /submit_    │   │ Save submission locally │
                     │ attendance        │   │   to offline queue      │
                     └───────┬──────────┘   └─────────────┬──────────┘
                             │                            │
                             ▼                            │
                ┌───────────────────────────┐             │
                │         Flask Server       │             │
                ├───────────────────────────┤             │
                │ • Verify HMAC signature   │             │
                │ • Validate session_id     │             │
                │ • Check duplicate entry   │             │
                │ • Compute latency         │             │
                │ • Store attendance record │             │
                └───────────────┬───────────┘             │
                                ▼                          │
                ┌──────────────────────────────────────┐   │
                │       Attendance Stored in DB        │   │
                └──────────────────────────────────────┘   │
                                                           │
                                           ┌───────────────┘
                                           ▼
                         ┌──────────────────────────────────────┐
                         │    Student Client Auto-Sync Logic    │
                         ├──────────────────────────────────────┤
                         │ On reconnect → send queued items      │
                         │     to POST /submit_attendance        │
                         │ Server validates each submission      │
                         │ Removes synced items from queue       │
                         └──────────────────────────────────────┘
