"""Unit test that tools/README.md lists every module of tools/.

Run from the repository root: python3 -m unittest discover -s tools
"""
import re
import unittest

from paths import REPO_ROOT

TOOLS_DIR = REPO_ROOT / "tools"
TOOLS_README = TOOLS_DIR / "README.md"
LISTED_MODULE = re.compile(r"^\| `(\w+)\.py` \|", re.MULTILINE)  # the first cell of a table row


class ToolsReadme(unittest.TestCase):
    def test_every_module_has_exactly_one_row(self):
        modules = sorted(path.stem for path in TOOLS_DIR.glob("*.py"))
        listed = sorted(LISTED_MODULE.findall(TOOLS_README.read_text(encoding="utf-8")))
        self.assertEqual(listed, modules)
