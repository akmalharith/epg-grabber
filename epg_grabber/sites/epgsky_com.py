from epg_grabber.models import Programme, ChannelMetadata, Channel
from datetime import datetime, date, timedelta
from typing import List
import requests

EPG_SKY_URL = "https://awk.epgsky.com/hawk/linear/schedule"
ALL_CHANNELS_URL = "http://awk.epgsky.com/hawk/linear/services/4101/1"
DATETIME_FORMAT = "%Y%m%d"

session = requests.Session()


def generate() -> ChannelMetadata:
    try:
        response = session.get(ALL_CHANNELS_URL)
    except Exception as e:
        raise e

    raw_channels = response.json()["services"]

    channels = [
        Channel(id=ch["sid"], display_name=ch["t"], icon="http://")
        for ch in raw_channels
    ]

    channel_metadata = ChannelMetadata(channels=channels)

    return channel_metadata


def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    date_today = date.today()

    for i in range(days):
        date_input = date_today + timedelta(days=i)
        date_string = date_input.strftime(DATETIME_FORMAT)

        try:
            response = session.get(f"{EPG_SKY_URL}/{date_string}/{channel_id}")
        except Exception as e:
            raise e

        raw_programs = response.json()["schedule"][0]["events"]

        for prog in raw_programs:
            start_date_time = datetime.utcfromtimestamp(int(prog["st"]))

            if 'sy' in prog:
                desc = prog['sy']
            else:
                desc = ''

            programmes.append(
                Programme(
                    start=start_date_time,
                    stop=start_date_time + timedelta(seconds=int(prog["d"])),
                    channel=channel_name,
                    title=prog["t"],
                    desc=desc,
                    episode=prog["eid"],
                )
            )

    return programmes
