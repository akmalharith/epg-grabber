import json
from typing import List
import requests
from pathlib import Path
from datetime import date, datetime, timedelta
from helper.utils import get_channel_by_name, get_epg_datetime
from helper.classes import Channel, Program

ALL_CHANNELS_URL = "https://www.mewatch.sg/channel-guide"
PROGRAMS_URL = "https://cdn.mewatch.sg/api/schedules?channels={channel_id}&date={date}&duration=24&hour=16&segments=all"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def get_all_channels() -> List[Channel]:
    try:
        response = requests.get(ALL_CHANNELS_URL)
    except requests.RequestException as e:
        raise SystemExit(e)

    web_page = response.text
    start_tag = "window.__data"

    matched_line = [line for line in web_page.split(
        "\n") if start_tag in line][0]
    matched_line_inner = matched_line.split("</script>")[1]

    to_remove = """<!-- '"´ --><script nonce="_">window.__data = """

    output = json.loads(matched_line_inner.replace(to_remove, ""))

    channels_raw = output["cache"]["list"]["137962|page_size=24"]["list"]["items"]

    channels = [Channel(
        id=channel["id"],
        tvg_id=channel["title"] + ".Sg",
        tvg_name=channel["title"],
        tvg_logo=channel["images"]["square"],
        sanitize=True
    ) for channel in channels_raw]

    return channels


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_today = date.today() - timedelta(days=1)
    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    all_programs = []
    for i in range(days):
        date_input = date_today + timedelta(days=i)
        channel_url = PROGRAMS_URL.format(
            channel_id=channel.id, date=date_input)

        r = requests.get(channel_url)

        if r.status_code != 200:
            return [Program()]

        output = r.json()
        schedules = output[0]["schedules"]

        programs = []

        for schedule in schedules:

            start_program = datetime.strptime(
                schedule["startDate"], DATETIME_FORMAT)
            end_program = datetime.strptime(
                schedule["endDate"], DATETIME_FORMAT)

            obj = Program(
                channel.tvg_id,
                schedule["item"]["title"],
                schedule["item"]["description"],
                get_epg_datetime(start_program),
                get_epg_datetime(end_program),
                ""
            )
            programs.append(obj)

        all_programs.extend(programs)

    return all_programs
