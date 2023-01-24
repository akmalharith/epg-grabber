from epg_grabber.models import Programme, ChannelMetadata, Channel
from typing import List
from datetime import date, datetime, timedelta
import requests
import json

ALL_CHANNELS_URL = "https://www.mewatch.sg/channel-guide"
PROGRAMS_URL = 'https://cdn.mewatch.sg/api/schedules'
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

session = requests.Session()


def generate() -> ChannelMetadata:
    try:
        response = session.get(ALL_CHANNELS_URL)
    except session.RequestException as e:
        raise e

    web_page = response.text
    start_tag = "window.__data"

    matched_line = [line for line in web_page.split(
        "\n") if start_tag in line][0]
    matched_line_inner = matched_line.split("</script>")[1]

    to_remove = """<!-- '"´ --><script nonce="_">window.__data = """

    output = json.loads(matched_line_inner.replace(to_remove, ""))

    channels_raw = output["cache"]["list"]["137962|page_size=24"]["list"]["items"]

    channels = [
        Channel(
            id=channel["id"],
            display_name=channel["title"],
            icon=channel["images"]["square"],
        )
        for channel in channels_raw
    ]

    channels_metadata = ChannelMetadata(channels=channels)

    return channels_metadata


def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    date_today = date.today() - timedelta(days=1)

    programmes = []

    for i in range(days):
        date_input = date_today + timedelta(days=i)

        try:
            response = session.get(PROGRAMS_URL, params={
                'channels': channel_id,
                'date': date_input,
                'duration': '24',
                'hour': '16',
                'segments': 'all'
            })
        except Exception as e:
            raise e

        [output] = (response.json())
        schedules = output['schedules']

        for schedule in schedules:

            start_program = datetime.strptime(
                schedule["startDate"], DATETIME_FORMAT)
            end_program = datetime.strptime(
                schedule["endDate"], DATETIME_FORMAT)

            prog_obj = Programme(
                start=start_program,
                stop=end_program,
                channel=channel_name,
                title=schedule['item']['title'],
                desc=schedule['item']['description']
            )

            programmes.append(prog_obj)

    return programmes
