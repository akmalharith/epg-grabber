import os

TITLE = "epg-grabber"
EPG_XMLTV_TIMEFORMAT = "%Y%m%d%H%M%S"
CONFIG_REGEX = r"^[-\w\s]+(?:;[-.&\w\s]*)$"
PERIOD = "."
SITES_DIR = "sites"
METADATA_DIR = os.path.join(SITES_DIR, "channels_metadata")
CONFIG_DIR = os.path.join(SITES_DIR, "channels_config")

EMPTY_CONFIG_ERROR_MESSAGE = """
The URL {config_url} does not contain any valid configurations.
The file should contain a list of site configuration as below:

mewatch;Channel5.Sg
mewatch;Channel8.Sg
mewatch;ChannelU.Sg"""

TESTS_FILE = "tests.txt"
DEVELOP_FILE = "local.txt"
