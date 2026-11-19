"""Draw the front page for news-image-20261118 v8 (1024x1024 PNG).

v8 answers Ilham's order directly: all 40 verified stories, every
one readable at the judge's 300px view. The price is the pictures:
40 illustrated cards cannot fit in 1024px with readable text, so
v8 is 40 compact title+body cards (240x70 each, 4x10 grid) with no
illustrations, no map, no list. One line of Bebas Neue 26pt title
and one line of Work Sans 13pt SemiBold body per story. The
masthead, region bar, 6-number strip and DATE CHECK + sources
footer stay. The CLAIM story marks itself in its body line
("CLAIM: Manila disagrees.", amber).

This trades criterion 5 (craft: no illustrations, unlike every top
entry) and storytelling depth (one line per story) for criteria 2
(breadth: all 40) and 3 (readability: all 40). v7 (16 illustrated
cards) stays in git as the fallback if this trade looks wrong.

Rebuild after Ilham called v2 "jelek banget". Python 3.13, standard
library + Pillow + numpy, no network, deterministic. Text sizes are
fixed and never shrink: if a title or body does not fit at its set
size, the program stops so the wording can be shortened instead.

Layout (1024 units): masthead 10-109, region bar 111-137, numbers
139-179, cards 187-977 (4x10 grid, 240x70 each), date check
990-1005, footer 1008.
"""

import glob
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
SCALE = int(os.environ.get("MAKEFUN_SCALE", "1"))

W, H = 1024, 1024
OUT = HERE / ("entry-2048.png" if SCALE == 2 else "entry.png")

PAPER = (247, 243, 232)
CARD = (255, 253, 246)
INK = (17, 17, 17)
NAVY = (20, 38, 76)
RED = (193, 39, 45)
GREY = (90, 84, 72)
SEA = (207, 227, 238)
GREEN = (0, 110, 60)
AMBER = (140, 90, 0)
CHIP = (20, 38, 76)

REGION_COLORS = {
    "EUROPE": (43, 94, 167),
    "MIDDLE EAST": (176, 58, 46),
    "ASIA": (122, 79, 163),
    "AFRICA": (208, 122, 31),
    "AMERICAS": (46, 125, 79),
    "OCEANIA": (42, 157, 143),
    "WORLD": (107, 114, 128),
}
REGIONS = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS",
           "OCEANIA", "WORLD"]

FONTS = HERE / "fonts"
# Three families only (v6 typography brief): Bebas Neue for the
# masthead and big titles, Montserrat Bold for medium titles and
# the numbers strip, Work Sans for bodies, list and labels
# (600 = SemiBold, used wherever the old design used a bold sans).
BEBAS = str(FONTS / "BebasNeue-Regular.ttf")
MONTS = str(FONTS / "Montserrat-Bold.ttf")
WORK = str(FONTS / "WorkSans-400.woff")
WORK_B = str(FONTS / "WorkSans-600.woff")

BIG_TITLE = 30
TITLE = 19
BIG_BODY = 13
BODY = 13
LIST = 11

_cache = {}


def font(path, size):
    key = (path, int(round(size * SCALE)))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, key[1])
    return _cache[key]


def sc(v):
    return int(round(v * SCALE))


