from epg_grabber.models import Programme, Channel, ChannelMetadata
from typing import List
from string import Template
from itertools import islice
from datetime import datetime, timedelta
import requests

ALL_CHANNELS_URL = "https://contenthub-api.eco.astro.com.my/channel/all.json"
PROGRAM_URL = Template(
    "https://contenthub-api.eco.astro.com.my/channel/$channel_id.json"
)
PROGRAM_DETAIL_URL = "https://contenthub-api.eco.astro.com.my/api/v1/linear-detail"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

DEFAULT_HEADERS = {
    "authority": "contenthub-api.eco.astro.com.my",
    "origin": "https://content.astro.com.my",
    "referer": "https://content.astro.com.my",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}

session = requests.Session()


def generate() -> ChannelMetadata:
    try:
        response = session.get(ALL_CHANNELS_URL)
    except Exception as e:
        raise e

    raw_channels = response.json()["response"]

    channels = [
        Channel(
            id=str(channel["id"]),
            display_name=channel["title"],
            icon=channel["imageUrl"],
        )
        for channel in raw_channels
    ]

    channel_metadata = ChannelMetadata(channels=channels)

    return channel_metadata


def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:
    def get_program_details(traffic_key: str) -> str:

        try:
            response = session.get(
                PROGRAM_DETAIL_URL,
                headers=DEFAULT_HEADERS,
                params={"siTrafficKey": traffic_key},
            )
        except Exception as e:
            raise e

        output = response.json()["response"]

        if 'shortSynopsis' in output:
            return output["shortSynopsis"]
        else:
            return ''

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    program_url = PROGRAM_URL.substitute({"channel_id": channel_id})

    try:
        response = session.get(program_url, headers=DEFAULT_HEADERS)
    except Exception as e:
        raise e

    output = response.json()

    schedules_filtered = dict(
        islice(output["response"]["schedule"].items(), days))

    schedules = []
    filtered_values = schedules_filtered.values()
    for filtered in filtered_values:
        schedules.extend(filtered)

    for schedule in schedules:

        start_time = datetime.strptime(
            schedule["datetimeInUtc"], DATETIME_FORMAT)
        hour, min, sec = schedule["duration"].split(":")
        end_time = start_time + timedelta(
            hours=int(hour), minutes=int(min), seconds=int(sec)
        )

        programme_obj = Programme(
            start=start_time,
            stop=end_time,
            channel=channel_name,
            title=schedule["title"],
            desc=get_program_details(schedule["siTrafficKey"]),
        )

        programmes.append(programme_obj)

    return programmes
