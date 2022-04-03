from typing import Dict
import requests


def get_session() -> Dict[str, str]:
    auth_url = "https://api.redbull.tv/v3/session?os_family=http"

    try:
        r = requests.get(auth_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    output = r.json()

    session_headers = {"authorization": output["token"]}

    return session_headers
