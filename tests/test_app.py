import os

from unittest import TestCase
from xmlunittest import XmlTestMixin

from epg_grabber.app import scrape_by_site
from epg_grabber.sites import (astro)
from epg_grabber.source.classes import EpgWriter
from epg_grabber.source.utils import load_channels_metadata
from epg_grabber.generate import get_sites

class ChannelMetadata:
    @staticmethod
    def load(site):
        """Load first channel
        """
        os.path.abspath(os.curdir)
        project_root = os.path.abspath(os.curdir)
        metadata_path = os.path.join(project_root, "epg_grabber/sites/channels_metadata/"+site+".json")

        data = load_channels_metadata(metadata_path)
        return data[0]

    @staticmethod
    def load_all_sites():
        return get_sites()

class TestVisionPlus(TestCase, XmlTestMixin):
    def test_vision(self):

        channel = ChannelMetadata.load("visionplus")
        programs, channel = scrape_by_site("visionplus", channel["tvg_id"])

        xml_data = EpgWriter.generate(channels=[channel], programs=programs)

        self.assertXmlDocument(xml_data)