"""Unit tests for the build number, run against throwaway Git repositories.

Run from the repository root: python3 -m unittest discover -s tools
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

from build_version import UNKNOWN_PATCH, build_patch, song_count_change


class SongCountChange(unittest.TestCase):
    def test_added_minus_deleted(self):
        self.assertEqual(song_count_change(["A", "A", "D"]), 1)

    def test_replacing_a_song_does_not_change_the_count(self):
        self.assertEqual(song_count_change(["A", "D"]), 0)


class BuildPatch(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.root), *args],
                       check=True, capture_output=True)

    def commit(self, message: str, files: dict[str, str | None]) -> None:
        """Commit files (path -> text, None deletes)."""
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(exist_ok=True)
            if text is None:
                path.unlink()
            else:
                path.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def test_counts_commits_since_the_last_change_of_the_song_count(self):
        self.commit("first songs", {"pisnicky/a.tex": "a", "pisnicky/b.tex": "b"})
        self.assertEqual(build_patch(self.root), "0")
        self.commit("tools", {"notes": "1"})
        self.commit("edit a song", {"pisnicky/a.tex": "a2"})
        self.assertEqual(build_patch(self.root), "2")

    def test_a_new_song_restarts_the_count(self):
        self.commit("first song", {"pisnicky/a.tex": "a"})
        self.commit("tools", {"notes": "1"})
        self.commit("second song", {"pisnicky/b.tex": "b"})
        self.assertEqual(build_patch(self.root), "0")
        self.commit("tools again", {"notes": "2"})
        self.assertEqual(build_patch(self.root), "1")

    def test_a_deleted_song_restarts_the_count(self):
        self.commit("songs", {"pisnicky/a.tex": "a", "pisnicky/b.tex": "b"})
        self.commit("remove one", {"pisnicky/b.tex": None})
        self.commit("tools", {"notes": "1"})
        self.assertEqual(build_patch(self.root), "1")

    def test_replacing_a_song_keeps_counting(self):
        self.commit("songs", {"pisnicky/a.tex": "a"})
        self.commit("swap", {"pisnicky/a.tex": None, "pisnicky/b.tex": "b"})
        self.assertEqual(build_patch(self.root), "1")

    def test_only_the_first_parent_is_counted(self):
        self.commit("song", {"pisnicky/a.tex": "a"})
        self.git("checkout", "-q", "-b", "side")
        self.commit("side 1", {"notes": "1"})
        self.commit("side 2", {"notes": "2"})
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
        self.assertEqual(build_patch(self.root), "1")

    def test_a_song_added_on_a_merged_branch_counts_at_the_merge(self):
        self.commit("song", {"pisnicky/a.tex": "a"})
        self.git("checkout", "-q", "-b", "side")
        self.commit("side song", {"pisnicky/b.tex": "b"})
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
        self.assertEqual(build_patch(self.root), "0")

    def test_unknown_without_a_repository(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(build_patch(Path(empty)), UNKNOWN_PATCH)

    def test_unknown_in_a_shallow_clone(self):
        self.commit("song", {"pisnicky/a.tex": "a"})
        self.commit("tools", {"notes": "1"})
        with tempfile.TemporaryDirectory() as parent:
            clone = Path(parent) / "clone"
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{self.root}", str(clone)],
                           check=True, capture_output=True)
            self.assertEqual(build_patch(clone), UNKNOWN_PATCH)


if __name__ == "__main__":
    unittest.main()
