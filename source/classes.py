import string
from config.constants import PERIOD


class Program:
    __slots__ = ['channel_name', 'title',
                 'description', 'start', 'stop', 'episode']

    def __init__(
            self,
            channel_name="",
            title="",
            description="",
            start="",
            stop="",
            episode="") -> None:
        """
        Details of a single programme transmission. If no attributes are set we are returning empty program, useful if API calls are not returning success, because we do not want to break the scraping job.

        Eg:
            if req.status_code != 200:
                return [Program()]

        Args:
            channel_name (string): A user-friendly name for the channel - maybe even a channel number.  List the most canonical / common ones first and the most obscure names last.  The lang attribute follows RFC 1766.
            title (string): Programme title.
            description (string): Description of the programme or episode.
            start (string): Programme start time. Use get_epg_time() which will parse it for you from a datetime input.
            stop (string): Programme start time. Use get_epg_time() which will parse it for you from a datetime input.
            episode (string): Not the title of the episode, its number or ID.  There are several ways of numbering episodes, so the 'system' attribute lets you specify which you mean. There are two predefined numbering systems, 'xmltv_ns' and 'onscreen'.

        """
        self.channel_name = channel_name
        self.title = title
        self.description = description
        self.start = start
        self.stop = stop
        self.episode = episode


class Channel:
    __slots__ = ["id", "tvg_id", "tvg_name", "tvg_logo"]

    def __init__(self, id, tvg_id, tvg_name, tvg_logo, sanitize=False) -> None:
        """Channel records, store information about channels.

        Args:
            id (string): Channel identifier that is unique to the source that we are scraping from.
            tvg_id (string): Channel ID in EPG XML file
            tvg_name (string): A user-friendly name for the channel - maybe even a channel number.
            tvg_logo (string): Channel logo.
        """
        self.id = id

        if sanitize:
            # Sanitize the characters in tvg_id, except a period
            tvg_id = [tvg_id.replace(char, "")
                    for char in string.punctuation
                    if char != PERIOD][0].replace(" ", "")
        self.tvg_id = tvg_id

        self.tvg_name = tvg_name
        self.tvg_logo = tvg_logo
