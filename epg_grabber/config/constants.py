import os

TITLE = "epg-grabber"
EPG_XMLTV_TIMEFORMAT = "%Y%m%d%H%M%S"
CONFIG_REGEX = r"^[-\w\s]+(?:;[-.&\w\s]*)$"
PERIOD = "."
SITES_DIR = "sites"
METADATA_DIR = os.path.join(SITES_DIR, "channels_metadata")
CONFIG_DIR = os.path.join(SITES_DIR, "channels_config")

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36"

EMPTY_CONFIG_ERROR_MESSAGE = """
The URL {config_url} does not contain any valid configurations.
The file should contain a list of site configuration as below:

mewatch;Channel5.Sg
mewatch;Channel8.Sg
mewatch;ChannelU.Sg"""

TESTS_FILE = "tests.txt"
DEVELOP_FILE = "local.txt"
