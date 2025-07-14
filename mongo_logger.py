from pymongo import MongoClient

def log_event(event_type, track_id, timestamp=None):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["people_counter"]
    collection = db["entries_exits"]

    event = {
        "type": event_type,
        "track_id": track_id
    }

    if timestamp:
        event["timestamp"] = timestamp

    collection.insert_one(event)

