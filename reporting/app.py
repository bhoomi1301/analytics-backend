from fastapi import FastAPI, HTTPException
from typing import Optional, List
from datetime import datetime, date
import os
from sqlalchemy import create_engine, text
from models import AnalyticsResponse, PathView

app = FastAPI(title="Reporting Service")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://analytics:analytics123@localhost:5432/analytics_db")
engine = create_engine(DATABASE_URL)

@app.get("/stats")
def get_stats(site_id: str, date: Optional[str] = None):
    if not site_id:
        raise HTTPException(status_code=400, detail="site_id is required")
    params = {"site_id": site_id}
    where = " WHERE site_id = :site_id "
    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
        except Exception:
            raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")
        where += " AND event_ts >= :start_ts AND event_ts < :end_ts "
        params["start_ts"] = f"{date} 00:00:00+00"
        params["end_ts"] = f"{date} 23:59:59+00"

    q_total = text(f"SELECT COUNT(*) AS total_views FROM events {where};")
    q_unique = text(f"SELECT COUNT(DISTINCT user_id) AS unique_users FROM events {where} AND user_id IS NOT NULL;")
    q_top = text(f"SELECT COALESCE(path,'/') AS path, COUNT(*) AS views FROM events {where} GROUP BY path ORDER BY views DESC LIMIT 10;")

    with engine.connect() as conn:
        try:
            total = conn.execute(q_total, params).scalar_one()
            unique = conn.execute(q_unique, params).scalar_one()
            top_rows = conn.execute(q_top, params).fetchall()
            top_paths = [PathView(path=r[0], views=int(r[1])) for r in top_rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return AnalyticsResponse(
        site_id=site_id,
        date=date,
        total_views=int(total),
        unique_users=int(unique),
        top_paths=top_paths
    )
