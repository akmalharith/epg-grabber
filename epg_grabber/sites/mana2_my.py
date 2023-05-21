from epg_grabber.models import Programme, Channel, ChannelMetadata
from datetime import date, datetime, timedelta
from typing import List 
import requests

CHANNELS_API = 'https://api.mana2.my/api/channels'
ORGANIZATION_ID = '196288014'
DEFAULT_HEADERS = {
    "Origin": "https://www.mana2.my",
    "Referer": "https://www.mana2.my",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

session = requests.Session()

def generate() -> ChannelMetadata:
    try:
        response = requests.get(
            url=CHANNELS_API,
            params={
                'action':'getChannels',
                'version':'04',
                'orderBy':'logicalChannelNumber',
                'organizationId': ORGANIZATION_ID
            },
            headers=DEFAULT_HEADERS
        )
    except Exception as e:
        raise e

    output = response.json()
    raw_channels = output['channels']

    channels = [
        Channel(
            id=str(channel["serviceId"]),
            display_name=channel["title"],
            icon=channel["imageSmall"],
        )
        for channel in raw_channels
    ]

    channel_metadata = ChannelMetadata(channels=channels)

    return channel_metadata

def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:
    
    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    start_dt = date.today()
    start_date = datetime.combine(start_dt, datetime.min.time())
    start_timestamp_in_miliseconds = int(start_date.timestamp() * 1000)

    end_dt = start_dt + timedelta(days=(days)-1)
    end_date = datetime.combine(end_dt, datetime.max.time())
    end_timestamp_in_miliseconds = int(end_date.timestamp() * 1000)

    try:
        response = requests.get(url=CHANNELS_API,params={
            'action':'getEvents',
            'version':'04',
            'organizationId': ORGANIZATION_ID,
            'lcId': channel_id, 
            'from':start_timestamp_in_miliseconds,
            'to':end_timestamp_in_miliseconds
        })
    except Exception as e:
        raise e
    
    output = response.json()
    events = output['events']
    for e in events:
        # Time in UTC
        start_time = datetime.strptime(e['info']['startTime'], DATETIME_FORMAT)
        duration_in_seconds = (e['info']['duration'])
        end_time = start_time + timedelta(seconds=int(duration_in_seconds))

        programme_obj = Programme(
            start=start_time,
            stop=end_time,
            channel=channel_name,
            title=e['description']['en_US']['name'],
            desc=e['description']['en_US']['shortDescription']
        )

        programmes.append(programme_obj)

    return programmes
