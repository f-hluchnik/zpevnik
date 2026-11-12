"""Unit test that tools/README.md lists every module and package of tools/.

Run from the repository root: python3 -m unittest discover -s tools
"""
import re
import unittest

from paths import REPO_ROOT

TOOLS_DIR = REPO_ROOT / "tools"
TOOLS_README = TOOLS_DIR / "README.md"
LISTED_MODULE = re.compile(r"^\| `(\w+)(?:\.py|/)` \|", re.MULTILINE)  # the first cell: `name.py` or `name/`
TESTS_PACKAGE = "tests"


class ToolsReadme(unittest.TestCase):
    def test_every_module_has_exactly_one_row(self):
        packages = [path.parent.name for path in TOOLS_DIR.glob("*/__init__.py")]
        modules = sorted([path.stem for path in TOOLS_DIR.glob("*.py")]
                         + [name for name in packages if name != TESTS_PACKAGE])
        listed = sorted(LISTED_MODULE.findall(TOOLS_README.read_text(encoding="utf-8")))
        self.assertEqual(listed, modules)
