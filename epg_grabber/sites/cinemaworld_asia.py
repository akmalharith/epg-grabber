from epg_grabber.models import Programme, ChannelMetadata, Channel
from datetime import datetime, timedelta, date
from typing import List
import requests

EPG_URL = 'https://nova.cinemaworld.asia/api/schedules'
HRS_OFFSET = -8
DATETIME_FORMAT = '%Y-%m-%d %I:%M %p'


def generate() -> ChannelMetadata:
    return ChannelMetadata(channels=[
        Channel(
            id='cinemaworld',
            display_name='CinemaWorld',
            icon='https://www.voilah.sg/wp-content/uploads/2020/04/cinema-world-2.png'
        )
    ])


def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    date_today = date.today()

    limit_days = 6 if days > 6 else days

    schedules = []

    for i in range(limit_days):
        date_input = date_today + timedelta(days=i)

        try:
            response = requests.get(EPG_URL, params={
                'startDate': date_input
            })
        except Exception as e:
            raise e

        schedules.extend(response.json()['shows'])

    for i in range(len(schedules)):

        str_date = schedules[i]['schedule_start_date']
        str_time = schedules[i]['schedule_start_time']

        try:
            next_str_date = schedules[i+1]['schedule_start_date']
            next_str_time = schedules[i+1]['schedule_start_time']
        except IndexError:
            # Unfortunately due to this limitation the last program for this channel will have to
            # be omitted
            pass

        start_datetime = datetime.strptime(
            f"{str_date} {str_time}", DATETIME_FORMAT) + timedelta(hours=HRS_OFFSET)
        end_datetime = datetime.strptime(
            f"{next_str_date} {next_str_time}", DATETIME_FORMAT) + timedelta(hours=HRS_OFFSET)

        prog_obj = Programme(
            start=start_datetime,
            stop=end_datetime,
            channel=channel_name,
            title=schedules[i]['title'],
            desc=schedules[i]['short_desc']
        )
        programmes.append(prog_obj)

    return programmes
