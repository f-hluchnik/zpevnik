"""The build number of the songbook version, counted from the Git history.

The version is `major.minor.patch`. `major.minor` is the song count plus 100 (see
generate.py); the patch is the number of first-parent commits on the current branch
since the last commit that changed the song count, so it is the same in CI and in a
local build with the full history. Nothing is stored. Without the full history (no
Git, no repository, a shallow clone) the patch is UNKNOWN_PATCH, visibly incomplete.

Python >= 3.11, standard library only.
"""
import subprocess
from pathlib import Path

from paths import SONGS_DIR

UNKNOWN_PATCH = "?"
SONG_FILES = f"{SONGS_DIR}/*.tex"
COMMIT_MARK = "@"  # starts the hash line of a commit in the log output
ADDED, DELETED = "A", "D"


def git(root: Path, *args: str) -> str | None:
    """Output of `git <args>` in root, or None if Git is missing or the command fails."""
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout


def song_count_change(lines: list[str]) -> int:
    """Songs added minus songs deleted in one commit's `--name-status` lines."""
    statuses = [line.split("\t", 1)[0] for line in lines]
    return statuses.count(ADDED) - statuses.count(DELETED)


def last_count_change(root: Path) -> str | None:
    """The newest first-parent commit that changed the song count, or None if there is none."""
    log = git(root, "log", "--first-parent", "--diff-filter=AD", "--name-status",
              f"--format={COMMIT_MARK}%H", "--", SONG_FILES)
    if log is None:
        return None
    commit, lines = None, []
    for line in [*log.splitlines(), COMMIT_MARK]:  # the last mark flushes the final commit
        if line.startswith(COMMIT_MARK):
            if commit is not None and song_count_change(lines) != 0:
                return commit
            commit, lines = line[len(COMMIT_MARK):], []
        elif line:
            lines.append(line)
    return None


def build_patch(root: Path) -> str:
    """Commits since the last change of the song count, or UNKNOWN_PATCH if Git can't tell."""
    if git(root, "rev-parse", "--is-shallow-repository") != "false\n":
        return UNKNOWN_PATCH
    changed = last_count_change(root)
    if changed is None:
        return UNKNOWN_PATCH
    count = git(root, "rev-list", "--first-parent", "--count", f"{changed}..HEAD")
    return count.strip() if count else UNKNOWN_PATCH
