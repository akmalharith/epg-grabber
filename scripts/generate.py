# Generate script is not meant to be part of the epg_grabber package
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import argparse
import json

epg_grabber_dir = Path(__file__).parents[1]/"epg_grabber"
sites_dir = epg_grabber_dir/"sites"
channels_metadata_dir = sites_dir/"channels_metadata"

generate_parser = argparse.ArgumentParser(
    description="Generate channel metadata for a site.")
generate_parser.add_argument(
    "-s",
    "--site",
    help="Site name.",
    required=True
)

args = generate_parser.parse_args()

# Load from file
sites_file = epg_grabber_dir/"sites"/f"{args.site}.py"
spec = spec_from_file_location(args.site, sites_file)
site = module_from_spec(spec)
spec.loader.exec_module(site)

# Save JSON channels metadata
channel_metadata = site.generate().json()
channel_metadata_json_data = json.loads(channel_metadata)
# 
with open(channels_metadata_dir/f"{args.site}.json", "w") as outfile:
    json.dump(channel_metadata_json_data, outfile, indent=4)
