from typing import List
from epg_grabber.models import Programme
from datetime import date, datetime, timedelta

from requests import Session 
from random import randint

session = Session()
session.headers.update(
    {
        "Accept": "application/json",
        "Content-Type":  "application/json",
        "Origin": "https://playtv.unifi.com.my",
        "Referer": "https://playtv.unifi.com.my/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
)

device_id = randint(199000000, 799999000)

response = session.post('https://playtv.unifi.com.my/VSP/V3/Login?from=throughMSAAccess', json={
    "subscriberID": "",
    "deviceModel": "PC Web TV"
})

response.raise_for_status()

response = session.post('https://playtv.unifi.com.my:7053/VSP/V3/Authenticate?from=throughMSAAccess', json={
    "authenticateBasic": {
        "userID": "",
        "userType": "3",
        "isSupportWebpImgFormat": "0",
        "needPosterTypes": ["0", "1", "2", "3", "4", "5", "6", "7"],
        "timeZone": "Asia/Kuala_Lumpur"
    },
    "authenticateDevice": {
        "physicalDeviceID": device_id,
        "terminalID": device_id,
        "deviceModel": "PC Web TV"
    },
    "authenticateTolerant": {
        "areaCode": "",
        "templateName": "",
        "bossID": "",
        "userGroup": ""
    }
})

response.raise_for_status()

result = response.json()['result']

if result["retCode"] != "000000000":
    raise Exception(result['retMsg'])

def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:

    programmes: List[Programme] = []

    channel_name = channel_xml_id if channel_xml_id else channel_id

    for day in range(days):

        start_dt = date.today() + timedelta(days=day)
        start_date = datetime.combine(start_dt, datetime.min.time())
        start_timestamp_in_milliseconds = int(start_date.timestamp() * 1000)

        end_dt = start_dt + timedelta(days=day+1)
        end_date = datetime.combine(end_dt, datetime.max.time())
        end_timestamp_in_milliseconds = int(end_date.timestamp() * 1000)

        url = 'https://playtv.unifi.com.my:7053/VSP/V3/QueryPlaybillList?from=throughMSAAccess'
        payload = {
            "queryChannel": {"channelIDs": [channel_id]},
            "queryPlaybill": {
                "type": 0,
                "count": 100,
                "offset": 0,
                "isFillProgram": "1",
                "sortType": "STARTTIME:ASC",
                "startTime": start_timestamp_in_milliseconds,
                "endTime": end_timestamp_in_milliseconds
            }
        }

        response = session.post(url, json=payload)
        response.raise_for_status()

        result = response.json()['result']

        if result["retCode"] != "000000000":
            raise Exception(result['retMsg'])
        
        data = response.json()

        playbill_lites = data["channelPlaybills"][0]["playbillLites"]

        for item in playbill_lites:

            program = Programme(
                start=datetime.fromtimestamp(int(item['startTime']) / 1000),
                stop=datetime.fromtimestamp(int(item['endTime']) / 1000),
                channel=f"{item['channelID']}.unifi_com_my",
                title=item["name"],
                rating=item["rating"]["name"],
                desc=get_program_detail(playbill_id=item["ID"])
            )    

            programmes.append(program)

    return programmes

def get_program_detail(playbill_id: str) -> str:
    url = "https://playtv.unifi.com.my:7053/VSP/V3/GetPlaybillDetail?from=throughMSAAcces"

    response = session.post(url, json={
        "playbillID":playbill_id
    })
    response.raise_for_status()

    result = response.json()['result']

    if result["retCode"] != "000000000":
        raise Exception(result['retMsg'])
    
    data = response.json()

    try:
        return data["playbillDetail"]["introduce"]
    except KeyError:
        return ""
