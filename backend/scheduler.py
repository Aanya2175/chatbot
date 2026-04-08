from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()
pending = {}  # session_id -> [messages]

def start():
    scheduler.start()

def add_reminder(session_id: str, message: str, interval_minutes: int = 1440):
    job_id = f"{session_id}_{datetime.now().timestamp()}"
    scheduler.add_job(
        func=_queue_reminder,
        trigger="interval",
        minutes=interval_minutes,
        id=job_id,
        args=[session_id, message]
    )

def _queue_reminder(session_id: str, message: str):
    pending.setdefault(session_id, []).append(message)

def pop_reminders(session_id: str):
    msgs = pending.get(session_id, [])
    pending[session_id] = []
    return msgs
def _queue_reminder(session_id: str, message: str):
    print(f"DEBUG - queuing reminder for {session_id}: {message}")
    pending.setdefault(session_id, []).append(message)