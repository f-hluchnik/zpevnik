"""Unit tests for the score export (no MuseScore needed: the SVGs are synthetic).

Run from the repository root: python3 -m unittest discover -s tools
"""
import os
import stat
import sys
import tempfile
import textwrap
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from scores import (ScoreError, StaffPosition, chord_colour, export_svg, is_up_to_date, outputs,
                    paint_chord_names, placement_tex, remove_page_background, run, staff_position,
                    system_width_pt)

# 100 SVG units are 10 mm wide, so one unit is 0.1 mm = 0.283465 pt.
PT_PER_UNIT = 0.1 / 25.4 * 72


def svg(*lines: tuple[float, float], extra: str = "") -> ElementTree.Element:
    """An SVG 10 mm wide with staff lines starting at (x, y), in SVG units."""
    polylines = "".join(f'<polyline class="StaffLines" points="{x},{y} 100,{y}"/>' for x, y in lines)
    return ElementTree.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="10mm" height="10mm" viewBox="0 0 100 100">'
        f'{extra}{polylines}</svg>')


def tab_staff(top: float, x: float = 0, spacing: float = 3) -> list[tuple[float, float]]:
    return [(x, top + i * spacing) for i in range(6)]


class StaffPositionTest(unittest.TestCase):
    def test_middle_and_left_of_a_single_staff(self):
        position = staff_position(svg(*tab_staff(top=20)))
        self.assertAlmostEqual(position.middle, 27.5 * PT_PER_UNIT)
        self.assertAlmostEqual(position.left, 0)

    def test_only_the_first_system_counts(self):
        position = staff_position(svg(*tab_staff(top=40), *tab_staff(top=10)))
        self.assertAlmostEqual(position.middle, 17.5 * PT_PER_UNIT)

    def test_notation_above_tab_is_the_first_staff(self):
        notation = [(0, 10 + i * 2) for i in range(5)]
        position = staff_position(svg(*notation, *tab_staff(top=25)))
        self.assertAlmostEqual(position.middle, 14 * PT_PER_UNIT)

    def test_ink_left_of_the_staff_moves_its_left_end(self):
        self.assertAlmostEqual(staff_position(svg(*tab_staff(top=20, x=4))).left, 4 * PT_PER_UNIT)

    def test_without_staff_lines_it_fails(self):
        with self.assertRaises(ScoreError):
            staff_position(svg((0, 10)))

    def test_lines_that_are_not_evenly_spaced_are_no_staff(self):
        with self.assertRaisesRegex(ScoreError, "first staff has 2"):
            staff_position(svg((0, 10), (0, 12), (0, 30), (0, 33), (0, 36)))

    def test_segments_of_one_line_count_once_from_the_leftmost(self):
        lines = tab_staff(top=20, x=10) + [(2, 20)]
        self.assertAlmostEqual(staff_position(svg(*lines)).left, 2 * PT_PER_UNIT)

    def test_positions_count_from_the_view_box_origin(self):
        image = svg(*tab_staff(top=20, x=5))
        image.set("viewBox", "5 10 100 100")
        position = staff_position(image)
        self.assertAlmostEqual((position.left, position.middle), (0, 17.5 * PT_PER_UNIT))

    def test_malformed_points_fail(self):
        image = svg(*tab_staff(top=20))
        image[0].set("points", "0;20 100;20")
        with self.assertRaisesRegex(ScoreError, "malformed"):
            staff_position(image)

    def test_without_size_in_mm_it_fails(self):
        image = svg(*tab_staff(top=20))
        image.set("width", "100")
        with self.assertRaises(ScoreError):
            staff_position(image)


class ImageTest(unittest.TestCase):
    def test_chord_names_get_the_colour_and_nothing_else(self):
        image = svg(*tab_staff(top=20), extra='<path class="Harmony" d="M0,0"/><path class="Note" d="M0,0"/>')
        paint_chord_names(image, "#B82727")
        fills = {element.get("class"): element.get("fill") for element in image if element.get("class")}
        self.assertEqual((fills["Harmony"], fills["Note"]), ("#B82727", None))

    def test_page_background_is_removed(self):
        image = svg(*tab_staff(top=20), extra='<title>a</title><path class="" fill="#FFFFFF" d="M0,0 L100,0"/>')
        remove_page_background(image)
        self.assertEqual([element.get("class") for element in image], [None] + ["StaffLines"] * 6)

    def test_only_the_page_painted_first_is_removed(self):
        image = svg(*tab_staff(top=20))
        image.append(ElementTree.fromstring('<path class="" fill="#ffffff" d="M0,0"/>'))
        remove_page_background(image)
        self.assertEqual(len(image), 7)


