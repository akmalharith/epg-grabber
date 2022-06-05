from typing import Dict
import requests
from config.env import starhubtvplus_app_key, starhubtvplus_client_uuid
from config.constants import DEFAULT_USER_AGENT


def get_session() -> Dict[str, str]:
    try:
        response = requests.get(
            "https://api.one.accedo.tv/session?appKey={application_key}&uuid={uuid}".format(
                application_key=starhubtvplus_app_key,
                uuid=starhubtvplus_client_uuid))
    except Exception as e:
        raise(e)
    output = response.json()

    return {
        "x-application-session": output["sessionKey"],
        "x-application-key": starhubtvplus_app_key +
        "_" +
        starhubtvplus_client_uuid,
        "User-Agent": DEFAULT_USER_AGENT}
