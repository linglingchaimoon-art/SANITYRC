from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

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


@router.post("/join")
def join_waitlist(body: WaitlistRequest, db: Session = Depends(get_db)):
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

    try:
        send_waitlist_email(email)
    except Exception as e:
        print("WAITLIST EMAIL FAILED:", str(e))

    try:
        send_owner_waitlist_notification(email, discord)
    except Exception as e:
        print("OWNER WAITLIST EMAIL FAILED:", str(e))

    return {
        "success": True,
        "message": "You joined the Sanity RC waitlist",
        "id": entry.id,
    }


@router.get("/all")
def get_waitlist(db: Session = Depends(get_db)):
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