class Draw:
    """Draw in 1024 units on an image that may be SCALE times bigger."""

    def __init__(self, raw):
        self.d = raw

    def _p(self, xy):
        return [v * SCALE for v in xy]

    def _pts(self, pts):
        return [(x * SCALE, y * SCALE) for x, y in pts]

    def text(self, xy, s, f, fill):
        self.d.text((xy[0] * SCALE, xy[1] * SCALE), s, font=f, fill=fill)

    def length(self, s, f):
        return self.d.textlength(s, font=f) / SCALE

    def bbox(self, xy, s, f):
        box = self.d.textbbox((xy[0] * SCALE, xy[1] * SCALE), s, font=f)
        return tuple(v / SCALE for v in box)

    def line(self, xy, fill, width=1):
        self.d.line(self._p(xy), fill=fill, width=max(1, width * SCALE))

    def rect(self, xy, fill=None, outline=None, width=1):
        self.d.rectangle(self._p(xy), fill=fill, outline=outline,
                         width=max(1, width * SCALE))

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon(self._pts(pts), fill=fill, outline=outline)

    def ell(self, xy, fill=None, outline=None, width=1):
        self.d.ellipse(self._p(xy), fill=fill, outline=outline,
                       width=max(1, width * SCALE))


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.length(trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, text, path, size, max_w, max_lines, label):
    """Wrap at a fixed size; stop if it needs more lines than allowed."""
    f = font(path, size)
    lines = wrap(d, text, f, max_w)
    if len(lines) > max_lines:
        sys.exit(f"{label}: needs {len(lines)} lines, max {max_lines}: "
                 f"{text!r}")
    return f, lines, int(size * 1.17)


BOXES = []
FIT_OK = []


def put(d, x, y, text, f, fill, group, label=""):
    d.text((x, y), text, f, fill)
    BOXES.append((group, label, d.bbox((x, y), text, f)))


def put_c(d, cx, y, text, f, fill, group, label=""):
    w = d.length(text, f)
    d.text((cx - w / 2, y), text, f, fill)
    BOXES.append((group, label, d.bbox((cx - w / 2, y), text, f)))

# ------------------------------------------------------------------
# Stories: 13 cards, then 27 list items. Titles and summaries are
# short on purpose so they fit at the fixed sizes above.
# ------------------------------------------------------------------

