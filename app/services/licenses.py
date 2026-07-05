VALID_LICENSES = {
    "SANITY2X-OWNER-KEY": {
        "owner": "TJ",
        "role": "Owner",
        "active": True
    },
    "SANITY2X-TEST-KEY": {
        "owner": "Test Admin",
        "role": "Admin",
        "active": True
    }
}


def check_license(key: str):
    license_data = VALID_LICENSES.get(key)

    if not license_data:
        return None

    if not license_data["active"]:
        return None

    return license_data