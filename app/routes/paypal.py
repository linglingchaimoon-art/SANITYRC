import random
import string
import requests

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import (
    PAYPAL_CLIENT_ID,
    PAYPAL_CLIENT_SECRET,
    PAYPAL_MODE,
    FRONTEND_URL,
)
from app.database import get_db
from app.models import License
from app.services.email import send_license_email

router = APIRouter(prefix="/paypal", tags=["PayPal"])


class PayPalOrderRequest(BaseModel):
    plan: str


class PayPalCaptureRequest(BaseModel):
    order_id: str


def paypal_base_url():
    return "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"


def generate_license_key():
    def part():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

    return f"RC-{part()}-{part()}-{part()}"


def get_paypal_access_token():
    res = requests.post(
        f"{paypal_base_url()}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        headers={"Accept": "application/json"},
    )

    if res.status_code >= 400:
        raise HTTPException(status_code=500, detail=res.text)

    return res.json()["access_token"]


@router.post("/create-order")
def create_paypal_order(body: PayPalOrderRequest):
    if body.plan == "monthly":
        amount = "9.99"
        name = "Sanity RC Monthly License"
    elif body.plan == "lifetime":
        amount = "49.99"
        name = "Sanity RC Lifetime License"
    else:
        raise HTTPException(status_code=400, detail="Invalid plan")

    token = get_paypal_access_token()

    res = requests.post(
        f"{paypal_base_url()}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "description": name,
                    "custom_id": body.plan,
                    "amount": {
                        "currency_code": "EUR",
                        "value": amount,
                    },
                }
            ],
            "application_context": {
                "brand_name": "Sanity RC",
                "landing_page": "LOGIN",
                "user_action": "PAY_NOW",
                "return_url": f"{FRONTEND_URL}/paypal-success",
                "cancel_url": f"{FRONTEND_URL}/",
            },
        },
    )

    if res.status_code >= 400:
        raise HTTPException(status_code=500, detail=res.text)

    data = res.json()

    approve_url = None
    for link in data.get("links", []):
        if link.get("rel") == "approve":
            approve_url = link.get("href")

    if not approve_url:
        raise HTTPException(status_code=500, detail="PayPal approval URL missing")

    return {
        "order_id": data["id"],
        "approve_url": approve_url,
    }


@router.post("/capture-order")
def capture_paypal_order(body: PayPalCaptureRequest, db: Session = Depends(get_db)):
    token = get_paypal_access_token()

    existing_license = (
        db.query(License)
        .filter(License.stripe_session_id == body.order_id)
        .first()
    )

    if existing_license:
        return {
            "license_key": existing_license.license_key,
            "email": existing_license.customer_email,
            "active": existing_license.active,
            "claimed": existing_license.claimed,
            "plan": existing_license.plan,
        }

    capture = requests.post(
        f"{paypal_base_url()}/v2/checkout/orders/{body.order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    if capture.status_code >= 400:
        print("PAYPAL CAPTURE FAILED:", capture.text)
        raise HTTPException(status_code=500, detail=capture.text)

    data = capture.json()

    purchase_unit = data["purchase_units"][0]
    capture_data = purchase_unit["payments"]["captures"][0]

    plan = purchase_unit.get("custom_id") or "lifetime"

    payer = data.get("payer", {})
    email = payer.get("email_address")

    license_key = generate_license_key()

    license = License(
        license_key=license_key,
        owner=None,
        role="Owner",
        active=True,
        claimed=False,
        claimed_by_user_id=None,
        stripe_session_id=body.order_id,
        stripe_subscription_id=None,
        customer_email=email,
        plan=plan,
    )

    db.add(license)
    db.commit()
    db.refresh(license)

    if email:
        try:
            send_license_email(email, license_key)
        except Exception as e:
            print("PAYPAL EMAIL SEND FAILED:", str(e))

    print("NEW PAYPAL LICENSE CREATED:", license_key)

    return {
        "license_key": license.license_key,
        "email": license.customer_email,
        "active": license.active,
        "claimed": license.claimed,
        "plan": license.plan,
        "paypal_capture_id": capture_data.get("id"),
    }