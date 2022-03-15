import requests
from datetime import datetime, timedelta
from pytz import timezone
from source.classes import Channel, Program
from source.utils import get_epg_datetime

PROGRAMS_URL = "https://nwapi.nhk.jp/nhkworld/epg/v7b/world/s{start}-e{end}.json"


def get_all_channels():  # Hardcode since we are only dealing with one channel
    return [Channel("nhk", "nhk.Jp", "NHK World Japan", "")]


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    start_temp = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = int(start_temp.timestamp() * 1000)

    end_temp = start_temp + timedelta(days=days)
    end_time = int(end_temp.timestamp() * 1000)

    url = PROGRAMS_URL.format(start=start_time, end=end_time)

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()["channel"]["item"]

    programs = []

    for program in output:
        start_timestamp = int(int(program["pubDate"]) / 1000)
        start_program = datetime.fromtimestamp(
            start_timestamp, timezone("UTC"))

        end_timestamp = int(int(program["endDate"]) / 1000)
        end_program = datetime.fromtimestamp(end_timestamp, timezone("UTC"))

        obj = Program(
            get_all_channels()[0].tvg_id,
            program["title"],
            program["description"],
            get_epg_datetime(start_program),
            get_epg_datetime(end_program),
            ""
        )
        programs.append(obj)

    return programs
