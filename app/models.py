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

class Waitlist(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    discord = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ConnectedServer(Base):
    __tablename__ = "connected_servers"

    rcon_ip = Column(String, nullable=True)
    rcon_port = Column(Integer, nullable=True)
    rcon_password_encrypted = Column(String, nullable=True)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    server_name = Column(String)
    service_id = Column(String)
    nitrado_token_encrypted = Column(String)

    connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    server_name = Column(String, nullable=True)
    reporter_discord = Column(String)
    target_player = Column(String)
    reason = Column(String)
    evidence = Column(String, nullable=True)

    status = Column(String, default="open")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))