STORIES = [
    # v8: all 40 verified stories as compact title+body cards, no
    # illustrations. Titles are shortened to one line of Bebas 26pt,
    # bodies to one line of Work Sans 13pt SemiBold, so every story
    # is readable at the judge's 300px view. The wording is plain
    # (v6/v7 language); the facts are the same as sources.json, and
    # the titles are shortened forms of the verified headlines, not
    # new claims. The ill keys are kept for the record only: v8
    # shows no pictures.
    {"id": 1, "region": "ASIA", "title": "Xi greets Trump",
     "summary": "Summit with Putin tomorrow.",
     "status": "CONFIRMED", "ill": "01-tarmac", "source": "Reuters"},
    {"id": 2, "region": "MIDDLE EAST", "title": "Iran attacks Kuwait",
     "summary": "Bahrain hit too.",
     "status": "CONFIRMED", "ill": "02-gulf", "source": "Reuters"},
    {"id": 35, "region": "WORLD", "title": "Voyager 1 passes",
     "summary": "One light-day from Earth.",
     "status": "CONFIRMED", "ill": "03-voyager", "source": "NASA"},
    {"id": 4, "region": "EUROPE", "title": "Russian strikes kill",
     "summary": "4 dead in Odesa.", "status": "none",
     "ill": "04-odesa", "source": "Reuters"},
    {"id": 5, "region": "MIDDLE EAST", "title": "Israeli tanks cross",
     "summary": "Rare move, 3 dead.", "status": "none",
     "ill": "05-gaza", "source": "BBC"},
    {"id": 6, "region": "AMERICAS", "title": "Peltola wins Alaska",
     "summary": "Democrats lead 56-44.", "status": "none",
     "ill": "06-peltola", "source": "AP"},
    {"id": 7, "region": "AMERICAS", "title": "US measles-free ends",
     "summary": "26 years clear. Now over.", "status": "none",
     "ill": "07-measles", "source": "PAHO"},
    {"id": 8, "region": "WORLD", "title": "Nvidia sales hit",
     "summary": "$115.8bn, shares fall.", "status": "none",
     "ill": "08-nvidia", "source": "CNBC"},
    {"id": 9, "region": "WORLD", "title": "Anthropic debuts",
     "summary": "First sale at $83.", "status": "none",
     "ill": "09-anthropic-wide", "source": "Reuters"},
    {"id": 10, "region": "EUROPE", "title": "EU plans \u20ac45bn loan",
     "summary": "Only frozen Russian cash.", "status": "none",
     "ill": "10-euloan-wide", "source": "Reuters"},
    {"id": 13, "region": "ASIA", "title": "Trump praises deal",
     "summary": "Manila disagrees.", "status": "CLAIM",
     "ill": "13-manila", "source": "Reuters"},
    {"id": 12, "region": "EUROPE", "title": "UniCredit buys bank",
     "summary": "Commerzbank deal done.", "status": "none",
     "ill": "12-unicredit", "source": "Reuters"},
    {"id": 11, "region": "EUROPE", "title": "Imamoglu jailed again",
     "summary": "Two more years, new ban.", "status": "none",
     "ill": "11-imamoglu", "source": "Reuters"},
    {"id": 15, "region": "AFRICA", "title": "Uganda activist held",
     "summary": "Charged with treachery.", "status": "none",
     "ill": "15-uganda", "source": "Reuters"},
    {"id": 33, "region": "OCEANIA", "title": "Fiji drought disaster",
     "summary": "El Nino blamed.", "status": "none",
     "ill": "33-fiji", "source": "RNZ"},
    {"id": 34, "region": "AFRICA", "title": "Ebola hits children",
     "summary": "Three in four under-5s die.", "status": "none",
     "ill": "34-ebola", "source": "Horizon"},
    {"id": 37, "region": "OCEANIA", "title": "Quake hits Papua",
     "summary": "Magnitude 6.0, 10 km deep.", "status": "none",
     "ill": "37-pngquake", "source": "Reuters"},
    {"id": 3, "region": "EUROPE", "title": "Crimea bridge falls",
     "summary": "Span falls to the sea.", "status": "none",
     "ill": "", "source": "Reuters"},
    {"id": 14, "region": "ASIA", "title": "Three leaders meet",
     "summary": "Gather in China.", "status": "none",
     "ill": "", "source": "BBC"},
    {"id": 16, "region": "MIDDLE EAST", "title": "Bahrain stops Iran",
     "summary": "Attacks blocked again.", "status": "none",
     "ill": "", "source": "Reuters"},
    {"id": 17, "region": "MIDDLE EAST", "title": "Gaza baby dies",
     "summary": "Dies of cold in floods.", "status": "none",
     "ill": "", "source": "WHO"},
    {"id": 18, "region": "MIDDLE EAST", "title": "Israel spy chief",
     "summary": "Pushed Iran strikes.", "status": "none",
     "ill": "", "source": "Reuters"},
    {"id": 19, "region": "EUROPE", "title": "UK inflation rises",
     "summary": "3.6% in October.", "status": "none",
     "ill": "", "source": "Reuters"},
    {"id": 20, "region": "EUROPE", "title": "Fed keeps rates high",
     "summary": "Interest rates stay high.", "status": "none",
     "ill": "", "source": "Reuters"},
    {"id": 21, "region": "AMERICAS", "title": "Waymo halts rides",
     "summary": "No driver on freeways.", "status": "none",
     "ill": "", "source": "TechCrunch"},
    {"id": 22, "region": "AMERICAS", "title": "Mullin faces hearing",
     "summary": "Congress grills on outages.", "status": "none",
     "ill": "", "source": "AP"},
    {"id": 23, "region": "ASIA", "title": "EU approves trade",
     "summary": "Indonesia signing ok.", "status": "none",
     "ill": "", "source": "EU"},
    {"id": 24, "region": "AFRICA", "title": "Border troops mass",
     "summary": "Ethiopia, Eritrea face off.", "status": "none",
     "ill": "", "source": "Reuters"},
    {"id": 25, "region": "EUROPE", "title": "Quake near Comandau",
     "summary": "Magnitude 5.3.", "status": "none",
     "ill": "", "source": "USGS"},
    {"id": 26, "region": "AMERICAS", "title": "Rain floods Florida",
     "summary": "South Florida swamped.", "status": "none",
     "ill": "", "source": "BBC"},
    {"id": 27, "region": "EUROPE", "title": "Como win 9-1",
     "summary": "Douvikas scores 3.", "status": "none",
     "ill": "", "source": "A Sports"},
    {"id": 28, "region": "EUROPE", "title": "Chelsea 1-0 PSG",
     "summary": "Man City 2-0 Hacken.", "status": "none",
     "ill": "", "source": "PSG"},
    {"id": 29, "region": "ASIA", "title": "Royals meet Modi",
     "summary": "William and Kate in India.", "status": "none",
     "ill": "", "source": "BBC"},
    {"id": 30, "region": "ASIA", "title": "Cyclone nears India",
     "summary": "Akvan nears coast.", "status": "none",
     "ill": "", "source": "Hindu"},
    {"id": 31, "region": "WORLD", "title": "Word of 2026: human",
     "summary": "Cambridge picks human.", "status": "none",
     "ill": "", "source": "Anadolu"},
    {"id": 32, "region": "EUROPE", "title": "Worst wildfire season",
     "summary": "Europe faces worst yet.", "status": "none",
     "ill": "", "source": "EU"},
    {"id": 36, "region": "AMERICAS", "title": "Floods hit Ecuador",
     "summary": "Rains flood Quito.", "status": "none",
     "ill": "", "source": "ECHO"},
    {"id": 38, "region": "AMERICAS", "title": "Jeffries for Speaker",
     "summary": "Chosen 251-11.", "status": "none",
     "ill": "", "source": "AP"},
    {"id": 39, "region": "WORLD", "title": "Nuclear deal backed",
     "summary": "Agency chief backs US-Saudi.", "status": "none",
     "ill": "", "source": "Reuters"},
    {"id": 40, "region": "MIDDLE EAST", "title": "Hospital chief held",
     "summary": "Held 6 more months.", "status": "none",
     "ill": "", "source": "Reuters"},
]

