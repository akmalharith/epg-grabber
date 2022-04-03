import string

from config.constants import PERIOD, TITLE
from helper.xmlutils import channel_to_xml, program_to_xml, xml_header, xml_close


class Program:
    __slots__ = [
        'channel_name',
        'title',
        'description',
        'start',
        'stop',
        'episode',
        'category',
        'rating']

    def __init__(
            self,
            channel_name="",
            title="",
            description="",
            start="",
            stop="",
            episode="",
            category="",
            rating="") -> None:
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
        self.category = category
        self.rating = rating


class Channel:
    __slots__ = ["id", "tvg_id", "tvg_name", "tvg_logo"]

    def __init__(
            self,
            id="",
            tvg_id="",
            tvg_name="",
            tvg_logo="",
            sanitize=False) -> None:
        """
        _summary_

        Args:
            id (str, optional): _description_. Defaults to "".
            tvg_id (str, optional): _description_. Defaults to "".
            tvg_name (str, optional): _description_. Defaults to "".
            tvg_logo (str, optional): _description_. Defaults to "".
            sanitize (bool, optional): _description_. Defaults to False.
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


class EpgWriter:
    @staticmethod
    def generate(
            channels=None,
            programs=None) -> bytes:
        """Generate an XML data from channels and programs."""

        channel_xml = [channel_to_xml(channel) for channel in channels][0]
        programs_xml = [program_to_xml(program) for program in programs][0]

        xmlstring = xml_header(TITLE) + channel_xml + \
            programs_xml + xml_close()
        xmlbytes = bytes(xmlstring, "utf-8")

        return xmlbytes

    @staticmethod
    def save(
            file="",
            channels=None,
            programs=None):

        with open(file, "w+") as file:
            file.write(xml_header(TITLE))

            for channel in channels:
                file.write(channel_to_xml(channel))

            for program in programs:
                file.write(program_to_xml(program))

            file.write(xml_close())
