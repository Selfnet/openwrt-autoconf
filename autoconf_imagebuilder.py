import json
import logging
import generate
import subprocess
from pathlib import Path

autoconf_template_file = "99-random-pws-autoconf"
preinstalled_packages = ["luci", "luci-theme-openwrt-2020"]


class AutoconfImageBuilder:
    def __init__(self, args) -> None:
        self.openwrt_profile = args.profile
        self.ssid_prefix = args.ssid_prefix
        self.imagebuilder_path = Path("imagebuilder")
        self.out_path = Path(args.output, self.openwrt_profile)

    def build_openwrt_image(self):
        ssid = generate.ssid(self.ssid_prefix)
        wifi_password = generate.password(16)
        root_password = generate.password(8)
        self.outfilename_without_extension = f"openwrt_{ssid}"
        self.out_path.mkdir(parents=True, exist_ok=True)
        self._generate_uci_defaults_file(ssid, wifi_password, root_password)
        self._imagebuilder_run_make()
        self._generate_metadata_file(ssid, wifi_password, root_password)
        self._rename_and_move_image()

    def _generate_uci_defaults_file(self, ssid, wifi_password, root_password):
        uci_defaults_path = self.imagebuilder_path / "files" / "etc" / "uci-defaults"
        uci_defaults_path.mkdir(parents=True, exist_ok=True)

        with open(autoconf_template_file, "r") as template_file:
            template = template_file.read()

        autoconf_content = template.format(
            ssid=ssid, wifi_password=wifi_password, root_password=root_password
        )

        autoconf_file = uci_defaults_path / autoconf_template_file
        with open(autoconf_file, "w") as autoconf:
            autoconf.write(autoconf_content)

    def _imagebuilder_run_make(self):
        try:
            subprocess.run(
                [
                    "make",
                    "image",
                    f"PROFILE={self.openwrt_profile}",
                    f"PACKAGES={' '.join(preinstalled_packages)}",
                    "FILES=files",
                ],
                cwd=self.imagebuilder_path,
                check=True,
            )
        except subprocess.CalledProcessError:
            logging.error("Error while running make command in imagebuilder directory")
            raise

    def _generate_metadata_file(self, ssid, wifi_password, root_password):
        metadata = {
            "ssid": ssid,
            "wifi_password": wifi_password,
            "root_password": root_password,
        }

        metadata_file = self.out_path / f"{self.outfilename_without_extension}.json"
        with open(metadata_file, "w") as file:
            json.dump(metadata, file, indent=4)

        logging.info(f"Metadata file generated: {metadata_file}")

    def _rename_and_move_image(self):
        targets_path = self.imagebuilder_path / "bin" / "targets"

        # Find file matching "openwrt*{self.openwrt_profile}*squashfs-sysupgrade.bin"
        # recursively in subdirectories to avoid needing to specify the target
        # as additional command line parameter
        sysupgrade_file = next(
            targets_path.glob(
                f"**/openwrt*{self.openwrt_profile}*squashfs-sysupgrade.bin"
            )
        )

        new_image_file = self.out_path / f"{self.outfilename_without_extension}.bin"
        sysupgrade_file.rename(new_image_file)
        logging.info(f"Image file generated: {new_image_file}")
