from epg_grabber.models import Programme, ChannelMetadata, Channel
from pytz import timezone
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime, timedelta
from typing import List
import json
import xmltodict
import requests
import re

ALL_CHANNELS_URL = 'https://www.visionplus.id/sitemap-channels.xml'
PROGRAMS_URL = 'https://web-api.visionplus.id/api/v10/epg'
VISITOR_API_URL = 'https://web-api.visionplus.id/api/v1/visitor'

session = requests.Session()

token = session.get(VISITOR_API_URL).json()['data']['access_token']
headers = {'authorization': token}


def generate() -> ChannelMetadata:
    response = session.get(ALL_CHANNELS_URL)

    data_dict = xmltodict.parse(response.text)
    json_data = json.dumps(data_dict)
    json_dict = json.loads(json_data)
    channels_raw = json_dict["urlset"]["url"]

    channels = []

    for channel in channels_raw:
        metadata = (
            re.match("https://www.visionplus.id/channel/(.*)", channel["loc"])
            .group(1)
            .split("/")
        )
        channel_id = metadata[0]
        metadata[1]
        channel_display_name = channel["video:video"]["video:title"]
        channel_logo = channel["video:video"]["video:thumbnail_loc"]

        obj = Channel(
            id=channel_id,
            display_name=channel_display_name,
            icon=channel_logo,
        )

        channels.append(obj)

    channels_metadata = ChannelMetadata(channels=channels)

    return channels_metadata


def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    date_today = date.today()

    for i in range(days):
        date_input = date_today + timedelta(days=i)

        try:
            response = session.get(PROGRAMS_URL,
                                   params={
                                       'start_time_from': date_input,
                                       'channel_ids': channel_id,
                                       'lang': 'en'
                                   },
                                   headers=headers)
        except Exception as e:
            raise e

        output = response.json()

        if 'data' not in output:
            continue

        output = output['data'][0]
        schedules = output['schedules'][0]['items']

        for schedule in schedules:
            program_url = schedule["mpd"]

            parsed_url = urlparse(program_url)

            start_timestamp = int(parse_qs(parsed_url.query)["begin"][0])
            start_program = datetime.fromtimestamp(
                start_timestamp, timezone("UTC"))
            end_timestamp = int(parse_qs(parsed_url.query)["end"][0])
            end_program = datetime.fromtimestamp(
                end_timestamp, timezone("UTC"))

            prog_obj = Programme(
                start=start_program,
                stop=end_program,
                channel=channel_name,
                title=schedule["t"],
                desc=schedule["synopsis"]
            )

            programmes.append(prog_obj)

    return programmes
