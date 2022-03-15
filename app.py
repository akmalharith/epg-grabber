import importlib
import os
import re
import requests
import logging
from config.env import config_name, config_url, epg_days, tmp_epg_file # Environment variables
from source import xmlutils
from source.utils import get_channel_by_name
from config.constants import TITLE, EMPTY_CONFIG_ERROR_MESSAGE

config_regex = r"^[-\w\s]+(?:;[-.&\w\s]*)$"

log = logging.getLogger("epg_grabber")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def load_config():
    """This is where the config file is read and parsed as a list.

    The config file should be in raw text with the following content:
    site_name;channel_name

    Returns:
        list[config_items]
    """

    try:
        r = requests.get(config_url)
        r.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise Exception(e)
    except requests.exceptions.RequestException as e:
        raise Exception(e)
    except Exception as e:
        raise Exception(e)
    

    config_items = [config for config in r.text.splitlines() 
                    if config
                    if re.match(config_regex, config)
                    if not config.startswith("#")]

    if not config_items:
        raise Exception(EMPTY_CONFIG_ERROR_MESSAGE.format(config_url=config_url))

    return config_items


def scrape_by_site(site_name, channel_name):
    """Scrape the program and channel information for the given site

    Args:
        site_name (string): Site module
        channel_name (string): Channel from the site moudle

    Returns:
        tuple (list, Channel): Tuple of programs list and channel object
    """
    try:
        site = importlib.import_module("sites." + site_name)
    except ModuleNotFoundError as error:
        log.error("Site unsupported! {}".format(error))
        return

    log.info("Start scrape_by_site for " + channel_name)

    try:
        programs_by_channel = site.get_programs_by_channel(
            channel_name, int(epg_days))
    except BaseException as error:
        log.error(
            "An exception occurred on " +
            channel_name +
            ": {}".format(error))
        return

    try:
        channel = get_channel_by_name(channel_name, site_name)
    except BaseException as error:
        log.error(
            "An exception occurred on " +
            channel_name +
            ": {}".format(error))
        return

    # channel.name = site_name + ";" + channel.name.replace(" ", "")

    log.info("Total programs for " + channel_name +
          " = " + str(len(programs_by_channel)))
    log.info("Completed for " + channel_name)

    return programs_by_channel, channel


def scrape():
    """
    Main scraping method for the configurations loaded
    """
    channels = []
    programs = []

    config_items = load_config()

    for config_item in config_items:
        site_name = config_item.split(";")[0]
        channel_name = config_item.split(";")[1].strip()

        log.info("Channel found: " + channel_name + ". Scraping programs...")
        try:
            programs_by_channel, channel_info = scrape_by_site(
                site_name, channel_name)
        except TypeError:
            continue

        programs.extend(programs_by_channel)
        channels.append(channel_info)

    """
    Writing XMLTV format to a temporary file
    """
    with open(tmp_epg_file, "w+") as f:
        f.write(xmlutils.xml_header(TITLE))
        for channel in channels:
            f.write(xmlutils.channel_to_xml(channel))

        for p in programs:

            f.write(xmlutils.program_to_xml(p))

        f.write(xmlutils.xml_close())

    return True


if __name__ == "__main__":
    log.info("START: Starting scraping for config " + config_name + "...")

    if scrape():
        log.info("FINISH: Finished scraping.")
        exit()