# NOTE: id 3 (Crimea bridge) is a card in v8: the strike was 17 Nov
# but the collapse was confirmed 18 Nov, and the DATE CHECK box
# still says the strike was 17 Nov.
CARDS = STORIES
ALSO = []
assert len(CARDS) == 40 and len(ALSO) == 0

NUMBERS = [
    ("$115.8bn", "Nvidia sales", GREEN),
    ("$83", "Anthropic first sale", INK),
    ("56-44", "Democrats lead Senate", INK),
    ("5,400+", "US measles cases", INK),
    ("9-1", "Como win at Lens", INK),
    ("6.0", "Papua New Guinea quake", INK),
]

DATECHECK_TEXT = ("DATE CHECK - Not from 18 Nov: Kerch span struck 17 Nov "
                  "(collapse confirmed 18 Nov) - Israel parliament speaker "
                  "Kahana (17 Nov) - Yemen's Houthi group drones at Riyadh "
                  "(17 Nov).")
FOOTER_TEXT = ("Claims labelled CLAIM. Sources: Reuters, AP, NASA, BBC, "
               "CNBC, PAHO, WHO, EU, USGS, ECHO, TechCrunch, A Sports, "
               "PSG, Hindu, Anadolu, RNZ, Horizon. Pictures generated for "
               "this page.")


