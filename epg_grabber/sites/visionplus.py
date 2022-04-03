import json
from typing import List
import xmltodict
import requests
import re
from pathlib import Path
from pytz import timezone
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime, timedelta

from sites.auth.visionplus_auth import get_token
from helper.classes import Channel, Program
from helper.utils import get_channel_by_name, get_epg_datetime


# Get access token
headers = get_token()

ALL_CHANNELS_URL = "https://www.visionplus.id/sitemap-channels.xml"
PROGRAMS_URL = "https://web-api.visionplus.id/api/v10/epg?start_time_from={date_input}&channel_ids={channel_id}&lang=en"


def get_all_channels() -> List[Channel]:
    response = requests.get(ALL_CHANNELS_URL)

    data_dict = xmltodict.parse(response.text)
    json_data = json.dumps(data_dict)
    json_dict = json.loads(json_data)
    channels_raw = json_dict["urlset"]["url"]

    channels = []

    for channel in channels_raw:
        metadata = re.match(
            "https://www.visionplus.id/channel/(.*)",
            channel["loc"]).group(1).split("/")
        channel_id = metadata[0]
        metadata[1]
        channel_display_name = channel["video:video"]["video:title"]
        channel_logo = channel["video:video"]["video:thumbnail_loc"]

        obj = Channel(
            id = channel_id,
            tvg_id = channel_display_name + ".Id",
            tvg_name = channel_display_name,
            tvg_logo = channel_logo,
            sanitize = True
        )

        channels.append(obj)

    return channels


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_today = date.today()

    channel = get_channel_by_name(channel_name, Path(__file__).stem)
    all_programs = []

    for i in range(days):
        date_input = date_today + timedelta(days=i)
        channel_url = PROGRAMS_URL.format(
            date_input=date_input, channel_id=channel.id)

        r = requests.get(channel_url, headers=headers)

        if r.status_code != 200:
            break

        programs = []

        output = r.json()

        if "data" in output:
            output_inner = output["data"][0]
        else:
            break

        if "schedules" not in output_inner:
            break
        else:
            schedules = output_inner["schedules"][0]["items"]

        for schedule in schedules:
            program_url = schedule["mpd"]
            parsed_url = urlparse(program_url)

            start_timestamp = int(parse_qs(parsed_url.query)["begin"][0])
            start_program = datetime.fromtimestamp(
                start_timestamp, timezone("UTC"))
            end_timestamp = int(parse_qs(parsed_url.query)["end"][0])
            end_program = datetime.fromtimestamp(
                end_timestamp, timezone("UTC"))

            obj = Program(
                channel_name = channel.tvg_id,
                title = schedule["t"],
                description = schedule["synopsis"],
                start = get_epg_datetime(start_program),
                stop = get_epg_datetime(end_program)
            )
            programs.append(obj)
        all_programs.extend(programs)

    return all_programs
