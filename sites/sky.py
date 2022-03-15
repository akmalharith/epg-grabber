from pathlib import Path
import requests
from datetime import date, datetime, timedelta
from pytz import timezone
from common.utils import get_channel_by_name, get_epg_time
from common.classes import Channel, Program

ALL_CHANNELS_URL = "http://awk.epgsky.com/hawk/linear/services/4101/1"
PROGRAMS_URL = "https://awk.epgsky.com/hawk/linear/schedule/{date_str}/{channelId}"
CHANNEL_LOGO_PREFIX_URL = "https://d2n0069hmnqmmx.cloudfront.net/epgdata/1.0/newchanlogos/320/320/skychb"
DATETIME_FORMAT = "%Y%m%d"

def get_all_channels():
    query_url = ALL_CHANNELS_URL

    try:
        r = requests.get(query_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()
    channel_json = output["services"]

    channels = [Channel(
        channel["sid"],
        channel["t"]+".Uk",
        channel["t"],
        CHANNEL_LOGO_PREFIX_URL +
        channel["sid"] +
        ".png"
    ) for channel in channel_json]

    return channels


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_today = date.today()
    
    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    all_programs = []
    for i in range(days):
        date_input = date_today + timedelta(days=i)
        date_string = date_input.strftime(DATETIME_FORMAT)

        url = PROGRAMS_URL.format(date_str=date_string, channelId=channel.id)

        r = requests.get(url)

        programs = []
        if r.status_code != 200:
            return [Program()]

        schedules = r.json()["schedule"][0]["events"]
        for schedule in schedules:
            start_program = datetime.fromtimestamp(int(schedule["st"]), timezone("UTC"))
            end_program = start_program + timedelta(seconds=int(schedule["d"]))

            obj = Program(
                channel.tvg_id,
                schedule["t"],
                schedule["sy"],
                get_epg_time(start_program),
                get_epg_time(end_program),
                schedule["eid"].upper()
            )
            programs.append(obj)
        all_programs.extend(programs)

    return all_programs
