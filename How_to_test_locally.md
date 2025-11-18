


## NOW TO MAKE START SERVER 
 ## Step1
Open new terminal
go to backend
   pip install -r requirements.txt
then  
  python server.py
   (it will run server on 5000)
   
 ## NOW TO MAKE SESSION AS PROFESSOR FOR A CLASS (students can mark attendance)
 ## Step2
further open new terminal and create a session using post request 
 
     curl -X POST http://localhost:5000/create_session \
       -H "Content-Type: application/json" \
        -d '{"course":"Networks","duration_minutes":20}'


## NOW OUR  SESSION IS MADE , NOW WE HAVE TO SUBMIT ATTENDANCE AS A STUDENT
 ## Step3
open new terminal
Go to your client folder:
python student_client.py --student-id 2022IMT-048 --server http://localhost:5000 --network online

You will see a menu:
1) Paste QR payload JSON
2) Toggle network
3) Show offline queue
4) Force sync
5) Exit

 Choose 1  ans paste from  output of Step 2 or  ask from professor(as real scenario)

{"payload_b64":"eyJjb3Vyc2UiOiAiTmV0d29ya3MiLCAiZHVyYXRpb25fbWludXRlcyI6IDIwLCAic2Vzc2lvbl9pZCI6ICI2OWQyMGFlZS05ZjVlLTQxNWItYTI3Mi00YWZlZDBlYjBhMzQiLCAic3RhcnRfdGltZSI6ICIyMDI1LTExLTE0VDA4OjM4OjU4LjgyMTExMCswMDowMCJ9","signature":"3cbc15f7db564b2dc8df05b0308af7923445f8d500df3dc99de20189095761ef"}


You should now get:

[+] Submission accepted. latency: X.XX

🎉 SUCCESS!

## For professor to see attendance 
Method 1 — View Attendance in Browser (EASIEST)

Open your browser and go to:

http://localhost:5000/attendance/69d20aee-9f5e-415b-a272-4afed0eb0a34

This is the session_id from your create_session output:

