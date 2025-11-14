from fastapi import FastAPI, HTTPException, status
import redis, os, json
from models import Event

app = FastAPI(title="Ingestion Service")

QUEUE_NAME = "events_queue"

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.post("/event", status_code=status.HTTP_202_ACCEPTED)
def post_event(ev: Event):
    payload = ev.model_dump()
    try:
        redis_client.lpush(QUEUE_NAME, json.dumps(payload))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"queue_error: {e}")
    return {"status": "accepted"}
