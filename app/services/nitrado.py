import requests
from fastapi import HTTPException

from app.config import NITRADO_TOKEN, BASE_URL


def nitrado_request(method: str, endpoint: str, json=None):
    url = BASE_URL + endpoint

    headers = {
        "Authorization": f"Bearer {NITRADO_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("NITRADO REQUEST:", method, url)
    print("NITRADO BODY:", json)

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        timeout=30,
    )

    print("NITRADO STATUS:", response.status_code)
    print("NITRADO RESPONSE:", response.text)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )

    try:
        return response.json()
    except ValueError:
        return {
            "status": "success",
            "raw": response.text,
        }