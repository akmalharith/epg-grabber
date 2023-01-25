from epg_grabber.models import Programme, ChannelMetadata, Channel
from datetime import datetime, time, timedelta
from typing import List
import requests

EPG_API_URL = "https://headend-api.tonton.com.my/v100/api/epg.class.api.php/getChannelListings/378"
ALL_CHANNELS_API_URL = 'https://headend-api.tonton.com.my/v100/api/categoryTree.class.api.php/GOgetLiveChannels/378'
FILTER_FIELDS = "Duration,EventTitle,EpisodeTitle,ParentalRating,ShortSynopsis,ParentalAdvice,Genre,MainGenre,SubGenre,StartTimeUTC,ProgramID,EndTimeUTC,RawStartTimeUTC,RawEndTimeUTC,YearOfProduction,Keywords,ReportingGenre,ReportingSubGenre,ClosedCaption,HighDefinition,SeriesNumber,EpisodeNumber"
APP_ID = "TONTON"
IMAGE_PREFIX_URL = "https://headend-api.tonton.com.my/v100/imageHelper.php?id="
IMAGE_SUFFIX_URL = ".:378:CHANNEL:IMAGE:png"

DEFAULT_HEADERS = {
    "authority": "headend-api.tonton.com.my",
    "origin": "https://watch.tonton.com.my",
    "referer": "https://watch.tonton.com.my",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}

session = requests.Session()


def generate() -> ChannelMetadata:
    try:
        response = session.get(ALL_CHANNELS_API_URL, params={
            'format': 'json',
            'appID': 'TONTON',
            'plt': 'web',

        })
    except Exception as e:
        raise e

    raw_channels = response.json()['liveChannel']
    
    # https://headend-api.tonton.com.my/v100/imageHelper.php?id=6420323:378:CHANNEL:IMAGE:png 
    channels = []
    for ch in raw_channels:
        ch_image_id = f"{ch['image'].split('_')[-1]}{IMAGE_SUFFIX_URL}"

        ch_obj = Channel(
            id=ch['channelCode'],
            display_name=ch['title'],
            icon=f"{IMAGE_PREFIX_URL}{ch_image_id}"
        )
        channels.append(ch_obj)

    return ChannelMetadata(channels=channels)


def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    date_today: datetime = datetime.combine(datetime.today(), time.min)

    for i in range(days):

        begin_datetime = date_today + timedelta(days=i)
        end_datetime = begin_datetime + timedelta(days=1)

        begin_datetime = int(begin_datetime.timestamp())
        end_datetime = int(end_datetime.timestamp())

        try:
            response = session.get(
                EPG_API_URL,
                params={
                    "filter_starttime": begin_datetime,
                    "filter_endtime": end_datetime,
                    "filter_channels": channel_id,
                    "filter_fields": FILTER_FIELDS,
                    "format": "json",
                    "appID": APP_ID,
                    "serviceId": "default",
                },
                headers=DEFAULT_HEADERS,
            )
        except Exception as e:
            raise e

        [raw_programs] = response.json()
        raw_programs = raw_programs["ChannelSchedule"]["EventList"]

        output_programs = [
            Programme(
                start=datetime.utcfromtimestamp(int(prog["StartTimeUTC"])),
                stop=datetime.utcfromtimestamp(int(prog["EndTimeUTC"])),
                channel=channel_name,
                title=prog["EventTitle"].title(),
                desc=prog["ShortSynopsis"],
            )
            for prog in raw_programs
        ]

        programmes.extend(output_programs)

    return programmes
