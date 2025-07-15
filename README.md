# People Entry/Exit Counter 

This project is a real-time people counting application that tracks how many people enter or exit a room using computer vision. It uses YOLOv8 for person detection, DeepSORT for tracking, and logs each entry/exit event in MongoDB. A Streamlit dashboard provides an interactive user interface.


##  Features

- Detects and tracks people using YOLOv8 + DeepSORT
- Works with both horizontal and vertical entry/exit directions
- Logs events (entry/exit with timestamp and ID) to MongoDB
- Displays live annotated video and count in Streamlit UI
- View logs directly from the UI
- Sends notifications (via your `notifier.py` logic)

## Technologies Used
                  Component	Purpose
YOLOv8 - Object Detection (detect people)
DeepSORT -	Object Tracking (track people)
OpenCV -	Frame-by-frame video processing
Streamlit -	Frontend UI 
MongoDB	- Persistent logging of events
Python - 	 code & logic implementation

## System Architecture
Video Upload or Stream
       ↓
   Frame-by-frame
       ↓
+-------------------+
| YOLOv8 detects    | → Bounding boxes for 'person'
| people in frame   |
+-------------------+
       ↓
+-------------------+
| DeepSORT assigns  | → Unique IDs to track people
| track_id to each  |
| person            |
+-------------------+
       ↓
Movement tracking →
       ↓
Cross center line? → Entry/Exit event
       ↓
+---------------------------+
| Streamlit UI (Live Video)|
| Display: Entry, Exit     |
+---------------------------+
       ↓
+---------------------------+
| MongoDB Logs              |
| entry/exit with time, ID  |
+---------------------------+
## Logic
Detect when a person enters or exits the room.
Detect People:Using YOLOv8 object detection model, which identifies only persons (class 0).

Track People:DeepSORT tracker assigns a track ID to each detected person, which remains the same across frames.

Monitor Movement Direction:For each person (track_id), we store their past positions (center of the bounding box).
If they move left → right or top → bottom, we treat that as entry.
If they move right → left or bottom → top, we treat that as exit.

Log Entry and Exit:When a person enters, we log their track ID and datetime.now() as entry time.
When the same person exits, we check that exit time > entry time, and log it.

## Counters
entry_count = exit_count = 0
These are incremented only when valid entry/exit is detected and not duplicated.

We also maintain dictionaries:
track_history = {}        # Position history
track_flags = {}          # Flags to prevent duplicate logging
track_timestamps = {}     # To store entry timestamps

## MongoDB Logging
We log each event like:
{
  "event": "entry",
  "track_id": "ID 4",
  "timestamp": "2025-07-15T10:34:00"
}
A custom function log_event(event_type, track_id, timestamp) inserts this into MongoDB.

Later, Streamlit shows this in a dataframe using:
with st.expander("View MongoDB Logs"):
    ...
    st.dataframe(df)

## Streamlit UI Features
Upload any .mp4, .avi, .mov video.

Click Start Counting.

See video frames with bounding boxes and track IDs.

see live counters
<img width="1739" height="638" alt="image" src="https://github.com/user-attachments/assets/9fca97f2-3ea7-4685-acb2-15429357d714" />
<img width="490" height="159" alt="image" src="https://github.com/user-attachments/assets/f3f495ae-d1f9-47fa-9fbf-91978fd9a16c" />
<img width="1821" height="771" alt="image" src="https://github.com/user-attachments/assets/e5132dc3-1e87-45f4-8eae-a7fd0861aad0" />
<img width="1779" height="857" alt="image" src="https://github.com/user-attachments/assets/c1920ed5-a5dd-46a7-8648-26e199f56ea7" />



