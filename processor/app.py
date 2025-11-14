import json
import os
import time
import redis
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models import Base, Event

# config
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://analytics:analytics123@localhost:5432/analytics_db")
QUEUE_NAME = "events_queue"

# redis client
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=5)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

def wait_for_db(max_retries=10, retry_delay=2):
    """Wait for database to be ready"""
    import time
    from sqlalchemy.exc import OperationalError
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("Database connection successful!")
                return True
        except OperationalError as e:
            if attempt == max_retries - 1:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise
            print(f"Database not ready, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
    return False

def init_db():
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")

def parse_ts(ts_str):
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.utcnow()

def process_event_obj(obj):
    session = SessionLocal()
    try:
        e = Event(
            site_id=obj.get("site_id"),
            event_type=obj.get("event_type"),
            path=obj.get("path"),
            user_id=obj.get("user_id"),
            event_ts=parse_ts(obj.get("timestamp"))
        )
        session.add(e)
        session.commit()
    except Exception as ex:
        session.rollback()
        print("DB write failed:", ex)
    finally:
        session.close()

def run_worker():
    print("Processor starting; initializing DB...")
    init_db()
    print("Connected to Redis at", REDIS_HOST, REDIS_PORT)
    while True:
        try:
            item = r.brpop(QUEUE_NAME, timeout=5)
            if item:
                _, payload = item
                try:
                    obj = json.loads(payload)
                    process_event_obj(obj)
                except Exception as e:
                    print("Skipping invalid payload:", e)
            else:
                # no items, loop
                time.sleep(0.1)
        except Exception as e:
            print("Processor error:", e)
            time.sleep(1)

if __name__ == "__main__":
    run_worker()
