"""Unit tests for the cover the printer gets separately (no TeX, poppler or Pillow needed).

Run from the repository root: python3 -m unittest discover -s tools
"""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import print_cover
import print_output
from edition import BlockSettings, CoverSettings
from print_cover import check_cover, cover_tex, make_cover, prepare_pictures, preview_tex
from print_layout import A5, CROP_MARK_ROOM_MM
from print_output import PrintError

COVER = CoverSettings(design="editions/lite/cover/design.tex", paper=A5, colour="cmyk", crop_marks=True,
                      bleed_mm=3)
PICTURES = Path("build/editions/lite/print-cover/pictures")
COVER_PDFINFO = """Pages: 4
MediaBox: 0.00 0.00 504.57 680.31
BleedBox: 34.02 34.02 470.55 646.30
TrimBox: 42.52 42.52 462.05 637.80
"""


class Document(unittest.TestCase):
    def test_the_design_draws_the_four_pages_in_the_order_the_printer_gets_them(self):
        tex = cover_tex(COVER, PICTURES)
        pages = [line for line in tex.splitlines() if line.startswith("\\printcoverpage{")]
        self.assertEqual(pages, ["\\printcoverpage{\\zpcoverfront}", "\\printcoverpage{\\zpcoverinsidefront}",
                                 "\\printcoverpage{\\zpcoverinsideback}", "\\printcoverpage{\\zpcoverback}"])

    def test_the_front_and_the_back_are_required_the_insides_are_not(self):
        tex = cover_tex(COVER, PICTURES)
        for page in ("zpcoverfront", "zpcoverback"):
            self.assertIn(f"\\ifdefined\\{page}\\else\\errmessage", tex)
        self.assertNotIn("\\ifdefined\\zpcoverinsidefront\\else", tex)

    def test_the_converted_pictures_are_found_before_the_designs_own(self):
        tex = cover_tex(COVER, PICTURES)
        self.assertIn("\\graphicspath{{build/editions/lite/print-cover/pictures/}{editions/lite/cover/}}", tex)
        self.assertIn("\\input{editions/lite/cover/design}", tex)

    def test_the_design_gets_the_trimmed_page_and_the_bleed(self):
        tex = cover_tex(COVER, PICTURES)
        self.assertIn("\\setlength{\\zpcovertrimwidth}{148.000mm}", tex)
        self.assertIn("\\setlength{\\zpcovertrimheight}{210.000mm}", tex)
        self.assertIn("\\setlength{\\zpcoverbleed}{3.000mm}", tex)
        self.assertIn("{crop}", tex)

    def test_the_preview_cuts_every_page_to_its_trim_and_puts_the_block_inside_the_cover(self):
        block = BlockSettings(paper=A5)  # no room around its pages
        tex = preview_tex(Path("cover.pdf"), COVER, Path("block.pdf"), block)
        includes = [line for line in tex.splitlines() if line.startswith("\\includepdf")]
        room = f"{CROP_MARK_ROOM_MM:.3f}mm"
        self.assertEqual(includes, [
            f"\\includepdf[pages={{1-2}},trim={room} {room} {room} {room},clip]{{cover.pdf}}",
            "\\includepdf[pages={-},trim=0.000mm 0.000mm 0.000mm 0.000mm,clip]{block.pdf}",
            f"\\includepdf[pages={{3-4}},trim={room} {room} {room} {room},clip]{{cover.pdf}}"])
        self.assertNotIn("{crop}", tex)


class Pictures(unittest.TestCase):
    def prepare(self, cover: CoverSettings) -> tuple[Path, list[tuple[str, Path]]]:
        """Prepare the pictures of a design folder with a few files and an earlier build; the root
        and what was converted (source name, target)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "editions/lite/cover"
            folder.mkdir(parents=True)
            for name in ("design.tex", "front.jpg", "paper.JPEG", "lily.pdf", "logo.png"):
                (folder / name).write_text("", encoding="utf-8")
            (root / PICTURES).mkdir(parents=True)
            (root / PICTURES / "old.jpg").write_text("", encoding="utf-8")
            with (mock.patch.object(print_cover, "profile_file", return_value=Path("fogra.icc")),
                  mock.patch.object(print_cover, "convert_picture") as convert):
                prepare_pictures(root, cover, PICTURES)
            self.assertEqual(list((root / PICTURES).iterdir()), [])  # the converter is mocked
            return root, [(call.args[0].name, call.args[1]) for call in convert.call_args_list]

    def test_for_cmyk_the_jpegs_of_the_designs_folder_are_converted_by_name(self):
        root, converted = self.prepare(COVER)
        self.assertEqual(converted, [("front.jpg", root / PICTURES / "front.jpg"),
                                     ("paper.JPEG", root / PICTURES / "paper.JPEG")])

    def test_for_rgb_nothing_is_converted_and_nothing_of_an_earlier_build_stays(self):
        _, converted = self.prepare(CoverSettings(design=COVER.design, paper=A5))
        self.assertEqual(converted, [])


class Check(unittest.TestCase):
    def check(self, info: str = COVER_PDFINFO, images: tuple[tuple[int, str], ...] = ((1, "cmyk"),),
              cover: CoverSettings = COVER) -> None:
        with (mock.patch.object(print_cover, "pdfinfo", return_value=info),
              mock.patch.object(print_output, "unembedded_fonts", return_value=[]),
              mock.patch.object(print_output, "image_colours", return_value=list(images))):
            check_cover(Path("cover.pdf"), cover)

    def test_a_cover_of_four_pages_in_cmyk_passes(self):
        self.check()

    def test_a_cover_is_four_pages(self):
        with self.assertRaisesRegex(PrintError, "has 2 pages, not the 4 of a cover"):
            self.check(info=COVER_PDFINFO.replace("Pages: 4", "Pages: 2"))

    def test_an_rgb_picture_is_refused_in_cmyk_only(self):
        with self.assertRaisesRegex(PrintError, "pages 4 of .* images in RGB"):
            self.check(images=((4, "rgb"),))
        rgb_cover = CoverSettings(design=COVER.design, paper=A5, crop_marks=True, bleed_mm=3)
        self.check(images=((4, "rgb"),), cover=rgb_cover)

    def test_the_boxes_are_checked(self):
        with self.assertRaisesRegex(PrintError, "the bleed box"):
            self.check(info=COVER_PDFINFO.replace("34.02 34.02 470.55 646.30", "42.52 42.52 462.05 637.80"))


class Editions(unittest.TestCase):
    def test_an_edition_without_a_cover_table_has_nothing_to_make(self):
        settings = mock.Mock(cover=None)
        with mock.patch.object(print_cover, "read_print_settings", return_value=settings):
            self.assertIsNone(make_cover(Path("."), "lite"))
