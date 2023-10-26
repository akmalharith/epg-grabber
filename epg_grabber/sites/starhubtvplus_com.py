import requests
from uuid import uuid4
from datetime import date, timedelta, datetime
from epg_grabber.models import Channel, ChannelMetadata, Programme

from typing import List

API_URL = "https://api.starhubtvplus.com"
APP_KEY = "5ee2ef931de1c4001b2e7fa3"
IDENTIFIER = "5ee2ec25a0e845001c1783dc"

# Authenticate
response = requests.get(
    "https://api.one.accedo.tv/session",
    params={"appKey": "5ee2ef931de1c4001b2e7fa3", "uuid": str(uuid4())},
)
auth_output = response.json()

headers = {
    "x-application-key": f"{APP_KEY}_{IDENTIFIER}",
    "x-application-session": auth_output["sessionKey"],
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}

def generate() -> ChannelMetadata:
    query_body = """
    query webFilteredEpg($category: String) {
        nagraEpg(category: $category) {
            items {
                channelId: tvChannel
                image
                name: longName
            }
        }
    } 
    """
    try:
        epg_response = requests.post(
            API_URL,
            headers=headers,
            json={
                "operationName": "webFilteredEpg",
                "query": query_body,
            },
        )
    except Exception as e:
        raise e

    epg_output = epg_response.json()
    items = epg_output["data"]["nagraEpg"]["items"]

    channels = [
        Channel(id=str(item["channelId"]), display_name=item['name'].replace("_DASH",""), icon=item["image"]) 
        for item in items
    ]

    return ChannelMetadata(channels=channels)

def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:
    query_body = """
    query webFilteredEpg($category: String, $dateFrom: DateWithoutTime, $dateTo: DateWithoutTime!) {
        nagraEpg(category: $category) {
            items {
                channelId: tvChannel
                id
                name: longName
                programs: programsByDate(dateFrom: $dateFrom, dateTo: $dateTo) {
                    id
                    title
                    startTime
                    endTime
                    rating
                    description
                    Categories
                }
            }
        }
    } 
    """

    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id

    date_from = date.today()
    date_to = date_from + timedelta(days=days)

    try:
        epg_response = requests.post(
            API_URL,
            headers=headers,
            json={
                "operationName": "webFilteredEpg",
                "variables": {
                    "dateFrom": str(date_from),
                    "dateTo": str(date_to),
                },
                "query": query_body,
            },
        )
    except Exception as e:
        raise e

    epg_output = epg_response.json()
    items = epg_output["data"]["nagraEpg"]["items"]

    try:
        items = [i for i in items if i["channelId"] == int(channel_id)][0]
    except IndexError:
        raise Exception("Channel doesn't exists")

    for program in items["programs"]:
        start_time = datetime.utcfromtimestamp(int(program["startTime"]) / 1000)
        end_time = datetime.utcfromtimestamp(int(program["startTime"]) / 1000)

        programmes.append(
            Programme(
                start=start_time,
                stop=end_time,
                title=program["title"],
                desc=program["description"],
                category=program["Categories"][0],
                channel=channel_name,
                rating=program["rating"][0],
            )
        )

    return programmes
