import importlib
import json
import os
import logging

sites_dir = "sites"
metadata_dir = os.path.join(sites_dir, "channels_metadata")
config_dir = os.path.join(sites_dir, "channels_config")

log = logging.getLogger("epg_grabber_generate_metadata")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def generate_config(site_name, channel_names):
    filepath = os.path.join(config_dir, site_name + "_channels.txt")

    try:
        open(filepath).close()
    except FileNotFoundError:
        pass
    with open(filepath, "w") as infile:
        for channel in channel_names:
            infile.write(
                site_name + ";" +
                channel.tvg_id.replace("!","").replace("-","") +
                "\n"
            )
        infile.close()

    log.info(site_name + "_channels.txt succesfully generated. (" +
          str(len(channel_names)) + " channels)")


def generate_metadata(site_name, channel_names):
    filepath = os.path.join(metadata_dir, site_name + ".json")
    channel_metadata = []
    for channel in channel_names:
        channel_metadata.append(
            {'id': channel.id, 'tvg_id': channel.tvg_id, 'tvg_name': channel.tvg_name, 'tvg_logo': channel.tvg_logo}
        )

    try:
        open(filepath).close()
    except FileNotFoundError:
        pass
    with open(filepath, "w") as infile:
        json.dump(channel_metadata, infile)
        infile.close()

    log.info(site_name + ".json metadata generated.")


def generate(site_name):
    site = importlib.import_module('sites.' + site_name)
    log.info('Generating a new channel list for ' + site_name)

    channel_names = site.get_all_channels()

    generate_config(site_name, channel_names)
    generate_metadata(site_name, channel_names)


def generate_all():
    log.info('Generating all channels lists')

    for channel in get_channels():
        generate(channel)

    log.info('Done!')


def get_channels():
    channels = []

    for l in os.listdir(sites_dir):
        if os.path.isfile(os.path.join(sites_dir, l)):
            if l.endswith('.py'):
                if not l == '__init__.py':
                    if not l.endswith('_auth.py'):
                        channels.append(l[:-3])

    return channels


generate_all()