def check_stories():
    # v8: the page shows all 40 verified stories, but the titles are
    # shortened to one line, so they no longer equal the headlines in
    # sources.json. The check verifies each story id exists there
    # with the same source and an 18 Nov date; the facts behind the
    # shortened titles are the verified headlines and notes.
    if len(STORIES) != 40:
        sys.exit(f"expected 40 stories, got {len(STORIES)}")
    ids = [s["id"] for s in STORIES]
    if sorted(ids) != list(range(1, 41)):
        sys.exit("story ids must be 1..40")
    for field in ("title",):
        seen = {}
        for s in STORIES:
            key = s[field].strip().lower()
            if key in seen:
                sys.exit(f"duplicate {field}: {s[field]!r}")
            seen[key] = s["id"]
    for s in STORIES:
        if s["region"] not in REGIONS:
            sys.exit(f"story {s['id']}: bad region {s['region']!r}")
        if s.get("status", "none") not in ("CONFIRMED", "CLAIM", "none"):
            sys.exit(f"story {s['id']}: bad status")
    with open(HERE / "sources.json", encoding="utf-8") as f:
        srcs = json.load(f)
    by_id = {e["id"]: e for e in srcs}
    if sorted(by_id) != list(range(1, 41)):
        sys.exit("sources.json ids must be 1..40")
    for s in STORIES:
        e = by_id[s["id"]]
        if e["source_name"] != s["source"]:
            sys.exit(f"sources.json id {s['id']}: source mismatch")
        if not str(e["published_utc"]).startswith("2026-11-18"):
            sys.exit(f"sources.json id {s['id']}: not dated 18 Nov")


def region_counts():
    counts = {r: 0 for r in REGIONS}
    for s in STORIES:
        counts[s["region"]] += 1
    return counts


# ------------------------------------------------------------------
# Illustrations: AI-generated woodcut images, one per card, made in
# this session. Cover-cropped to the card slot.
# ------------------------------------------------------------------

def illustration_path(key):
    cands = sorted((HERE / "illustrations").glob(
        f"media-generation-ill-{key}-*.webp"))
    if not cands:
        sys.exit(f"missing illustration for card {key}")
    return cands[0]


def illustration(key, w, h):
    src = Image.open(illustration_path(key)).convert("RGB")
    return ImageOps.fit(src, (sc(w), sc(h)), Image.LANCZOS,
                        centering=(0.5, 0.5))


# ------------------------------------------------------------------
# Cards
# ------------------------------------------------------------------

CARD_BOUNDS = []
HEIGHT_LOG = []


def card_frame(d, x, y, w, h, region, pad=12):
    d.rect([x, y, x + w, y + h], fill=CARD, outline=INK, width=2)
    d.rect([x, y, x + w, y + 5], fill=REGION_COLORS[region])
    return x + pad, y + pad, w - 2 * pad, h - 2 * pad


def draw_compact(img, d, x, y, w, h, story):
    # v8 compact card: 240x70, inner 220x50 (10px frame). One line of
    # Bebas 26pt title, one line of Work Sans 13pt SemiBold body.
    # No illustration, no category line, no source chip: there is no
    # room for any of them at 40 stories. The CLAIM story marks
    # itself in its body line, in amber, so the footer's "Claims
    # labelled CLAIM" stays true.
    num = CARDS.index(story) + 1
    group = f"card{num}"
    ix, iy, iw, ih = card_frame(d, x, y, w, h, story["region"], pad=10)
    CARD_BOUNDS.append((group, ix, iy, ix + iw, iy + ih))
    f, lines, lh = block(d, story["title"], BEBAS, 26, iw, 1,
                         f"compact title {num}")
    for ln in lines:
        put(d, ix, iy, ln, f, INK, group, label="title")
    sy = iy + lh + 2
    body = story["summary"]
    bcol = INK
    if story["status"] == "CLAIM":
        body = "CLAIM: " + body
        bcol = AMBER
    f2, lines2, lh2 = block(d, body, WORK_B, BIG_BODY, iw, 1,
                            f"compact sub {num}")
    for ln in lines2:
        put(d, ix, sy, ln, f2, bcol, group, label="sub")
    used = lh + 2 + len(lines2) * lh2
    HEIGHT_LOG.append((f"compact card {num}", used, ih))

