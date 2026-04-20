# lms_producer.py
import json
import time
import random
from datetime import datetime, timezone
from azure.eventhub import EventHubProducerClient, EventData
from faker import Faker
from dotenv import load_dotenv
import os

load_dotenv()

fake = Faker()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
# Mirror real OULAD student IDs — producer uses a sampled subset
STUDENT_IDS = random.sample(range(6516, 2000000), 500)

# Mirror real OULAD course module codes
COURSE_IDS = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"]

# Synthetic instructor IDs — OULAD has no instructors; we derive them
# One instructor per course (7 courses = 7 instructors)
INSTRUCTOR_MAP = {course: f"INST_{i:03d}" for i, course in enumerate(COURSE_IDS, 1)}

EVENT_TYPES = [
    "login",
    "lecture_viewed",
    "quiz_attempted",
    "quiz_completed",
    "assignment_submitted",
    "attendance_marked",
    "forum_post",
    "feedback_submitted",
]

# Realistic score ranges per event type
SCORE_EVENTS = {"quiz_attempted", "quiz_completed", "assignment_submitted"}

# Realistic duration ranges (seconds) per event type
DURATION_MAP = {
    "login":                (5, 30),
    "lecture_viewed":       (300, 3600),
    "quiz_attempted":       (120, 1800),
    "quiz_completed":       (120, 1800),
    "assignment_submitted": (600, 7200),
    "attendance_marked":    (1, 10),
    "forum_post":           (60, 600),
    "feedback_submitted":   (30, 300),
}

def generate_event():
    course_id = random.choice(COURSE_IDS)
    event_type = random.choice(EVENT_TYPES)
    
    # Weight: at-risk students produce fewer events
    student_id = random.choice(STUDENT_IDS)
    
    event = {
        "student_id":     student_id,
        "course_id":      course_id,
        "instructor_id":  INSTRUCTOR_MAP[course_id],
        "event_type":     event_type,
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "session_id":     fake.uuid4(),
        "duration_sec":   random.randint(*DURATION_MAP[event_type]),
        "score":          round(random.uniform(20, 100), 1) if event_type in SCORE_EVENTS else None,
        "status":         random.choice(["completed", "partial", "abandoned"])
                          if event_type in {"quiz_attempted", "assignment_submitted"}
                          else "completed",
        "source":         "lms_simulator_v1",
    }
    return event

def run_producer(events_per_batch=5, interval_sec=3):
    producer = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STRING)
    total_sent = 0

    print(f"Producer started. Sending {events_per_batch} events every {interval_sec}s. Ctrl+C to stop.\n")

    try:
        while True:
            with producer:
                producer = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STRING)
                batch = producer.create_batch()
                
                for _ in range(events_per_batch):
                    event = generate_event()
                    batch.add(EventData(json.dumps(event)))
                
                producer.send_batch(batch)
                total_sent += events_per_batch
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent {events_per_batch} events | Total: {total_sent}")
            
            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print(f"\nProducer stopped. Total events sent: {total_sent}")

if __name__ == "__main__":
    run_producer(events_per_batch=5, interval_sec=3)