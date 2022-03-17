import requests
from config.env import playtv_unifi_user_id, playtv_unifi_password, playtv_unifi_device_id


def get_session():
    auth_url = "https://playtv.unifi.com.my:7047/VSP/V3/Authenticate"

    try:
        r = requests.post(auth_url, json={
            "authenticateBasic": {
                "userID": playtv_unifi_user_id,
                "userType": "1",
                "timeZone": "Asia/Brunei",
                "isSupportWebpImgFormat": "0",
                "clientPasswd": playtv_unifi_password,
                "lang": "en"
            },
            "authenticateDevice": {
                "physicalDeviceID": playtv_unifi_device_id,
                "terminalID": playtv_unifi_device_id,
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
