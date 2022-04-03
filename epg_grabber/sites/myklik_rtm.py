from pathlib import Path
from typing import List
import requests
import urllib3
from datetime import date, timedelta, datetime
from helper.classes import Channel, Program
from helper.utils import get_channel_by_name, get_epg_datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ALL_CHANNELS_URL = "https://rtmklik.rtm.gov.my/bs-api/RTM(epg)/channels"
PROGRAMS_URL = "https://rtmklik.rtm.gov.my/bs-api/RTM(epg)/channels/{channel_id}/epg?date={date}"
TIMEZONE_OFFSET = "+0800"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_all_channels() -> List[Channel]:
    query_url = ALL_CHANNELS_URL

    try:
        r = requests.get(query_url, verify=False)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    output = r.json()

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    channels = [Channel(
        id=channel['id'],
        tvg_id=channel['title'] + ".My",
        tvg_name=channel['title'],
        tvg_logo=channel['imageUrls'][0],
        sanitize=True
    ) for channel in output]

    return channels


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_today = date.today()
    all_programs = []

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    for i in range(days):
        date_input = date_today + timedelta(days=i)
        channel_id = channel.id
        channel_url = PROGRAMS_URL.format(
            channel_id=channel_id, date=date_input)

        try:
            r = requests.get(channel_url, verify=False)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        if r.status_code != 200:
            raise Exception(r.raise_for_status())

        schedules = r.json()
        programs = []

        for schedule in schedules:
            start_time = datetime.strptime(schedule['start'], DATETIME_FORMAT)
            end_time = datetime.strptime(schedule['end'], DATETIME_FORMAT)

            obj = Program(
                channel_name=channel.tvg_id,
                title=schedule['title'],
                description=schedule['description'],
                start=get_epg_datetime(start_time, TIMEZONE_OFFSET),
                stop=get_epg_datetime(end_time, TIMEZONE_OFFSET)
            )
            programs.append(obj)
        all_programs.extend(programs)

    return all_programs