def check_layout():
    problems = []
    for label, got, need in HEIGHT_LOG:
        if got > need:
            problems.append(f"{label}: content {got}px over frame {need}px")
    bounds = {g: (x0, y0, x1, y1) for g, x0, y0, x1, y1 in CARD_BOUNDS}
    by_group = {}
    for group, label, box in BOXES:
        by_group.setdefault(group, []).append((label, box))
        x0, y0, x1, y1 = box
        if x0 < 10 or y0 < 10 or x1 > 1014 or y1 > 1022:
            problems.append(f"{group} {label}: box leaves the page")
        if group in bounds:
            bx0, by0, bx1, by1 = bounds[group]
            if (x0 < bx0 - 2 or x1 > bx1 + 2 or y0 < by0 - 2
                    or y1 > by1 + 2):
                problems.append(f"{group} {label}: box leaves its card")
    for group, items in by_group.items():
        for i, (l1, b1) in enumerate(items):
            for l2, b2 in items[i + 1:]:
                ox = min(b1[2], b2[2]) - max(b1[0], b2[0])
                oy = min(b1[3], b2[3]) - max(b1[1], b2[1])
                if ox > 1 and oy > 1:
                    problems.append(f"{group}: {l1} overlaps {l2}")
    if problems:
        sys.exit("LAYOUT CHECK FAILED:\n" + "\n".join(problems))
    print(f"layout check passed: {len(BOXES)} boxes, "
          f"{len(CARDS)} cards")

def check_card_text():
    """Measure every compact title and body against its card width.

    A compact card holds one line of Bebas 26pt title and one line of
    Work Sans 13pt SemiBold body in 220px. This fails loudly when a
    title or a body would wrap, so the wording gets shortened before
    the page is drawn instead of after. It runs before any drawing,
    and it reads only STORIES and the fonts.
    """
    probe = Image.new("RGB", (8, 8))
    pd = Draw(ImageDraw.Draw(probe))
    title_font = font(BEBAS, 26)
    body_font = font(WORK_B, 13)
    inner = 220
    worst_title = ("", 0.0)
    worst_body = ("", 0.0)
    for s in STORIES:
        title = s["title"]
        body = s["summary"]
        if s["status"] == "CLAIM":
            body = "CLAIM: " + body
        tw = pd.length(title, title_font)
        bw = pd.length(body, body_font)
        if tw > worst_title[1]:
            worst_title = (title, tw)
        if bw > worst_body[1]:
            worst_body = (body, bw)
        if tw > inner:
            sys.exit(f"compact title too wide ({tw:.1f}px): {title!r}")
        if bw > inner:
            sys.exit(f"compact body too wide ({bw:.1f}px): {body!r}")
    print(f"card text fits: longest title {worst_title[1]:.1f}px "
          f"({worst_title[0]!r}), longest body {worst_body[1]:.1f}px "
          f"({worst_body[0]!r})")


def coverage_report():
    """Print a plain-language summary of the page for the builder.

    Counts the stories and the regions, names the longest title and
    body in pixels, and lists the CLAIM and CONFIRMED stories, so the
    builder can see at a glance whether the page covers the day and
    whether anything is close to overflowing its card. It reads only
    STORIES and the fonts; it never touches the image.
    """
    regions = {}
    for s in STORIES:
        regions[s["region"]] = regions.get(s["region"], 0) + 1
    print(f"stories: {len(STORIES)}")
    for region in REGIONS:
        n = regions.get(region, 0)
        if n:
            print(f"  {region}: {n}")
    print(f"cards: {len(CARDS)} compact, {len(ALSO)} also")
    probe = Image.new("RGB", (8, 8))
    pd = Draw(ImageDraw.Draw(probe))
    longest_title = max(STORIES,
                        key=lambda s: pd.length(s["title"], font(BEBAS, 26)))
    longest_body = max(STORIES,
                       key=lambda s: pd.length(s["summary"], font(WORK_B, 13)))
    tw = pd.length(longest_title["title"], font(BEBAS, 26))
    bw = pd.length(longest_body["summary"], font(WORK_B, 13))
    print(f"longest title: {tw:.1f}px ({longest_title['title']!r})")
    print(f"longest body: {bw:.1f}px ({longest_body['summary']!r})")
    print(f"claim stories: {[s['id'] for s in STORIES if s['status'] == 'CLAIM']}")
    print(f"confirmed stories: {[s['id'] for s in STORIES if s['status'] == 'CONFIRMED']}")


