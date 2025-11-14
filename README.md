# QR Attendance Tracker


                 ┌───────────────────────────┐
                 │      Professor Client     │
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
                         │           QR Code            │
                         │  (PNG or JSON for sharing)   │
                         └───────────────┬──────────────┘
                                         │  Student scans
                                         ▼
                           ┌───────────────────────────┐
                           │       Student Client      │
                           ├───────────────────────────┤
                           │ Decodes QR payload        │
                           │ Builds submission JSON    │
                           └──────────────┬────────────┘
                                          │
                           ┌──────────────┴──────────────┐
                           │           Network?          │
                           └───────┬───────────┬─────────┘
                                   │           │
                                   ▼           ▼
                          ONLINE (Direct)   OFFLINE
                     ┌──────────────────┐   ┌────────────────────────┐
                     │ POST /submit_    │   │ Save submission locally│
                     │ attendance       │   │   to offline queue     │
                     └───────┬──────────┘   └─────────────┬──────────┘
                             │                            │
                             ▼                            │
                ┌───────────────────────────┐             │
                │         Flask Server      │             │
                ├───────────────────────────┤             │
                │ • Verify HMAC signature   │             │
                │ • Validate session_id     │             │
                │ • Check duplicate entry   │             │
                │ • Compute latency         │             │
                │ • Store attendance record │             │
                └───────────────┬───────────┘             │
                                ▼                         │
                ┌──────────────────────────────────────┐  │
                │       Attendance Stored in DB        │  │
                └──────────────────────────────────────┘  │
                                                          │
                                           ┌───────────────
                                           ▼
                         ┌──────────────────────────────────────┐
                         │    Student Client Auto-Sync Logic    │
                         ├──────────────────────────────────────┤
                         │ On reconnect → send queued items     │
                         │     to POST /submit_attendance       │
                         │ Server validates each submission     │
                         │ Removes synced items from queue      │
                         └──────────────────────────────────────┘

## START SERVER
<img width="1088" height="515" alt="Starting_Server" src="https://github.com/user-attachments/assets/3a9afef5-f194-4b1b-b278-4de46b9ee4de" />

## MAKE SESSION AS PROFESSOR (TAKE NOTE OF SESSION ID  AND SIGNATURE)

<img width="1520" height="324" alt="Creating_Session_AS_Professor" src="https://github.com/user-attachments/assets/d997240e-e269-422b-ab84-97b103c731fa" />

## MARK ATTENDANCE AS STUDENT USIGN QR  Signature

<img width="772" height="333" alt="Student_Marking_Attendance" src="https://github.com/user-attachments/assets/d6fa91c9-ae5f-46bf-84be-6ba0b1b6bb78" />

## Check Attendance as professor on browser

<img width="1733" height="719" alt="Attendance" src="https://github.com/user-attachments/assets/b452f051-b0fc-4a58-9ac7-f161ea99164f" />



