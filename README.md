# People Entry/Exit Counter 

This project is a real-time people counting application that tracks how many people enter or exit a room using computer vision. It uses YOLOv8 for person detection, DeepSORT for tracking, and logs each entry/exit event in MongoDB. A Streamlit dashboard provides an interactive user interface.


##  Features

- Detects and tracks people using YOLOv8 + DeepSORT
- Works with both horizontal and vertical entry/exit directions
- Logs events (entry/exit with timestamp and ID) to MongoDB
- Displays live annotated video and count in Streamlit UI
- View logs directly from the UI
- Sends notifications (via your `notifier.py` logic)

## Models 
(YOLO + DeepSORT + Streamlit + MongoDB)

