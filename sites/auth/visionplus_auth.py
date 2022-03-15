import requests


def get_token():
    return requests.get(
        "https://web-api.visionplus.id/api/v1/visitor").json()["data"]["access_token"]
