from pathlib import Path
from typing import List
import requests
import urllib3
from datetime import date, timedelta, datetime
from models.tvg import Channel, Program
from helper.utils import get_channel_by_name, get_epg_datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIMEZONE_OFFSET = "+0800"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_all_channels() -> List[Channel]:
    query_url = "https://rtm.glueapi.io/v3/epg?limit=100"

    try:
        r = requests.get(query_url, verify=False)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()
    output = output["data"]

    channels = [
        Channel(
            id=channel["id"],
            tvg_id=channel["channel"] + ".My",
            tvg_name=channel["channel"],
            tvg_logo="",  # TODO: Fix this
        )
        for channel in output
    ]

    return channels


def get_programs_by_channel(channel_name: str, days: int = 1) -> List[Program]:
    days = 7 if days > 7 else days

    date_today = date.today()

    date_start = date_today
    date_end = date_today + timedelta(days=days - 1)

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    programs = []
    channel_url = f"https://rtm.glueapi.io/v3/epg/{channel.id}/ChannelSchedule?dateStart={date_start}&dateEnd={date_end}&timezone=+08:00&embed=author,program"

    try:
        r = requests.get(channel_url, verify=False)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()

    schedules = output["schedule"]

    for schedule in schedules:
        start_time = datetime.strptime(schedule["dateTimeStart"], DATETIME_FORMAT)
        end_time = datetime.strptime(schedule["dateTimeEnd"], DATETIME_FORMAT)

        object = Program(
            channel_name=channel.tvg_id,
            title=schedule["scheduleProgramTitle"],
            description=schedule["scheduleProgramDescription"],
            start=get_epg_datetime(start_time, TIMEZONE_OFFSET),
            stop=get_epg_datetime(end_time, TIMEZONE_OFFSET),
        )

        programs.append(object)

    return programs
