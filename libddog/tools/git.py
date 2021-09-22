import os
import re
import subprocess
from typing import List, Optional


class GitRemote:
    def __init__(self, *, name: str, url: str, action: str) -> None:
        self.name = name
        self.url = url
        self.action = action


class GitHelper:
    # origin  git@github.com:nearmap/libddog.git (fetch)
    rx_remote_line = re.compile("^([^ ]+)\\s+([^ ]+)\\s+\\(([^ ]+)\\)$")

    # git@github.com:nearmap/libddog.git
    rx_remote_url = re.compile("([^ ]+)@([^:]+):(.*)")

    def get_current_branch(self) -> Optional[str]:
        code, output = subprocess.getstatusoutput("git branch --show-current")
        if code == 0:
            return output

        return None

    def get_remotes(self) -> Optional[str]:
        # $ git remote -v
        # origin  git@github.com:nearmap/libddog.git (fetch)
        # origin  git@github.com:nearmap/libddog.git (push)
        code, output = subprocess.getstatusoutput("git remote -v")
        if code == 0:
            return output

        return None

    def parse_remotes(self, output: str) -> List[GitRemote]:
        remotes = []
        lines = output.splitlines()

        for line in lines:
            match = self.rx_remote_line.match(line)
            if match:
                name, url, action = match.groups()
                remote = GitRemote(name=name, url=url, action=action)
                remotes.append(remote)

        return remotes

    def parse_remote_http_url(self, verbatim_url: str) -> Optional[str]:
        # git@github.com:nearmap/libddog.git -> https://github.com/nearmap/libddog
        match = self.rx_remote_url.match(verbatim_url)
        if match:
            _, netloc, path = match.groups()
            if path.endswith(".git"):
                path = path[:-4]
            return f"https://{netloc}/{path}"

        return None

    def get_remote_with_http_url(self, remotes: List[GitRemote]) -> Optional[GitRemote]:
        if not remotes:
            return None

        # Remotes can be called anything and we have reason to prefer any
        # particular remote over any other, but most repos will have only one
        # remote called 'origin' which was set up when the repo was cloned, or
        # the first time the repo was pushed to some other location.
        chosen_remote_name = None
        default_remote_name = "origin"

        unique_remote_names = {remote.name for remote in remotes}

        if len(unique_remote_names) == 1:
            chosen_remote_name = list(unique_remote_names)[0]
        elif default_remote_name in unique_remote_names:
            chosen_remote_name = default_remote_name
        else:
            # pick the first remote
            chosen_remote_name = remotes[0].name

        matched_remotes = [
            remote for remote in remotes if remote.name == chosen_remote_name
        ]

        for remote in matched_remotes:
            http_url = self.parse_remote_http_url(remote.url)
            if http_url:
                return remote

        return None

    def get_repo_http_url(self, remotes: List[GitRemote]) -> Optional[str]:
        remote = self.get_remote_with_http_url(remotes)
        if remote:
            return self.parse_remote_http_url(remote.url)

        return None

    def get_repo_name(self, remotes: List[GitRemote]) -> Optional[str]:
        http_url = self.get_repo_http_url(remotes)
        if http_url:
            name = os.path.basename(http_url)
            return name

        return None
