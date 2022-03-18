import requests
import json
import os
from datetime import date, timedelta, datetime
from pytz import timezone
from source.classes import Program, Channel

temp_file = "starhubtvplus_all_programs_temp.json"
api_url = "https://api.starhubtvplus.com/"

app_session = "01FYFAFG9ERQJNDKQJGRMKNP54101F7A4435"
app_key = "5ee2ef931de1c4001b2e7fa3_5ee2ec25a0e845001c1783dc" 

def get_all_channels():
    programs = _get_programs()
    # Unfortunately it's not possible to get the channel names
    # We have a web page in https://www.starhub.com/personal/tvplus/passes/channel-listing.html
    # It's not worth it that we need to scrape a whole page for this
    channels = [ Channel(
        program["id"],
        program["channelId"]+ ".Sg", 
        program["channelId"],
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
        "x-application-session": app_session,
        "x-application-key": app_key
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
        "x-application-session": app_session,
        "x-application-key": app_key
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

    programs_channel = [program["programs"] for program in programs
                        if program["channelId"] == int(channel_name)][0]

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
            start=get_epg_time(start_program),
            stop=get_epg_time(end_program),
            category=category,
            rating=rating
        )

        programs.append(program_object)

    return programs