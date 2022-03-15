import requests
import urllib3
from datetime import date, timedelta, datetime
from common.classes import Channel, Program
from common.utils import get_channelid_by_name, get_epg_time
from sites.astro import ALL_CHANNELS_URL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ALL_CHANNELS_URL = "https://rtmklik.rtm.gov.my/bs-api/RTM(epg)/channels"
PROGRAMS_URL = "https://rtmklik.rtm.gov.my/bs-api/RTM(epg)/channels/{channel_id}/epg?date={date}"
TIMEZONE_OFFSET = "+0800"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_all_channels():
    query_url = ALL_CHANNELS_URL

    try:
        r = requests.get(query_url, verify=False)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    output = r.json()

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    channels = [Channel(
        channel['id'],
        channel['title']+".My",
        channel['title'],
        channel['imageUrls'][0]
    ) for channel in output]

    return channels


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_today = date.today()
    all_programs = []

    for i in range(days):
        date_input = date_today + timedelta(days=i)
        channel_id = get_channelid_by_name(channel_name, "myklik_rtm")
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
                channel_name,
                schedule['title'],
                schedule['description'],
                get_epg_time(start_time, TIMEZONE_OFFSET),
                get_epg_time(end_time, TIMEZONE_OFFSET),
                ""
            )
            programs.append(obj)
        all_programs.extend(programs)

    return all_programs