def judge_preview(path):
    """Write a 300px downscale of the finished page beside it.

    The judge reads the page at about 300 pixels across, so the
    builder checks that view before calling the page done. This
    writes <name>-300.png next to the given file and prints the path;
    it never changes the page itself.
    """
    im = Image.open(path)
    small = im.resize((300, 300), Image.LANCZOS)
    out = Path(path).with_name(Path(path).stem + "-300.png")
    small.save(out)
    print(f"judge view (300px): {out}")
    return out


def main():
    check_stories()
    check_card_text()
    counts = region_counts()
    n_regions = sum(1 for r in REGIONS if counts[r] > 0)
    kicker = (f"WEDNESDAY 18 NOVEMBER 2026 - {len(STORIES)} STORIES - "
              f"{n_regions} REGIONS")

    img = Image.new("RGB", (sc(W), sc(H)), PAPER)
    d = Draw(ImageDraw.Draw(img))
    d.rect([10, 10, W - 11, 1022], outline=INK, width=4)

    # Masthead: navy poster band with the big date number.
    d.rect([10, 10, 1014, 109], fill=NAVY)
    put(d, 24, 12, "18", font(BEBAS, 84), (255, 255, 255), "header",
        label="date-num")
    put_c(d, 590, 16, "THE WORLD IN ONE PAGE", font(BEBAS, 64),
          (255, 255, 255), "header", label="title")
    put_c(d, 590, 76, kicker, font(WORK_B, 13), (255, 255, 255),
          "header", label="kicker")

    # Region bar.
    seg_font = font(WORK_B, 13)
    segs = [(f"{r} {counts[r]}", REGION_COLORS[r]) for r in REGIONS]
    sep_w = d.length(" - ", seg_font)
    total = sum(d.length(t, seg_font) for t, _ in segs)
    total += sep_w * (len(segs) - 1)
    sx = (W - total) / 2
    for i, (text, col) in enumerate(segs):
        put(d, sx, 115, text, seg_font, col, "header", label="region-bar")
        sx += d.length(text, seg_font)
        if i < len(segs) - 1:
            put(d, sx, 115, " - ", seg_font, GREY, "header", label="sep")
            sx += sep_w

    # Big-numbers strip (40px band, 8px of air above the cards).
    cell_w = (1008 - 16) / 6
    for i, (num, label, col) in enumerate(NUMBERS):
        cx = 16 + i * cell_w
        put_c(d, cx + cell_w / 2, 140, num, font(MONTS, 26), col,
              "numbers", label="num")
        put_c(d, cx + cell_w / 2, 168, label, font(WORK, 13), GREY,
              "numbers", label="num-label")
        if i:
            d.line([(cx, 141), (cx, 178)], fill=GREY, width=1)

    # Cards: 40 compact cards in a 4x10 grid, 240x70 each, one 10px
    # gutter. No illustrations in v8: 40 illustrated cards cannot
    # fit in 1024px with readable text, so the pictures were traded
    # for the full 40 stories.
    card_x = [16, 266, 516, 768]
    for r in range(10):
        for c in range(4):
            draw_compact(img, d, card_x[c], 187 + r * 80, 240, 70,
                         CARDS[r * 4 + c])

    # DATE CHECK box.
    d.rect([16, 990, 1008, 1005], outline=INK, width=2)
    d.rect([16, 990, 22, 1005], fill=RED)
    put(d, 30, 993, DATECHECK_TEXT, font(WORK, 9), INK, "footer",
        label="datecheck")

    put_c(d, W // 2, 1008, FOOTER_TEXT, font(WORK, 9), GREY, "footer",
          label="footer")

    check_layout()
    img.save(OUT, optimize=True)
    print("saved", OUT)
    if "--report" in sys.argv:
        coverage_report()
    if "--judge-view" in sys.argv:
        judge_preview(str(OUT))


if __name__ == "__main__":
    main()
