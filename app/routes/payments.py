import random
import string

import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, FRONTEND_URL
from app.database import get_db
from app.models import License
from app.services.email import send_license_email

router = APIRouter(prefix="/payments", tags=["Payments"])

stripe.api_key = STRIPE_SECRET_KEY


class CheckoutRequest(BaseModel):
    plan: str


def generate_license_key():
    def part():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

    return f"RC-{part()}-{part()}-{part()}"


def create_license_for_session(session, db: Session, source: str):
    session_id = session.id

    existing_license = (
        db.query(License)
        .filter(License.stripe_session_id == session_id)
        .first()
    )

    if existing_license:
        return existing_license

    customer_email = None
    if session.customer_details:
        customer_email = session.customer_details.email

    plan = (
        session.metadata["plan"]
        if session.metadata and "plan" in session.metadata
        else "lifetime"
    )

    subscription_id = session.subscription if hasattr(session, "subscription") else None

    license_key = generate_license_key()

    new_license = License(
        license_key=license_key,
        owner=None,
        role="Owner",
        active=True,
        claimed=False,
        claimed_by_user_id=None,
        stripe_session_id=session_id,
        stripe_subscription_id=subscription_id,
        customer_email=customer_email,
        plan=plan,
    )

    db.add(new_license)
    db.commit()
    db.refresh(new_license)

    print(f"NEW LICENSE CREATED FROM {source}:", license_key)

    if customer_email:
        try:
            send_license_email(customer_email, license_key)
        except Exception as e:
            print("EMAIL SEND FAILED:", str(e))

    return new_license


@router.post("/create-checkout")
def create_checkout(body: CheckoutRequest):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe secret key missing")

    if body.plan == "monthly":
        mode = "subscription"
        price_data = {
            "currency": "eur",
            "product_data": {
                "name": "Sanity RC Monthly License",
            },
            "unit_amount": 999,
            "recurring": {
                "interval": "month",
            },
        }

    elif body.plan == "lifetime":
        mode = "payment"
        price_data = {
            "currency": "eur",
            "product_data": {
                "name": "Sanity RC Lifetime License",
            },
            "unit_amount": 4999,
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid plan")

    checkout_data = {
        "mode": mode,
        "payment_method_types": ["card"],
        "line_items": [
            {
                "price_data": price_data,
                "quantity": 1,
            }
        ],
        "metadata": {
            "plan": body.plan,
        },
        "success_url": f"{FRONTEND_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{FRONTEND_URL}/",
    }

    if mode == "payment":
        checkout_data["customer_creation"] = "always"

    session = stripe.checkout.Session.create(**checkout_data)

    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid webhook signature: {str(e)}",
        )

    if event["type"] == "checkout.session.completed":
        session_id = event["data"]["object"]["id"]
        session = stripe.checkout.Session.retrieve(session_id)
        create_license_for_session(session, db, "WEBHOOK")

    return {"success": True}


@router.get("/license")
def get_license(session_id: str, db: Session = Depends(get_db)):
    license = (
        db.query(License)
        .filter(License.stripe_session_id == session_id)
        .first()
    )

    if license:
        return {
            "license_key": license.license_key,
            "email": license.customer_email,
            "active": license.active,
            "claimed": license.claimed,
            "plan": license.plan,
        }

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Stripe session not found")

    if session.payment_status != "paid":
        raise HTTPException(status_code=404, detail="Payment not completed yet")

    license = create_license_for_session(session, db, "SUCCESS PAGE")

    return {
        "license_key": license.license_key,
        "email": license.customer_email,
        "active": license.active,
        "claimed": license.claimed,
        "plan": license.plan,
    }