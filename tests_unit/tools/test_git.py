from libddog.tools.git import GitHelper

OUTPUT_TYPICAL = """\
origin  git@github.com:nearmap/libddog.git (fetch)
origin  git@github.com:nearmap/libddog.git (push)
"""


def test_parse_remotes() -> None:
    git = GitHelper()
    remotes = git.parse_remotes(OUTPUT_TYPICAL)

    assert len(remotes) == 2

    fst, snd = remotes

    assert fst.name == "origin"
    assert fst.url == "git@github.com:nearmap/libddog.git"
    assert fst.action == "fetch"

    assert snd.name == "origin"
    assert snd.url == "git@github.com:nearmap/libddog.git"
    assert snd.action == "push"


def test_get_repo_http_url() -> None:
    git = GitHelper()
    remotes = git.parse_remotes(OUTPUT_TYPICAL)
    url = git.get_repo_http_url(remotes)

    assert url == "https://github.com/nearmap/libddog"


def test_get_repo_name() -> None:
    git = GitHelper()
    remotes = git.parse_remotes(OUTPUT_TYPICAL)
    name = git.get_repo_name(remotes)

    assert name == "libddog"
