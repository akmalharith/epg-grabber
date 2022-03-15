import json
from multiprocessing.sharedctypes import Value
import os
from source.classes import Channel
from config.constants import EPG_XMLTV_TIMEFORMAT


def get_epg_time(datetime, offset="+0000"):
    return datetime.strftime(EPG_XMLTV_TIMEFORMAT)+" "+offset


def load_channels_metadata(site_name):
    working_dir = os.getcwd()
    target_dir = os.path.join(working_dir, "sites/channels_metadata")

    f = open(os.path.join(target_dir, site_name + ".json"), "r")

    data = json.load(f)

    return data


def get_channel_by_name(tvg_id, site_name):
    """Retrieve the whole Channel object given its name and its site. 
    
    If you don't want to hardcode the site_name parameter, use __file__
    as the site_name input.
    
    Eg:
        get_channel_by_name(channel_name, Path(__file__).stem)

    TODO: We could retrieve the caller filename and override the call in here.

    Args:
        channel_name (string): Channel name
        site_name (string): Website/module name

    Returns:
        Channel: Channel object
    """
    all_channels = load_channels_metadata(site_name)

    try:
        chan = next(
            channel for channel in all_channels if channel["tvg_id"].lower() == tvg_id.lower())
    except Exception as e:
        raise ValueError("Channel metadata %s not found.",tvg_id)
    return Channel(chan["id"], chan["tvg_id"], chan["tvg_name"], chan["tvg_logo"])


def get_channelid_by_name(tvg_id, site_name):
    return get_channel_by_name(tvg_id, site_name).id