import logging
import argparse
from autoconf_imagebuilder import AutoconfImageBuilder


def parse_args():
    parser = argparse.ArgumentParser(description="OpenWrt Autoconf")
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory base for generated images",
        default="out",
    )
    parser.add_argument(
        "profile",
        help="OpenWrt profile, run 'make info' in imagebuilder directory to get a list of available profiles",
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()

    AutoconfImageBuilder(args).build_openwrt_image()


if __name__ == "__main__":
    main()
