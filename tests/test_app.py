import os

from unittest import TestCase
from xmlunittest import XmlTestMixin

from epg_grabber import app, generate
from epg_grabber.source import classes, utils


class TestVisionPlus(TestCase, XmlTestMixin):
    def test_vision(self):

        sites = SiteHelper.load_all_sites()

        channel = SiteHelper.load("visionplus")
        programs, channel = app.scrape_by_site("visionplus", channel["tvg_id"])

        xml_data = classes.EpgWriter.generate(channels=[channel], programs=programs)

        self.assertXmlDocument(xml_data)

class SiteHelper:
    @staticmethod
    def load(site):
        """Load first channel
        """
        os.path.abspath(os.curdir)
        project_root = os.path.abspath(os.curdir)
        metadata_path = os.path.join(project_root, "epg_grabber/sites/channels_metadata/"+site+".json")

        data = utils.load_channels_metadata(metadata_path)
        return data[0]

    @staticmethod
    def load_all_sites():
        return generate.get_sites()