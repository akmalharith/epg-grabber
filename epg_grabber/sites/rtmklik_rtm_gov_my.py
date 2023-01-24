from epg_grabber.models import Programme, ChannelMetadata, Channel
from datetime import datetime, timedelta
from string import Template
from typing import List
import requests

ALL_CHANNELS_URL = 'https://rtm.glueapi.io/v3/epg?limit=100'
CHANNEL_ICON_PREFIX_URL = 'https://rtm-images.glueapi.io/320x0'
API_URL = Template("https://rtm.glueapi.io/v3/epg/$channel_id/ChannelSchedule")
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
HOURS_OFFSET = 8

session = requests.Session()


def generate() -> ChannelMetadata:
    try:
        response = session.get('https://rtm.glueapi.io/v3/epg?limit=100')
    except Exception as e:
        raise e

    raw_channels = response.json()['data']

    channels = [Channel(
        id=str(ch['id']),
        display_name=ch['channel'],
        icon=f"{CHANNEL_ICON_PREFIX_URL}/{ch['image']}"
    ) for ch in raw_channels]

    channel_metadata = ChannelMetadata(channels=channels)

    return channel_metadata


def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    date_today = datetime.today()

    date_start = date_today.date()
    date_end = (date_today + timedelta(days=days - 1)).date()

    api_url = API_URL.substitute({"channel_id": channel_id})

    try:
        response = session.get(
            api_url,
            params={
                "dateStart": date_start,
                "dateEnd": date_end,
                "timezone": "+08:00",
                "embed": "author,program",
            },
        )
    except Exception as e:
        raise e

    raw_programs = response.json()["schedule"]

    programmes = []

    for prog in raw_programs:
        # Programme() expects UTC
        start_time = datetime.strptime(
            prog["dateTimeStart"], DATETIME_FORMAT) - timedelta(hours=HOURS_OFFSET)
        stop_time = datetime.strptime(
            prog["dateTimeEnd"], DATETIME_FORMAT) - timedelta(hours=HOURS_OFFSET)

        prog_obj = Programme(
            start=start_time,
            stop=stop_time,
            channel=channel_name,
            title=prog["scheduleProgramTitle"],
            desc=prog["scheduleProgramDescription"],
        )
        programmes.append(prog_obj)

    return programmes