class SettingsTest(unittest.TestCase):
    def test_chord_colour_from_the_style_file(self):
        self.assertEqual(chord_colour("\\definecolor{chordred}{RGB}{184, 39, 39}"), "#B82727")

    def test_missing_chord_colour_fails(self):
        with self.assertRaises(ScoreError):
            chord_colour("\\definecolor{blue}{RGB}{0, 0, 255}")

    def test_system_width_is_the_printable_width(self):
        self.assertAlmostEqual(system_width_pt("<pagePrintableWidth>7.5</pagePrintableWidth>"), 540)

    def test_placement_file(self):
        self.assertEqual(placement_tex(StaffPosition(left=0, middle=40.054), 538.75),
                         "\\zpscoregeometry{0.00pt}{40.05pt}{538.75pt}\n")


class UpToDateTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.root))
        self.score = self.root / "scores" / "a.mscz"
        self.style = self.root / "scores" / "zpevnik.mss"
        self.score.parent.mkdir()
        self.score.write_text("score")
        self.style.write_text("style")
        os.utime(self.score, (100, 100))
        os.utime(self.style, (100, 100))

    def write_outputs(self, mtime: float) -> None:
        for file in outputs(self.score, self.root):
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("out")
            os.utime(file, (mtime, mtime))

    def test_missing_outputs_are_not_up_to_date(self):
        self.assertFalse(is_up_to_date(self.score, self.root, [self.style]))

    def test_outputs_newer_than_every_input_are_up_to_date(self):
        self.write_outputs(200)
        self.assertTrue(is_up_to_date(self.score, self.root, [self.style]))

    def test_a_newer_style_makes_them_stale(self):
        self.write_outputs(200)
        os.utime(self.style, (300, 300))
        self.assertFalse(is_up_to_date(self.score, self.root, [self.style]))


class ExportTest(unittest.TestCase):
    """export_svg against a stand-in for MuseScore that writes <name>-<page>.svg like it does."""

    def fake_mscore(self, pages: int) -> str:
        script = Path(self.work_dir) / "mscore"
        script.write_text(textwrap.dedent(f"""\
            #!{sys.executable}
            import sys
            from pathlib import Path
            out = Path(sys.argv[sys.argv.index("-o") + 1])
            for page in range(1, {pages} + 1):
                out.with_name(f"{{out.stem}}-{{page}}.svg").write_text("<svg/>")
            """))
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        return str(script)

    def setUp(self):
        self.work_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.work_dir))
        self.out_dir = Path(self.work_dir) / "out"
        self.out_dir.mkdir()

    def test_one_page(self):
        page = export_svg(self.fake_mscore(1), Path("scores/a.mscz"), Path("style.mss"), self.out_dir)
        self.assertEqual(page.name, "a-1.svg")

    def test_more_pages_fail(self):
        with self.assertRaisesRegex(ScoreError, "2 pages"):
            export_svg(self.fake_mscore(2), Path("scores/a.mscz"), Path("style.mss"), self.out_dir)


class FailureTest(unittest.TestCase):
    def test_the_message_names_the_program_and_drops_the_startup_warnings(self):
        code = ('import sys; print("qt.qml.typeregistration: Invalid QML element name", file=sys.stderr);'
                ' print("cannot open the score"); sys.exit(40)')
        with self.assertRaises(ScoreError) as caught:
            run([sys.executable, "-c", code], "export of a.mscz")
        message = str(caught.exception)
        self.assertIn("failed (40)", message)
        self.assertIn(sys.executable, message)
        self.assertIn("cannot open the score", message)
        self.assertNotIn("typeregistration", message)


if __name__ == "__main__":
    unittest.main()
