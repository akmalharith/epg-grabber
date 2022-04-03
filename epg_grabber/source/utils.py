import os
import json

from config.constants import EPG_XMLTV_TIMEFORMAT
from source.classes import Channel


def get_epg_datetime(datetime, offset="+0000"):
    """Method that returns the XMLTV date time string

    Args:
        datetime (datetime): Date Time object for a given program
        offset (str, optional): By default offset is UTC,
                                useful if time scraped is in Epoch timestamp.
                                Defaults to "+0000".

    Returns:
        epg_datetime (string): Date Time formatted in XMLTV format
    """
    return datetime.strftime(EPG_XMLTV_TIMEFORMAT) + " " + offset


def load_channels_metadata(metadata_path):
    f = open(metadata_path, "r")

    data = json.load(f)

    f.close()

    return data


def get_channel_by_name(tvg_id, site_name):
    """Retrieve the whole Channel object given its name and its site.

    If you don't want to hardcode the site_name parameter, use __file__
    as the site_name input.

    Eg:
        get_channel_by_name(channel_name, Path(__file__).stem)

    TODO: We could retrieve the caller filename and override the call in here.
        I never got it to work.

    Args:
        channel_name (string): Channel name
        site_name (string): Website/module name

    Returns:
        Channel: Channel object
    """
    metadata_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'sites/channels_metadata'))
    metadata_path = metadata_dir + "/" + site_name + ".json"
    all_channels = load_channels_metadata(metadata_path)

    try:
        chan = next(
            channel for channel in all_channels if channel["tvg_id"].lower() == tvg_id.lower())
    except Exception:
        raise ValueError("Channel metadata %s not found.", tvg_id)
    return Channel(
        chan["id"],
        chan["tvg_id"],
        chan["tvg_name"],
        chan["tvg_logo"])


def get_channelid_by_name(tvg_id, site_name):
    return get_channel_by_name(tvg_id, site_name).id
