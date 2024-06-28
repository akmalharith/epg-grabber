from epg_grabber.models import Programme, ChannelMetadata, Channel

from datetime import date, datetime, timezone, timedelta
from typing import List
import requests 
import urllib.parse

CLIENT_ID = 'xe1dgrShwdR1DVOKGmsj8Ut4QLlGyOFI'

session = requests.Session()
session.headers.update(
    {
        'Accept': 'application/json',
        'Origin': 'https://nostv.pt',
        'Referer': 'https://nostv.pt/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'X-Apikey': CLIENT_ID,
        'X-Core-AppVersion': '2.17.0.1',
        'X-Core-ContentRatingLimit': '0',
        'X-Core-DeviceId': '',
        'X-Core-DeviceType': 'web',
    }
)

def generate() -> ChannelMetadata:
    response = session.get('https://tyr-prod.apigee.net/nostv/ott/channels/guest',params={
        'client_id': CLIENT_ID
    })

    response.raise_for_status()

    channels = response.json()

    channels_obj = []

    for channel in channels:
        internal_image_url = channel['Images'][0]['Url']
        internal_image_url = urllib.parse.quote_plus(internal_image_url)

        image_url = f"https://mage.stream.nos.pt/v1/nostv_mage/Images?sourceUri={internal_image_url}&client_id={CLIENT_ID}&format=image/png"

        obj = Channel(
            id=channel['ServiceId'],
            display_name=channel['Name'],
            icon=image_url
        )

        channels_obj.append(obj) 

    return ChannelMetadata(channels=channels_obj)

def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:
    
    start_dt = date.today()
    start_datetime = datetime.combine(start_dt, datetime.min.time(), tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')

    end_dt = start_dt + timedelta(days=days)
    end_datetime = datetime.combine(end_dt, datetime.min.time(), tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')

    PROGRAM_API_URL = 'https://tyr-prod.apigee.net/nostv/ott/schedule/range/contents/guest'

    response = session.get(
        url=PROGRAM_API_URL,
        params={
            'channels': channel_id,
            'minDate': start_datetime,
            'maxDate': end_datetime,
            'isDateInclusive': 'true',
            'client_id': CLIENT_ID
        }
    )

    response.raise_for_status()

    programs = response.json()
    
    all_programms = []

    for program in programs:

        prog_obj = Programme(
            title=program['Metadata']['Title'],
            desc=program['Metadata']['Description'],
            start=datetime.strptime(program['UtcDateTimeStart'], '%Y-%m-%dT%H:%M:%SZ'),
            stop=datetime.strptime(program['UtcDateTimeEnd'], '%Y-%m-%dT%H:%M:%SZ'),
            channel=f'{channel_id}.nostv_pt',
            rating=program['Metadata']['RatingDisplay'],
            category=program['Metadata']['GenreDisplay'].strip(),
        )

        all_programms.append(prog_obj)

    return all_programms