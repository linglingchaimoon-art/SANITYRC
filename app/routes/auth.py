from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, License
from app.services.security import (
    hash_password,
    verify_password,
    create_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    license_key: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    license_key = body.license_key.strip().upper()

    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    license_data = (
        db.query(License)
        .filter(License.license_key == license_key)
        .first()
    )

    if not license_data:
        raise HTTPException(status_code=401, detail="Invalid license key")

    if not license_data.active:
        raise HTTPException(status_code=403, detail="License is inactive")

    if license_data.claimed:
        raise HTTPException(status_code=400, detail="License already claimed")

    user = User(
        email=email,
        password_hash=hash_password(body.password),
        role=license_data.role or "Owner",
        active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    license_data.claimed = True
    license_data.claimed_by_user_id = user.id
    license_data.owner = user.email

    db.commit()

    token = create_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    })

    return {
        "success": True,
        "message": "Account created and license claimed",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
        "license": {
            "license_key": license_data.license_key,
            "active": license_data.active,
            "claimed": license_data.claimed,
        }
    }


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    email = body.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = create_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    })

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    }


@router.get("/me")
def me(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    license_data = (
        db.query(License)
        .filter(License.claimed_by_user_id == user.id)
        .first()
    )

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "active": user.active,
        },
        "license": {
            "license_key": license_data.license_key if license_data else None,
            "active": license_data.active if license_data else False,
            "claimed": license_data.claimed if license_data else False,
            "plan": "Professional",
            "servers": "1 / 3",
            "expires": "Lifetime",
        }
    }