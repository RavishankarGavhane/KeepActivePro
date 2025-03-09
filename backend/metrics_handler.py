from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import VisitorMetrics


router = APIRouter()


# Increment Visitor Count
@router.post("/track-visitor")
def track_visitor(db: Session = Depends(get_db)):
    metrics = db.query(VisitorMetrics).first()
    if not metrics:
        metrics = VisitorMetrics(visitor_count=1, download_count=0)
        db.add(metrics)
    else:
        metrics.visitor_count += 1
    db.commit()
    db.refresh(metrics)  # ✅ Refresh to get updated values
    return {"message": "Visitor tracked", "visitor_count": metrics.visitor_count}


# Increment Download Count
@router.post("/track-download")
def track_download(db: Session = Depends(get_db)):
    metrics = db.query(VisitorMetrics).first()
    if not metrics:
        metrics = VisitorMetrics(visitor_count=0, download_count=1)
        db.add(metrics)
    else:
        metrics.download_count += 1
    db.commit()
    db.refresh(metrics)  # ✅ Refresh to get updated values
    return {"message": "Download tracked", "download_count": metrics.download_count}
