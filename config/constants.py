TITLE = "epg-grabber"
EPG_XMLTV_TIMEFORMAT = "%Y%m%d%H%M%S"
CONFIG_REGEX = r"^[-\w\s]+(?:;[-.&\w\s]*)$"
PERIOD = "."








EMPTY_CONFIG_ERROR_MESSAGE = """
The URL {config_url} does not contain any valid configurations.
The file should contain a list of site configuration as below:

mewatch;Channel5.Sg
mewatch;Channel8.Sg
mewatch;ChannelU.Sg"""