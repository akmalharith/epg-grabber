import importlib
import json
import os
import logging

from epg_grabber.config.constants import CONFIG_DIR, METADATA_DIR, SITES_DIR, TITLE


log = logging.getLogger(TITLE)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=os.environ.get("LOGLEVEL", "INFO"),
    datefmt='%Y-%m-%d %H:%M:%S')


def generate_config(site_name, channel_names):
    filepath = os.path.join(CONFIG_DIR, site_name + "_channels.txt")

    try:
        open(filepath).close()
    except FileNotFoundError:
        pass
    with open(filepath, "w") as infile:
        for channel in channel_names:
            infile.write(
                site_name + ";" +
                channel.tvg_id +
                "\n"
            )
        infile.close()

    log.info(
        "%s_channels.txt successfully generated. (%d channels)",
        site_name,
        len(channel_names))


def generate_metadata(site_name, channel_names):
    filepath = os.path.join(METADATA_DIR, site_name + ".json")
    channel_metadata = []
    for channel in channel_names:
        channel_metadata.append({'id': channel.id,
                                 'tvg_id': channel.tvg_id,
                                 'tvg_name': channel.tvg_name,
                                 'tvg_logo': channel.tvg_logo})

    try:
        open(filepath).close()
    except FileNotFoundError:
        pass
    with open(filepath, "w") as infile:
        json.dump(channel_metadata, infile)
        infile.close()

    log.info(site_name + ".json metadata generated.")


def generate(site_name):
    try:
        site = importlib.import_module('epg_grabber.sites.' + site_name)
    except Exception:
        return  # Don't stop generate() if any of the modules failed
    log.info('Generating a new channel list for ' + site_name)

    channel_names = site.get_all_channels()

    generate_config(site_name, channel_names)
    generate_metadata(site_name, channel_names)


def generate_all():
    log.info('Generating all channels lists')

    for channel in get_sites():
        generate(channel)

    log.info('Done!')


def get_sites():
    sites = []

    for l in os.listdir(SITES_DIR):
        if os.path.isfile(os.path.join(SITES_DIR, l)):
            if l.endswith('.py'):
                if not l == '__init__.py':
                    if not l.endswith('_auth.py'):
                        sites.append(l[:-3])

    return sites

if __name__ == '__main__':
    generate_all()