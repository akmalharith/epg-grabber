from pytz import timezone
from epg_grabber.models import Programme, Channel, ChannelMetadata
from datetime import date, datetime, timedelta
from typing import List 
from uuid import uuid4
from tzlocal import get_localzone_name
import requests

IMAGE_PREFIX_URL = "https://d229kpbsb5jevy.cloudfront.net/mytv/content"

def get_session() -> dict:
    box_id = str(uuid4())

    try:
        response = requests.get('https://mytv-api.revlet.net/service/api/v1/get/token', params={
            'tenant_code': 'mytv',
            'box_id': box_id,
            'product': 'mytv',
            'device_id': 61,
            'display_lang_code': 'ENG',
            'device_sub_type': 'Chrome,115.0.0.0,MacOS',
            'timezone': 'Asia/Kuala_Lumpur'
        })
    except Exception as e:
        raise(e)

    output = response.json()

    if not output['status']:
        raise Exception('Unable to get session.')

    session_id = output['response']['sessionId']

    return {
        'authority': 'mytv-api.revlet.net',
        'box-id': box_id,
        'session-id': session_id,
        'tenant-code': 'mytv',
        'origin': 'https://mana2.my',
        'referer': 'https://mana2.my/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

session_headers = get_session()

def generate() -> ChannelMetadata:
    try:
        response = requests.get('https://mytv-api.revlet.net/service/api/v1/page/content',
            params={
                'path': 'section/live-on-tv'
            },
            headers=session_headers
        )
    except Exception as e:
        raise e
    
    output = response.json()
    datas = output['response']['data'][0]['section']['sectionData']['data']

    channels = []

    for data in datas:
        channel_id = data['metadata']['channelId']['value']
        display_name = data['display']['parentName']
        image_url = data['display']['imageUrl']

        image_url = image_url.replace(",","/")
        image_url = f"{IMAGE_PREFIX_URL}/{image_url}"

        channel_obj = Channel(
            id=channel_id,
            display_name=display_name,
            icon=image_url,
        )

        channels.append(channel_obj)

    channel_metadata = ChannelMetadata(channels=channels)

    return channel_metadata

def get_programs(
    channel_id: str = 1, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:
    
    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    # for day in range(days):
    start_dt = date.today()   
    start_date = datetime.combine(start_dt, datetime.min.time())
    start_timestamp_in_miliseconds = int(start_date.timestamp() * 1000)

    end_dt = start_dt + timedelta(days=days)
    end_date = datetime.combine(end_dt, datetime.max.time())
    end_timestamp_in_miliseconds = int(end_date.timestamp() * 1000)


    try:
        response = requests.get('https://mytv-api.revlet.net/service/api/v1/static/tvguide',
            params={
                'channel_ids': channel_id,
                'start_time': start_timestamp_in_miliseconds,
                'end_time': end_timestamp_in_miliseconds,
                'page': 0,
            },
            headers=session_headers
        )
    except Exception as e:
        raise e
    
    output = response.json()
    [data] = (output['response']['data'])
    programs = data['programs']

    # Get caller TzInfo
    tz = timezone(get_localzone_name())

    for program in programs:
        title = (program['display']['title'])
        description = (program['display']['subtitle2'])
        start_time_mili = int(program['display']['markers']['startTime']['value']) / 1000
        end_time_mili = int(program['display']['markers']['endTime']['value']) / 1000

        start_time = tz.localize(datetime.fromtimestamp(start_time_mili))
        end_time = tz.localize(datetime.fromtimestamp(end_time_mili))

        programme_obj = Programme(
            start=start_time,
            stop=end_time,
            channel=channel_name,
            title=title,
            desc=description,
        )

        programmes.append(programme_obj)

    return programmes
