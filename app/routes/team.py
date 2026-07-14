from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import License, User
from app.services.security import decode_token

router = APIRouter(prefix="/team", tags=["Team Management"])

ALLOWED_STAFF_ROLES = {
    "ADMIN",
    "MODERATOR",
    "SUPPORT",
    "EVENT_MANAGER",
    "DEVELOPER",
}


class UpdateRoleRequest(BaseModel):
    role: str


class UpdateActiveRequest(BaseModel):
    active: bool


def get_current_user(
    authorization: str = Header(default=None, alias="authorization"),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = authorization.replace("Bearer ", "").strip()
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get("user_id")).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return user


def require_owner(user: User):
    if str(user.role).upper() != "OWNER":
        raise HTTPException(
            status_code=403,
            detail="Only the owner can manage the team.",
        )


def get_team_member(db: Session, owner: User, member_id: int):
    member = (
        db.query(User)
        .filter(
            User.id == member_id,
            User.owner_user_id == owner.id,
            User.id != owner.id,
        )
        .first()
    )

    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return member


@router.get("/members")
def list_team_members(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_owner(user)

    members = (
        db.query(User)
        .filter(User.owner_user_id == user.id, User.id != user.id)
        .order_by(User.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "members": [
            {
                "id": member.id,
                "email": member.email,
                "role": member.role,
                "active": member.active,
                "is_staff": member.is_staff,
                "owner_user_id": member.owner_user_id,
                "created_at": member.created_at,
                "last_login": getattr(member, "last_login", None),
            }
            for member in members
        ],
    }


@router.get("/pending")
def list_pending_invites(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_owner(user)

    pending = (
        db.query(License)
        .filter(
            License.plan == "lifetime_admin",
            License.claimed.is_(False),
            License.active.is_(True),
        )
        .order_by(License.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "invites": [
            {
                "id": invite.id,
                "email": invite.owner,
                "license_key": invite.license_key,
                "role": invite.role,
                "active": invite.active,
                "claimed": invite.claimed,
                "created_at": invite.created_at,
            }
            for invite in pending
        ],
    }


@router.patch("/members/{member_id}/role")
def update_member_role(
    member_id: int,
    body: UpdateRoleRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_owner(user)

    member = get_team_member(db, user, member_id)
    new_role = body.role.strip().upper()

    if new_role not in ALLOWED_STAFF_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported staff role.",
        )

    member.role = new_role
    member.is_staff = True

    db.commit()
    db.refresh(member)

    return {
        "success": True,
        "message": "Team member role updated.",
    }


@router.patch("/members/{member_id}/active")
def update_member_active(
    member_id: int,
    body: UpdateActiveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_owner(user)

    member = get_team_member(db, user, member_id)
    member.active = body.active

    db.commit()
    db.refresh(member)

    return {
        "success": True,
        "message": "Team member enabled." if member.active else "Team member disabled.",
    }


@router.delete("/members/{member_id}")
def remove_team_member(
    member_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_owner(user)

    member = get_team_member(db, user, member_id)

    member.active = False
    member.is_staff = False
    member.owner_user_id = None
    member.role = "USER"

    db.commit()

    return {
        "success": True,
        "message": "Team member removed.",
    }


@router.delete("/pending/{license_id}")
def revoke_pending_invite(
    license_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_owner(user)

    license_data = (
        db.query(License)
        .filter(
            License.id == license_id,
            License.plan == "lifetime_admin",
            License.claimed.is_(False),
        )
        .first()
    )

    if not license_data:
        raise HTTPException(
            status_code=404,
            detail="Pending invitation not found",
        )

    license_data.active = False
    db.commit()

    return {
        "success": True,
        "message": "Pending invitation revoked.",
    }
