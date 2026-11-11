"""Unit tests for reading an allow-list.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path

from allowlist import read_allowlist


class ReadAllowlist(unittest.TestCase):
    def read(self, text: str) -> set[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "list.txt"
            path.write_text(text, encoding="utf-8")
            return read_allowlist(path)

    def test_ids_are_read_one_per_line(self):
        self.assertEqual(self.read("alfa\nbeta\n"), {"alfa", "beta"})

    def test_comments_and_blank_lines_are_ignored(self):
        self.assertEqual(self.read("# why\n\nalfa  # a score only\n   \n"), {"alfa"})

    def test_a_missing_file_is_an_empty_list(self):
        self.assertEqual(read_allowlist(Path(tempfile.gettempdir()) / "no-such-allowlist.txt"), set())


if __name__ == "__main__":
    unittest.main()
