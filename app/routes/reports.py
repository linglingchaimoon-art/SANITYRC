from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report
from app.config import PRIVATE_API_KEY

from app.services.live import live_manager
import asyncio

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportCreate(BaseModel):
    server_name: str | None = None
    reporter_discord: str
    target_player: str
    reason: str
    evidence: str | None = None


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.post("/create")
def create_report(
    body: ReportCreate,
    x_api_key: str = Header(alias="x-api-key"),
    db: Session = Depends(get_db),
):
    check_key(x_api_key)

    report = Report(
        server_name=body.server_name,
        reporter_discord=body.reporter_discord,
        target_player=body.target_player,
        reason=body.reason,
        evidence=body.evidence,
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    
    asyncio.create_task(
        live_manager.broadcast({
            "type": "report_created",
            "message": f"New report submitted against {report.target_player}.",
            "report_id": report.id,
        })
    )

    return {
        "success": True,
        "message": "Report submitted",
        "report_id": report.id,
    }


@router.get("/all")
def get_reports(
    x_api_key: str = Header(alias="x-api-key"),
    db: Session = Depends(get_db),
):
    check_key(x_api_key)

    reports = db.query(Report).order_by(Report.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "server_name": r.server_name,
            "reporter_discord": r.reporter_discord,
            "target_player": r.target_player,
            "reason": r.reason,
            "evidence": r.evidence,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in reports
    ]


@router.patch("/{report_id}/status")
def update_report_status(
    report_id: int,
    status: str,
    x_api_key: str = Header(alias="x-api-key"),
    db: Session = Depends(get_db),
):
    check_key(x_api_key)

    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = status
    db.commit()

    return {
        "success": True,
        "message": "Report status updated",
    }