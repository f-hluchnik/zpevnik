"""Unit tests for the build number, run against throwaway Git repositories.

Run from the repository root: python3 -m unittest discover -s tools
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

from build_version import UNKNOWN_PATCH, UnknownHistory, build_patch, previous_version, song_count_change


class SongCountChange(unittest.TestCase):
    def test_added_minus_deleted(self):
        self.assertEqual(song_count_change(["A", "A", "D"]), 1)

    def test_replacing_a_song_does_not_change_the_count(self):
        self.assertEqual(song_count_change(["A", "D"]), 0)


class GitRepositoryTestCase(unittest.TestCase):
    """A throwaway repository on branch main, with helpers to commit and tag."""

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


class BuildPatch(GitRepositoryTestCase):

    def test_counts_commits_since_the_last_change_of_the_song_count(self):
        self.commit("first songs", {"songs/a.tex": "a", "songs/b.tex": "b"})
        self.assertEqual(build_patch(self.root), "0")
        self.commit("tools", {"notes": "1"})
        self.commit("edit a song", {"songs/a.tex": "a2"})
        self.assertEqual(build_patch(self.root), "2")

    def test_a_new_song_restarts_the_count(self):
        self.commit("first song", {"songs/a.tex": "a"})
        self.commit("tools", {"notes": "1"})
        self.commit("second song", {"songs/b.tex": "b"})
        self.assertEqual(build_patch(self.root), "0")
        self.commit("tools again", {"notes": "2"})
        self.assertEqual(build_patch(self.root), "1")

    def test_a_deleted_song_restarts_the_count(self):
        self.commit("songs", {"songs/a.tex": "a", "songs/b.tex": "b"})
        self.commit("remove one", {"songs/b.tex": None})
        self.commit("tools", {"notes": "1"})
        self.assertEqual(build_patch(self.root), "1")

    def test_replacing_a_song_keeps_counting(self):
        self.commit("songs", {"songs/a.tex": "a"})
        self.commit("swap", {"songs/a.tex": None, "songs/b.tex": "b"})
        self.assertEqual(build_patch(self.root), "1")

    def test_only_the_first_parent_is_counted(self):
        self.commit("song", {"songs/a.tex": "a"})
        self.git("checkout", "-q", "-b", "side")
        self.commit("side 1", {"notes": "1"})
        self.commit("side 2", {"notes": "2"})
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
        self.assertEqual(build_patch(self.root), "1")

    def test_a_song_added_on_a_merged_branch_counts_at_the_merge(self):
        self.commit("song", {"songs/a.tex": "a"})
        self.git("checkout", "-q", "-b", "side")
        self.commit("side song", {"songs/b.tex": "b"})
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
        self.assertEqual(build_patch(self.root), "0")

    def test_unknown_without_a_repository(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(build_patch(Path(empty)), UNKNOWN_PATCH)

    def test_unknown_in_a_shallow_clone(self):
        self.commit("song", {"songs/a.tex": "a"})
        self.commit("tools", {"notes": "1"})
        with tempfile.TemporaryDirectory() as parent:
            clone = Path(parent) / "clone"
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{self.root}", str(clone)],
                           check=True, capture_output=True)
            self.assertEqual(build_patch(clone), UNKNOWN_PATCH)


class PreviousVersion(GitRepositoryTestCase):
    def release(self, message: str, files: dict[str, str | None], version: str) -> None:
        """Commit files and tag the commit as the release of version."""
        self.commit(message, files)
        self.git("tag", f"v{version}")

    def test_is_the_last_release_before_the_song_count_changed(self):
        self.release("songs", {"songs/a.tex": "a"}, "1.01.0")
        self.release("edit a song", {"songs/a.tex": "a2"}, "1.01.1")
        self.release("new song", {"songs/b.tex": "b"}, "1.02.0")
        self.release("tools", {"notes": "1"}, "1.02.1")
        self.assertEqual(previous_version(self.root), "1.01.1")

    def test_a_new_song_in_the_commit_being_released_moves_it_on(self):
        self.release("songs", {"songs/a.tex": "a"}, "1.01.0")
        self.release("new song", {"songs/b.tex": "b"}, "1.02.0")
        self.commit("another new song, not released yet", {"songs/c.tex": "c"})
        self.assertEqual(previous_version(self.root), "1.02.0")

    def test_counts_a_removed_song_as_a_change(self):
        self.release("songs", {"songs/a.tex": "a", "songs/b.tex": "b"}, "1.02.0")
        self.release("remove one", {"songs/b.tex": None}, "1.01.0")
        self.assertEqual(previous_version(self.root), "1.02.0")

    def test_skips_tags_that_are_not_releases(self):
        self.release("songs", {"songs/a.tex": "a"}, "1.01.0")
        self.git("tag", "print-proof")
        self.release("new song", {"songs/b.tex": "b"}, "1.02.0")
        self.assertEqual(previous_version(self.root), "1.01.0")

    def test_unknown_without_a_release_before_the_change(self):
        self.commit("songs", {"songs/a.tex": "a"})
        self.release("new song", {"songs/b.tex": "b"}, "1.02.0")
        with self.assertRaises(UnknownHistory):
            previous_version(self.root)
