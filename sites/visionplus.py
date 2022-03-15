import json
import xmltodict
import requests
import re
from pytz import timezone
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime, timedelta
from common.classes import Channel, Program
from common.utils import get_channelid_by_name, get_epg_time
from sites.auth.visionplus_auth import get_token

# Get access token
token = get_token()

ALL_CHANNELS_URL = "https://www.visionplus.id/sitemap-channels.xml"


def get_all_channels():
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
            channel_id,
            channel_display_name+".Id",
            channel_display_name,
            channel_logo
        )

        channels.append(obj)

    return channels


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_today = date.today()

    channel_id = get_channelid_by_name(channel_name, "visionplus")
    all_programs = []

    for i in range(days):
        date_input = date_today + timedelta(days=i)
        channel_url = "https://web-api.visionplus.id/api/v10/epg?start_time_from={date_input}&channel_ids={channel_id}&lang=en".format(
            date_input=date_input, channel_id=channel_id)

        r = requests.get(channel_url, headers={"authorization": token})

        if r.status_code != 200:
            return [Program()]

        programs = []

        output = r.json()

        if "data" in output:
            schedules = output["data"][0]["schedules"][0]["items"]

        for schedule in schedules:
            program_url = schedule["mpd"]
            parsed_url = urlparse(program_url)

            start_timestamp = int(parse_qs(parsed_url.query)["begin"][0])
            start_program = datetime.fromtimestamp(
                start_timestamp, timezone("UTC"))
            end_timestamp = int(parse_qs(parsed_url.query)["begin"][0])
            end_program = datetime.fromtimestamp(
                end_timestamp, timezone("UTC"))

            obj = Program(
                channel_name,
                schedule["t"],
                schedule["synopsis"],
                get_epg_time(start_program),
                get_epg_time(end_program),
                ""
            )
            programs.append(obj)
        all_programs.extend(programs)

    return all_programs
