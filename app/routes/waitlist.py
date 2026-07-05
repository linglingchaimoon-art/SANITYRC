from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Waitlist

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


class WaitlistRequest(BaseModel):
    email: EmailStr
    discord: str | None = None


@router.post("/join")
def join_waitlist(body: WaitlistRequest, db: Session = Depends(get_db)):
    email = body.email.lower().strip()

    existing = db.query(Waitlist).filter(Waitlist.email == email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already joined waitlist")

    entry = Waitlist(
        email=email,
        discord=body.discord,
    )

    db.add(entry)
    db.commit()

    return {
        "success": True,
        "message": "You joined the Sanity RC waitlist"
    }