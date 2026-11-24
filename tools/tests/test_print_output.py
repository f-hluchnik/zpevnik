"""Unit tests for what every PDF for the printer shares: its page boxes and its delivery.

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import print_output
from edition import CoverSettings, PageSettings
from print_layout import A5, CROP_MARK_ROOM_MM, PAPERS, points
from print_output import clear_delivery, deliver, delivered_path, document_start, page_boxes_tex

A5_PAPER = PAPERS[A5]
ROOM = points(CROP_MARK_ROOM_MM)


class PageBoxes(unittest.TestCase):
    def test_without_crop_marks_and_bleed_the_pdf_page_is_the_trimmed_page(self):
        self.assertEqual(page_boxes_tex(PageSettings(paper=A5)), "")

    def test_crop_marks_add_room_and_the_page_names_its_trim_and_bleed(self):
        tex = page_boxes_tex(PageSettings(paper=A5, crop_marks=True, bleed_mm=3))
        self.assertIn("\\usepackage[cam,noinfo,center,pdftex,width=178.000mm,height=240.000mm]{crop}", tex)
        bleed = points(3)
        trim = f"[{ROOM:.3f} {ROOM:.3f} {ROOM + A5_PAPER.width:.3f} {ROOM + A5_PAPER.height:.3f}]"
        bleed_box = (f"[{ROOM - bleed:.3f} {ROOM - bleed:.3f} {ROOM + A5_PAPER.width + bleed:.3f} "
                     f"{ROOM + A5_PAPER.height + bleed:.3f}]")
        self.assertIn(f"/TrimBox {trim} /BleedBox {bleed_box}", tex)

    def test_a_bleed_without_crop_marks_is_the_room_around_the_page(self):
        tex = page_boxes_tex(PageSettings(paper=A5, bleed_mm=3))
        self.assertIn("\\usepackage[off,noinfo,center,pdftex,width=154.000mm,height=216.000mm]{crop}", tex)
        self.assertIn(f"/BleedBox [0.000 0.000 {A5_PAPER.width + 2 * points(3):.3f}", tex)

    def test_a_document_has_its_paper_then_its_page_then_the_packages(self):
        tex = document_start(CoverSettings(design="d.tex", paper=A5, crop_marks=True), ("tikz", "xcolor"))
        self.assertTrue(tex.startswith("\\documentclass[a5paper]{article}\n\\usepackage[cam,"))
        self.assertTrue(tex.endswith("\\usepackage{tikz}\n\\usepackage{xcolor}\n"))


class Delivery(unittest.TestCase):
    def test_the_file_for_the_printer_names_the_edition_the_version_and_the_part(self):
        self.assertEqual(delivered_path("lite", "8.49.3", "blok"),
                         Path("build/print/lite/zpevnik-lite-8.49.3-blok.pdf"))

    def test_a_make_print_replaces_every_earlier_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "build/print/lite"
            folder.mkdir(parents=True)
            for name in ("zpevnik-lite-8.48.1-blok.pdf", "zpevnik-lite-8.48.1-obalka.pdf"):
                (folder / name).write_text("old", encoding="utf-8")
            (root / "made.pdf").write_text("new", encoding="utf-8")
            clear_delivery(root, "lite")
            with mock.patch.object(print_output, "current_version", return_value="8.49.?"):
                target = deliver(root, Path("made.pdf"), "lite", "blok")
            self.assertEqual(target, Path("build/print/lite/zpevnik-lite-8.49.x-blok.pdf"))
            self.assertEqual([path.name for path in folder.iterdir()], ["zpevnik-lite-8.49.x-blok.pdf"])
            self.assertEqual((root / target).read_text(encoding="utf-8"), "new")

    def test_clearing_a_folder_that_does_not_exist_yet_does_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            clear_delivery(Path(tmp), "lite")
