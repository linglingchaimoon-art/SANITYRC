from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

from app.database import Base


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String, unique=True, index=True)
    owner = Column(String, nullable=True)
    role = Column(String, default="Owner")
    active = Column(Boolean, default=True)

    claimed = Column(Boolean, default=False)
    claimed_by_user_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    stripe_session_id = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)

    plan = Column(String, default ="lifetime")
    stripe_subscription_id = Column(String, nullable=True)


class PanelLog(Base):
    __tablename__ = "panel_logs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    role = Column(String)
    admin = Column(String)
    action = Column(String)
    success = Column(Boolean, default=True)
    message = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="Owner")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))