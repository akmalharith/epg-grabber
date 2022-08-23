from config.constants import TITLE
from models.tvg import Channel, Program
from helper.xmlutils import channel_to_xml, program_to_xml, xml_header, xml_close
from typing import List


class EpgWriter:
    @staticmethod
    def generate(channels=None, programs=None) -> bytes:
        """Generate an XML data from channels and programs."""

        channel_xml = [channel_to_xml(channel) for channel in channels][0]
        programs_xml = [program_to_xml(program) for program in programs][0]

        xmlstring = xml_header(TITLE) + channel_xml + programs_xml + xml_close()
        xmlbytes = bytes(xmlstring, "utf-8")

        return xmlbytes

    @staticmethod
    def save(file="", channels=List[Channel], programs=List[Program]):

        with open(file, "w+") as file:
            file.write(xml_header(TITLE))

            for channel in channels:
                file.write(channel_to_xml(channel))

            for program in programs:
                file.write(program_to_xml(program))

            file.write(xml_close())
