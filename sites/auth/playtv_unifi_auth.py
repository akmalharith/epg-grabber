import requests
import os
from dotenv import load_dotenv

load_dotenv()

user_id = os.environ["PLAYTV_UNIFI_USER_ID"]
password = os.environ["PLAYTV_UNIFI_PASSWORD"]
device_id = os.environ["PLAYTV_UNIFI_DEVICE_ID"]


def get_session():
    auth_url = "https://playtv.unifi.com.my:7047/VSP/V3/Authenticate"

    try:
        r = requests.post(auth_url, json={
            "authenticateBasic": {
                "userID": user_id,
                "userType": "1",
                "timeZone": "Asia/Brunei",
                "isSupportWebpImgFormat": "0",
                "clientPasswd": password,
                "lang": "en"
            },
            "authenticateDevice": {
                "physicalDeviceID": device_id,
                "terminalID": device_id,
                "deviceModel": "PC Web TV"
            },
            "authenticateTolerant": {
                "areaCode": "1200",
                "templateName": "default",
                "bossID": "",
                "userGroup": "-1"
            }
        })
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    output = r.json()

    if output["result"]["retCode"] != "000000000":
        raise Exception(output["result"]["retMsg"])

    session_headers = r.cookies.get_dict()

    return session_headers
