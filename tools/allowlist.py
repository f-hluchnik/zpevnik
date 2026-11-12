"""Reading an allow-list: song ids one per line, "#" starts a comment.

A tool that has an exception to a rule keeps the song ids in a text file of tools/
(paths.py) instead of marking the song itself, so the song files stay free of markers
for the tools. The hidden songs (data/hidden.txt) are a list in the same format.
A missing file is an empty list.

Python >= 3.11, standard library only.
"""
from pathlib import Path

COMMENT_START = "#"


def read_allowlist(path: Path) -> set[str]:
    """The song ids listed in the file, without comments and blank lines."""
    if not path.exists():
        return set()
    lines = (line.split(COMMENT_START, 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return {line for line in lines if line}
