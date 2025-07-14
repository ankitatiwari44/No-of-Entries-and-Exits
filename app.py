import cv2
import streamlit as st
import tempfile
import time
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from mongo_logger import log_event
from notifier import send_notification
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os
import numpy as np

# Load YOLO + DeepSORT
model = YOLO('yolov8s.pt')
tracker = DeepSort(max_age=60, n_init=3, max_cosine_distance=0.3)

st.set_page_config(layout="wide")
st.title("People Entry/Exit Counter")

video_file = st.file_uploader(" Upload a video", type=["mp4", "avi", "mov"])
run_button = st.button(" Start Counting")
FRAME_WINDOW = st.image([])

# Init counters and memory
entry_count = exit_count = 0
track_history = {}
track_flags = {}
track_timestamps = {}

if video_file and run_button:
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(video_file.read())
    cap = cv2.VideoCapture(temp_file.name)

    line_x = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2
    line_y = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)[0]
        detections = []
        for det in results.boxes.data.tolist():
            x1, y1, x2, y2, score, cls = det
            if int(cls) == 0 and score > 0.4:
                detections.append(([x1, y1, x2 - x1, y2 - y1], score, 'person'))

        tracks = tracker.update_tracks(detections, frame=frame)

        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            x1, y1, x2, y2 = map(int, track.to_ltrb())
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if track_id not in track_history:
                track_history[track_id] = []
            track_history[track_id].append((cx, cy))

            if track_id not in track_flags:
                track_flags[track_id] = {"entered": False, "exited": False}

            if track_id not in track_timestamps:
                track_timestamps[track_id] = {}

            name = f"ID {track_id}"

            if len(track_history[track_id]) >= 2:
                prev_x, prev_y = track_history[track_id][-2]
                dx = abs(cx - prev_x)
                dy = abs(cy - prev_y)

                if dx > dy:
                    if prev_x < line_x and cx >= line_x and not track_flags[track_id]["entered"]:
                        entry_time = datetime.now()
                        entry_count += 1
                        track_flags[track_id]["entered"] = True
                        track_timestamps[track_id]['entry'] = entry_time
                        log_event("entry", name, entry_time)
                        send_notification("Entry")
                    elif prev_x > line_x and cx <= line_x and track_flags[track_id]["entered"] and not track_flags[track_id]["exited"]:
                        exit_time = datetime.now()
                        if 'entry' in track_timestamps[track_id] and exit_time > track_timestamps[track_id]['entry']:
                            exit_count += 1
                            track_flags[track_id]["exited"] = True
                            log_event("exit", name, exit_time)
                            send_notification("Exit")
                else:
                    if prev_y < line_y and cy >= line_y and not track_flags[track_id]["entered"]:
                        entry_time = datetime.now()
                        entry_count += 1
                        track_flags[track_id]["entered"] = True
                        track_timestamps[track_id]['entry'] = entry_time
                        log_event("entry", name, entry_time)
                        send_notification("Entry")
                    elif prev_y > line_y and cy <= line_y and track_flags[track_id]["entered"] and not track_flags[track_id]["exited"]:
                        exit_time = datetime.now()
                        if 'entry' in track_timestamps[track_id] and exit_time > track_timestamps[track_id]['entry']:
                            exit_count += 1
                            track_flags[track_id]["exited"] = True
                            log_event("exit", name, exit_time)
                            send_notification("Exit")

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.putText(frame, f'Entry: {entry_count}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f'Exit: {exit_count}', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        time.sleep(0.03)

    cap.release()

    st.markdown(f"""
        ###  Final Counts  
        - Entry: `{entry_count}`  
        - Exit: `{exit_count}`
    """)

# ========== View MongoDB Logs ==========
with st.expander(" View MongoDB Logs"):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['people_counter']
    collection = db['entries_exits']
    logs = list(collection.find({}, {"_id": 0}))
    if logs:
        df = pd.DataFrame(logs)

        # Ensure timestamp column is all datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.sort_values(by='timestamp', key=lambda col: pd.to_datetime(col, errors='coerce'), ascending=False)

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No logs found.")