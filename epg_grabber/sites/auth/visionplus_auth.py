from typing import Dict
import requests


def get_token() -> Dict[str, str]:
    token = requests.get(
        "https://web-api.visionplus.id/api/v1/visitor").json()["data"]["access_token"]

    return {"authorization": token}
