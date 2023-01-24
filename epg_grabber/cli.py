from epg_grabber.models import InputConfig, TvData, TvDataItem
from epg_grabber.app import run, save_to_file
from epg_grabber.constants import SHOW_INDENT, CHANNELS_METADATA_DIR
from epg_grabber.utils import get_sites
import argparse
import sys
import json


def show(args):
    sites = get_sites()

    if args.show == "all":
        print("To view channel metadata for a site, pass --show {site}.")
        for site in sites:
            print(f"\t{site}")

    elif args.show in sites:
        # JSON file
        with open(f"{CHANNELS_METADATA_DIR/args.show}.json", "r") as f:
            channels = json.load(f)
            print(json.dumps(channels, indent=SHOW_INDENT))


def local(args):
    input_config = InputConfig.parse_file(args.file)

    if args.days:
        input_config.days = 7 if args.days > 7 else args.days

    if args.workers:
        input_config.workers = args.workers

    programmes, channels = run(input_config=input_config)
    tv_data_item = TvDataItem(channel=channels, programme=programmes)
    tv_data = TvData(tv=tv_data_item)
    save_to_file(tv_data=tv_data, filename=args.output)


def online(args):
    raise NotImplementedError


def main():
    parent_parser = argparse.ArgumentParser(
        description="epg-grabber. Built in Python, this is another Internet-based scraper and it provides a very rich EPG data set for some supported sites.")
    parent_parser.add_argument(
        "-s",
        "--show",
        help="Show site supported in this version. To view channel metadata for a site, pass --show {site}.",
        nargs="?",
        const="all"
    )

    mode = parent_parser.add_subparsers(title="mode", dest="mode")
    local_parser = mode.add_parser(
        "local",
        add_help=True,
        description="Run EPG grabbing locally by suppling an input config file.",
    )
    local_parser.add_argument(
        "-f", "--file", help="File of the EPG config", required=True)
    local_parser.add_argument(
        "-o", "--output", help="XMLTV EPG file output", required=True)
    local_parser.add_argument(
        "-d",
        "--days",
        type=int,
        help="No of days. Defaults to 1. Setting no. of days here will override the one in your input configuration file.",
        default=1,
    )
    local_parser.add_argument(
        "-w",
        "--workers",
        type=int,
        help="No of workers for parallelism. Defaults to 1.",
        default=1,
    )

    # TODO: Add online_parser with external URL support
    # online_parser = mode.add_parser("online", add_help=True, description="Online EPG grabbing")
    # online_parser.add_argument("--url", help="Direct URL of the EPG config raw text file", required=True)

    args = parent_parser.parse_args(args=None if sys.argv[1:] else ["--help"])

    ###
    # args router
    ###

    if args.show:
        show(args)

    if args.mode == "local":
        local(args)

    # if args.mode == 'online': online(args)


if __name__ == '__main__':
    main()
