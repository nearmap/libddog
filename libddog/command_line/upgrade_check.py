import os
import re
import sys
import tempfile
import time
import traceback
from typing import List, Optional

from packaging.version import Version

import libddog
from libddog.command_line.console import ConsoleWriter
from libddog.tools.process import CmdResult, invoke


class VersionDetectionFailed(Exception):
    pass


class UpgradeChecker:
    """
    Checks whether there is a more recent version of libddog available.
    Runs pip install libddog==X.X.X to induce the following error:

    ERROR: Could not find a version that satisfies the requirement libddog==X.X.X \
        (from versions: 0.0.1, 0.0.2, 0.0.3, 0.0.4, 0.0.5, 0.0.6, 0.0.7a0, 0.0.7a1)
    ERROR: No matching distribution found for libddog==X.X.X

    Parses the error string to discover the most recent version.
    """

    rx_err = re.compile(
        "ERROR: Could not find a version that satisfies the requirement.*"
        "\\(from versions: (.*?)\\)"
    )

    error_log_filename = "libddog-upgrade-check-error.log"
    last_run_filename = "libddog-upgrade-check-last-run"

    def __init__(self) -> None:
        path = tempfile.gettempdir()
        self.error_log_filepath = os.path.join(path, self.error_log_filename)
        self.last_run_filepath = os.path.join(path, self.last_run_filename)

        # check once every 24h
        self.check_interval_s = 3600 * 24

        self.writer = ConsoleWriter()

        self.installed_version = Version(libddog.__version__)
        self.proj_name = "libddog"
        self.changelog_url = (
            "https://github.com/nearmap/libddog/blob/master/CHANGELOG.md"
        )

    def run_mock_pip_install(self) -> CmdResult:
        # try to install a version we know doesn't exist
        args = ["pip", "install", "libddog==X.X.X"]

        # we don't want a keyring popup
        environ = {"PYTHON_KEYRING_BACKEND": "keyring.backends.null.Keyring"}

        return invoke(args=args, environ=environ)

    def parse_versions(self, result: CmdResult) -> List[Version]:
        output = result.stderr.decode()  # could raise

        match = self.rx_err.search(output)
        if match:
            versions_str = match.group(1)
            versions = versions_str.split(",")
            versions = [ver.strip() for ver in versions]
            version_objs = [Version(ver) for ver in versions]
            return version_objs

        raise VersionDetectionFailed(result)

    def get_latest_version(self, versions: List[Version]) -> Version:
        versions = [ver for ver in versions if not ver.is_prerelease]
        versions.sort()
        return versions[-1]

    def get_current_run_time(self) -> float:
        return time.time()

    def get_last_run_time(self) -> Optional[float]:
        try:
            with open(self.last_run_filepath, "r") as fl:
                content = fl.read()
                return float(content.strip())
        except (FileNotFoundError, ValueError):
            pass

        return None

    def write_last_run_time(self, tm: float) -> None:
        with open(self.last_run_filepath, "w") as fl:
            content = f"{tm}"
            fl.write(content)

    def should_check(self) -> bool:
        current_run_time = self.get_current_run_time()
        last_run_time = self.get_last_run_time()

        if last_run_time and (current_run_time - last_run_time) < self.check_interval_s:
            return False

        self.write_last_run_time(current_run_time)
        return True

    def unsafe_run(self) -> None:
        if not self.should_check():
            return

        result = self.run_mock_pip_install()
        versions = self.parse_versions(result)
        latest_version = self.get_latest_version(versions)

        if latest_version > self.installed_version:
            block = (
                f"Running {self.proj_name} version: {self.installed_version}. "
                f"The latest version is {latest_version}. "
                f"Changelog: {self.changelog_url}"
                f"\nTo upgrade run: pip install -U libddog"
            )
            self.writer.errorln(block)

    def run(self) -> None:
        result = None
        triple = None

        try:
            self.unsafe_run()

        except VersionDetectionFailed as ex:
            result = ex.args[0]
            triple = sys.exc_info()

        except Exception as ex:
            triple = sys.exc_info()

        if triple:
            _, _, tb = triple
            tb_lst = traceback.format_tb(tb)
            tb_block = "".join(tb_lst)
            content = f"Traceback:\n{tb_block}\n"

            if result:
                content = f"{content}\nCmdResult: {result!r}\n"

            with open(self.error_log_filepath, "w") as fl:
                fl.write(content)

            block = (
                f"Failed to detect latest version, "
                f"error saved to: {self.error_log_filepath}"
            )
            self.writer.errorln(block)
