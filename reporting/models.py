from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class PathView(BaseModel):
    path: str
    views: int

class AnalyticsResponse(BaseModel):
    site_id: str
    date: Optional[date] = None
    total_views: int
    unique_users: int
    top_paths: List[PathView]