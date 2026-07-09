import os
import secrets
import requests
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models import User, License
from app.services.security import decode_token

router = APIRouter(prefix="/admin", tags=["Admin Invites"])


class InviteAdminRequest(BaseModel):
    email: str


def get_current_user(
    authorization: str = Header(default=None, alias="authorization"),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def send_license_email(email: str, license_key: str):
    resend_api_key = os.getenv("RESEND_API_KEY")

    if not resend_api_key:
        raise HTTPException(status_code=500, detail="RESEND_API_KEY missing")

    register_link = f"https://sanityrc.com/register?license={license_key}"

    res = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Sanity RC <noreply@sanityrc.com>",
            "to": [email],
            "subject": "Your Sanity RC Lifetime Admin Access",
            "html": f"""
                <h1>Sanity RC Admin Access</h1>
                <p>You have been invited as an admin.</p>
                <p><b>Lifetime License Key:</b></p>
                <h2>{license_key}</h2>
                <p>Register here:</p>
                <a href="{register_link}">{register_link}</a>
            """,
        },
        timeout=20,
    )

    if res.status_code >= 400:
        raise HTTPException(status_code=500, detail=res.text)


@router.post("/invite")
def invite_admin(
    body: InviteAdminRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role.lower() != "owner":
        raise HTTPException(status_code=403, detail="Only owner can invite admins")

    license_key = f"ADMIN-LIFETIME-{secrets.token_hex(6).upper()}"

    license = License(
        license_key=license_key,
        owner=body.email,
        role="Admin",
        active=True,
        claimed=False,
        claimed_by_user_id=None,
        plan="lifetime_admin",
        created_at=datetime.now(timezone.utc),
    )

    db.add(license)
    db.commit()

    send_license_email(body.email, license_key)

    return {
        "success": True,
        "message": "Admin lifetime license sent.",
        "email": body.email,
        "license_key": license_key,
    }