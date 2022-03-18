import requests
import json
import os
from pathlib import Path
from datetime import date, timedelta, datetime
from pytz import timezone
from source.classes import Program, Channel
from source.utils import get_channel_by_name, get_epg_datetime
from config.env import starhubtvplus_app_session, starhubtvplus_app_key

temp_file = "starhubtvplus_all_programs_temp.json"
api_url = "https://api.starhubtvplus.com/"

def get_all_channels():
    date_from = date.today()
    date_to = date_from + timedelta(days = 1)
    programs = _get_programs(str(date_from), str(date_to))
    # Unfortunately it's not possible to get the channel names
    # We have a web page in https://www.starhub.com/personal/tvplus/passes/channel-listing.html
    # It's not worth it that we need to scrape a whole page for this
    channels = [ Channel(
        str(program["id"]),
        str(program["channelId"])+ ".Sg", 
        str(program["channelId"]),
        program["image"]
    ) for program in programs]

    return  channels

def _get_programs(date_from, date_to):
    if os.path.isfile(temp_file):
        file_data = open(temp_file, "r")
        temp_data = json.load(file_data)
        return temp_data
    
    get_programs_query = """query webFilteredEpg($category: String, $dateFrom: DateWithoutTime, $dateTo: DateWithoutTime!) {
nagraEpg(category: $category) {
    items {
    channelId: tvChannel
    id
    image
    isIptvMulticast
    isOttUnicast
    title: description
    programs: programsByDate(dateFrom: $dateFrom, dateTo: $dateTo) {
        channel {
        isIptvMulticast
        isOttUnicast
        __typename
        }
        endTime
        id
        startOverSupport
        startTime
        title
        __typename
    }
    __typename
    }
    __typename
}
}
"""
    headers = {
        "x-application-session": starhubtvplus_app_session,
        "x-application-key": starhubtvplus_app_key
    }

    programs_payload = {
        "operationName": "webFilteredEpg",
        "variables": {
            "id": "GLOBAL_58",
            "category": "",
            "dateFrom": date_from, 
            "dateTo": date_to
        },
        "query": get_programs_query
    }

    try:
        response = requests.post(api_url, headers=headers, json=programs_payload)
    except Exception as e:
        raise (e)

    output = response.json()

    all_channels_program = output["data"]["nagraEpg"]["items"]
    
    with open(temp_file, "w") as infile:
        json.dump(all_channels_program, infile)
        infile.close()
    
    return all_channels_program


def _get_program_details(program_id):
    get_programs_details_query = """query webEpgDetails($id: String!) {
  details(id: $id) {
    description
    duration
    genres
    id
    image
    productRefs
    rating
    title
    products {
      pack {
        id
        productId
        purchasableUfinityProduct {
          productId
          __typename
        }
        __typename
      }
      __typename
    }
    ... on LinearInterface {
      endTime
      isCatchUpSupported
      startOverSupport
      startTime
      __typename
    }
    ... on NagraProgram {
      channel {
        image
        __typename
      }
      next {
        duration
        id
        rating
        title
        __typename
      }
      channel {
        id
        tvChannel
        catchUpSupport
        __typename
      }
      __typename
    }
    ... on NagraChannel {
      tvChannel
      nowPlaying {
        id
        next {
          duration
          id
          rating
          title
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

    program_details_payload = {
        "operationName": "webEpgDetails",
        "variables": {
            "id": program_id
        },
        "query": get_programs_details_query
    }

    headers = {
        "x-application-session": starhubtvplus_app_session,
        "x-application-key": starhubtvplus_app_key
    }
    try:
        response = requests.post(api_url, headers=headers, json=program_details_payload)
    except Exception as e:
        raise (e)

    output = response.json()

    details = output["data"]["details"]

    if "description" in details:
        description = details["description"]
    
    if "genres" in details and len(details["genres"]) != 0:
        category = details["genres"][0] # Only get one genre for now

    if "rating" in details:
        rating = details["rating"] # <rating system="USA Parental Rating">

    return description, category, rating
        
def get_programs_by_channel(channel_name, *args):
    """_summary_

    Args:
        channel_name (_type_): _description_
    """
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_from = date.today()
    date_to = date_from + timedelta(days = days)

    programs = _get_programs(str(date_from), str(date_to))

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    programs_channel = [program["programs"] for program in programs
                        if program["id"] == channel.id][0]

    programs = []

    for programs_inner in programs_channel:
        description, category, rating = _get_program_details(programs_inner["id"])

        start_timestamp = programs_inner["startTime"] / 1000
        start_program = datetime.fromtimestamp(start_timestamp, timezone("UTC"))

        end_timestamp = programs_inner["startTime"] / 1000
        end_program = datetime.fromtimestamp(end_timestamp, timezone("UTC"))

        program_object = Program(
            channel_name=channel_name,
            title=programs_inner["title"],
            description=description,
            start=get_epg_datetime(start_program),
            stop=get_epg_datetime(end_program),
            category=category,
            rating=rating
        )

        programs.append(program_object)

    return programs