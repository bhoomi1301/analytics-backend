from pydantic import BaseModel, Field, validator
from datetime import datetime

class Event(BaseModel):
    site_id: str = Field(..., example="site-abc-123")
    event_type: str = Field(..., example="page_view")
    path: str | None = Field(None, example="/pricing")
    user_id: str | None = Field(None, example="user-xyz-789")
    timestamp: str = Field(..., example="2025-11-12T19:30:01Z")

    @validator("timestamp")
    def validate_ts(cls, v):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except Exception:
            raise ValueError("timestamp must be ISO8601, e.g. 2025-11-12T19:30:01Z")