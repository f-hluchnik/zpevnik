"""The build number of the songbook version, counted from the Git history.

The version is `major.minor.patch`. `major.minor` is the song count plus 100 (see
generate.py); the patch is the number of first-parent commits on the current branch
since the last commit that changed the song count, so it is the same in CI and in a
local build with the full history. Nothing is stored. Without the full history (no
Git, no repository, a shallow clone) the patch is UNKNOWN_PATCH, visibly incomplete.

The previous version is the release before that commit (previous_version): the website
links to the comparison of the two releases, where the songs added since are listed.

Python >= 3.11, standard library only.
"""
import subprocess
from pathlib import Path

from paths import SONGS_DIR

UNKNOWN_PATCH = "?"
SONG_PATHSPEC = f"{SONGS_DIR}/*.tex"
COMMIT_START = "\0"  # starts every commit in the log output (git writes it for %x00)
ADDED, DELETED = "A", "D"
RELEASE_TAG_PREFIX = "v"  # a release is tagged v<version> (the CI's release step)


class UnknownHistory(Exception):
    """Git can't tell the build number: no Git, no repository, a shallow clone."""


def git(root: Path, *args: str) -> str:
    """Output of `git <args>` in root; UnknownHistory if Git is missing or the command fails."""
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                              text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise UnknownHistory from error


def song_count_change(statuses: list[str]) -> int:
    """Songs added minus songs deleted, from the `--name-status` letters of one commit."""
    return statuses.count(ADDED) - statuses.count(DELETED)


def last_count_change(root: Path) -> str:
    """The newest first-parent commit that changed the song count."""
    log = git(root, "log", "--first-parent", "--diff-filter=AD", "--name-status",
              "--format=%x00%H", "--", SONG_PATHSPEC)
    for commit in log.split(COMMIT_START)[1:]:
        sha, _, changes = commit.partition("\n")
        statuses = [line.split("\t")[0] for line in changes.splitlines() if line]
        if song_count_change(statuses) != 0:
            return sha
    raise UnknownHistory


def require_full_history(root: Path) -> None:
    """UnknownHistory unless root is a repository with its full history (not a shallow clone)."""
    if git(root, "rev-parse", "--is-shallow-repository") != "false\n":
        raise UnknownHistory


def build_patch(root: Path) -> str:
    """Commits since the last change of the song count, or UNKNOWN_PATCH if Git can't tell."""
    try:
        require_full_history(root)
        since = last_count_change(root)
        return git(root, "rev-list", "--first-parent", "--count", f"{since}..HEAD").strip()
    except UnknownHistory:
        return UNKNOWN_PATCH


def previous_version(root: Path) -> str:
    """The version of the newest release before the last change of the song count: the
    release the website compares the current one with to show the new songs (D-184).
    UnknownHistory if Git can't tell (no full history, no release tag before that change)."""
    require_full_history(root)
    before_change = f"{last_count_change(root)}^"
    tag = git(root, "describe", "--tags", "--abbrev=0", "--first-parent",
              f"--match={RELEASE_TAG_PREFIX}*", before_change).strip()
    return tag.removeprefix(RELEASE_TAG_PREFIX)
