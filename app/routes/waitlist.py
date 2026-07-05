from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from fastapi import Header
from app.config import ADMIN_API_KEY

from app.database import get_db
from app.models import Waitlist
from app.services.email import (
    send_waitlist_email,
    send_owner_waitlist_notification,
)

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


class WaitlistRequest(BaseModel):
    email: EmailStr
    discord: str | None = None


def verify_admin(x_admin_key: str | None = Header(default=None)):
    if not ADMIN_API_KEY or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

def send_waitlist_emails(email: str, discord: str | None):
    try:
        send_waitlist_email(email)
    except Exception as e:
        print("WAITLIST EMAIL FAILED:", str(e))

    try:
        send_owner_waitlist_notification(email, discord)
    except Exception as e:
        print("OWNER WAITLIST EMAIL FAILED:", str(e))


@router.post("/join")
def join_waitlist(
    body: WaitlistRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email = body.email.lower().strip()
    discord = body.discord.strip() if body.discord else None

    existing = db.query(Waitlist).filter(Waitlist.email == email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already joined waitlist")

    entry = Waitlist(
        email=email,
        discord=discord,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    background_tasks.add_task(send_waitlist_emails, email, discord)

    return {
        "success": True,
        "message": "You joined the Sanity RC waitlist",
        "id": entry.id,
    }


@router.get("/all")
def get_waitlist(
    db : Session = Depends(get_db),
    admin: None = Depends(verify_admin)
):
    entries = db.query(Waitlist).order_by(Waitlist.created_at.desc()).all()

    return [
        {
            "id": entry.id,
            "email": entry.email,
            "discord": entry.discord,
            "created_at": entry.created_at,
        }
        for entry in entries
    ]

@router.get("/test-email")
def test_waitlist_email():
    send_waitlist_email("sanityrcinfo@gmail.com")
    send_owner_waitlist_notification("sanityrcinfo@gmail.com", "xmrtj")

    return {
        "success": True,
        "message": "Test waitlist emails sent"
    }

@router.delete("/delete")
def delete_waitlist_email(
    email: EmailStr,
    db: Session = Depends(get_db),
    admin: None = Depends(verify_admin),
):
    entry = db.query(Waitlist).filter(Waitlist.email == email.lower().strip()).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Email not found")

    db.delete(entry)
    db.commit()

    return {"success": True, "message": f"{email} deleted from waitlist"}