import importlib
import os
import re
import sys
import requests
import logging
# Environment variables
from config.env import config_name, config_url, develop, epg_days, tests, tmp_epg_file
from source import xmlutils
from source.utils import get_channel_by_name
from config.constants import CONFIG_REGEX, DEVELOP_FILE, TESTS_FILE, TITLE, EMPTY_CONFIG_ERROR_MESSAGE
from source.xmlutils import program_to_xml, channel_to_xml, xml_header


sys.tracebacklimit = 0
log = logging.getLogger(TITLE)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=os.environ.get("LOGLEVEL", "INFO"),
    datefmt='%Y-%m-%d %H:%M:%S')


def load_config():
    """This is where the config file is read and parsed as a list.

    The config file should be in raw text with the following content:
    site_name;channel_name

    Returns:
        list[config_items]
    """

    if tests():
        with open(TESTS_FILE, "r") as r:
            text_buffer = r.read()
    elif develop():
        with open(DEVELOP_FILE, "r") as r:
            text_buffer = r.read()
    else:
        try:
            r = requests.get(config_url)
            r.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise Exception(e)
        except requests.exceptions.RequestException as e:
            raise Exception(e)
        except Exception as e:
            raise Exception(e)
        text_buffer = r.text

    config_items = [config for config in text_buffer.splitlines()
                    if config
                    if re.match(CONFIG_REGEX, config)
                    if not config.startswith("#")]

    if not config_items:
        raise Exception(
            EMPTY_CONFIG_ERROR_MESSAGE.format(
                config_url=config_url))

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
    except Exception as e:
        log.error("Site unsupported! {}: {}".format(type(e).__name__, e))
        raise e

    log.info("[%s] Start scrape_by_site from %s", channel_name, site_name)

    try:
        programs_by_channel = site.get_programs_by_channel(
            channel_name, int(epg_days))
    except Exception as e:
        log.error("{}: {}".format(type(e).__name__, e))
        raise e

    try:
        channel = get_channel_by_name(channel_name, site_name)
    except Exception as e:
        log.error("{}: {}".format(type(e).__name__, e))
        raise e

    log.info(
        "[%s] Total programs = %d",
        channel_name,
        len(programs_by_channel))
    log.info("[%s] Scraping completed.", channel_name)

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

        log.info("[%s] Channel found. Scraping programs...", channel_name)

        try:
            programs_by_channel, channel_inner = scrape_by_site(
                site_name, channel_name)
        except Exception:
            continue

        channels.append(channel_inner)
        programs.extend(programs_by_channel)

    """
    Writing XMLTV format to a temporary file
    """
    with open(tmp_epg_file, "w+") as file:
        file.write(xml_header(TITLE))

        for channel in channels:
            file.write(channel_to_xml(channel))

        for program in programs:
            file.write(program_to_xml(program))

        file.write(xmlutils.xml_close())

    return True


if __name__ == "__main__":
    import time
    start_time = time.time()
    log.info("START: Starting scraping for config %s ...", config_name)

    if scrape():
        log.info("FINISH: Finished scraping.")
        print("--- %s seconds ---" % (time.time() - start_time))
        exit()
