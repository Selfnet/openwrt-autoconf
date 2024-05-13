import logging
import argparse
import generate
import subprocess
from pathlib import Path

imagebuilder_path = "imagebuilder"
autoconf_template_file = "99-random-pws-autoconf"
preinstalled_packages = ["luci", "luci-theme-openwrt-2020"]


def parse_args():
    parser = argparse.ArgumentParser(description="OpenWrt Autoconf")
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory for generated images",
        default="output-images",
    )
    parser.add_argument(
        "profile",
        help="OpenWrt profile, run 'make info' in imagebuilder directory to get a list of available profiles",
    )
    return parser.parse_args()


def generate_uci_defaults_file(ssid, wifi_password, root_password):
    uci_defaults_path = Path(imagebuilder_path, "files", "etc", "uci-defaults")
    uci_defaults_path.mkdir(parents=True, exist_ok=True)

    with open(autoconf_template_file, "r") as template_file:
        template = template_file.read()

    autoconf_content = template.format(
        ssid=ssid, wifi_password=wifi_password, root_password=root_password
    )

    autoconf_file = Path(uci_defaults_path, autoconf_template_file)
    with open(autoconf_file, "w") as autoconf:
        autoconf.write(autoconf_content)


def imagebuilder_run_make(profile):
    try:
        subprocess.run(
            [
                "make",
                "image",
                f"PROFILE={profile}",
                f"PACKAGES={' '.join(preinstalled_packages)}",
                "FILES=files",
            ],
            cwd=imagebuilder_path,
            check=True,
        )
    except subprocess.CalledProcessError:
        logging.error("Error while running make command in imagebuilder directory")
        raise


def create_openwrt_image(ssid_prefix, openwrt_profile):
    ssid = generate.ssid(ssid_prefix)
    wifi_password = generate.password(16)
    root_password = generate.password(8)
    generate_uci_defaults_file(ssid, wifi_password, root_password)
    imagebuilder_run_make(openwrt_profile)

    # Rename generated image and move to output directory


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    create_openwrt_image("OpenWrt", args.profile)


if __name__ == "__main__":
    main()
