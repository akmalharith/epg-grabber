import requests
from typing import List
from pathlib import Path
from datetime import datetime, timedelta
from pytz import timezone
from helper.utils import get_channel_by_name, get_epg_datetime
from helper.classes import Channel, Program
from sites.auth.playtv_unifi_auth import get_session
from config.env import playtv_unifi_device_id

session_headers = get_session()

ALL_CHANNEL_URL = "https://playtv.unifi.com.my:7047/VSP/V3/QueryAllChannel"
PROGRAM_DETAILS_URL = "https://playtv.unifi.com.my:7047/VSP/V3/GetPlaybillDetail?SID=playbilldetail3&DEVICE=PC&DID={device_id}".format(
    device_id=playtv_unifi_device_id)
PROGRAMS_URL = "https://playtv.unifi.com.my:7047/VSP/V3/QueryPlaybillList"


def get_all_channels() -> List[Channel]:
    query_url = ALL_CHANNEL_URL

    try:
        r = requests.post(query_url, cookies=session_headers)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    output = r.json()
    if r.status_code != 200:
        raise Exception(r.raise_for_status())
    if output["result"]["retCode"] != "000000000":
        raise Exception(output["result"]["retMsg"])

    channel_jsons = output["channelDetails"]

    channels = [Channel(
        channel["ID"],
        channel["name"] + ".My",
        channel["name"],
        channel["logo"]["url"],
        True) for channel in channel_jsons]

    return channels


def get_program_details(program_id: str) -> str:
    program_details_url = PROGRAM_DETAILS_URL
    program_info = {
        "playbillID": str(program_id),
        "isReturnAllMedia": "1",
        "queryDynamicRecmContent": {
            "recmScenarios": [
                {
                    "count": "12",
                    "offset": "0",
                    "contentType": "PROGRAM",
                    "contentID": program_id,
                    "entrance": "CatchupTV_Similar_Recommendations",
                    "businessType": "CUTV"}]}}

    r = requests.post(program_details_url,
                      cookies=session_headers, json=program_info)

    output = r.json()

    if r.status_code != 200:
        return ""

    if output["result"]["retCode"] != "000000000":
        return ""

    return output["playbillDetail"]["introduce"]


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    days = args[0] if args else 1

    start_temp = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = int(start_temp.timestamp() * 1000)

    end_temp = start_temp + timedelta(days=days)
    end_time = int(end_temp.timestamp() * 1000)

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    programs_url = PROGRAMS_URL
    channel_info = {
        "queryChannel": {
            "subjectID": "-1",
            "contentType": "CHANNEL",
            "channelIDs": [channel.id],
            "isReturnAllMedia": "1",
            "channelFilter": {}},
        "needChannel": "0",
        "queryPlaybill": {
            "startTime": start_time,
            "endTime": end_time,
            "count": "100",
            "offset": "0",
            "type": "0",
            "isFillProgram": "1"}}

    r = requests.post(programs_url, cookies=session_headers, json=channel_info)

    output = r.json()

    programs = []

    if r.status_code != 200:
        programs.append(Program())
        return programs
    if output["result"]["retCode"] != "000000000":
        programs.append(Program())
        return programs

    program_json = output["channelPlaybills"][0]["playbillLites"]

    for program in program_json:

        start_timestamp = int(int(program["startTime"]) / 1000)
        start_program = datetime.fromtimestamp(
            start_timestamp, timezone("UTC"))

        end_timestamp = int(int(program["endTime"]) / 1000)
        end_program = datetime.fromtimestamp(end_timestamp, timezone("UTC"))

        obj = Program(
            channel_name=channel.tvg_id,
            title=program["name"],
            description=get_program_details(program["ID"]),
            start=get_epg_datetime(start_program),
            stop=get_epg_datetime(end_program)
        )
        programs.append(obj)

    return programs
