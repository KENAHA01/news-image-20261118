"""Draw the front page for news-image-20261118 (1024x1024 PNG).

Written fresh in this session for Wednesday 18 November 2026. One
newspaper page: a serif date banner, a BY THE NUMBERS strip, a WHY
line, 15 illustrated cards (3 big, 12 small), a world map with pins,
a numbered list of 19 more stories, a DATE CHECK strip and a footer.
Every card scene is drawn here in code with Pillow and numpy: a sky
gradient, a ground or sea band, and one simple motif per story. No
photo, no downloaded asset, no face, no image model. Text sizes are
fixed and never shrink: if a title or body does not fit at its set
size, the program stops so the wording can be shortened instead.

Layout (1024 units): header 14-65, numbers 81-108, why 108, big row
122-286, thread 294, row 2 307-453, row 3 456-614, map and list
619-967, date check 970-986, footer 990-999.
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SCALE = int(os.environ.get("MAKEFUN_SCALE", "1"))

W, H = 1024, 1024
OUT = HERE / ("entry-2048.png" if SCALE == 2 else "entry.png")

PAPER = (247, 243, 232)
CARD = (255, 253, 246)
INK = (26, 26, 26)
RED = (139, 30, 30)
GREY = (90, 84, 72)
SEA = (207, 227, 238)
LAND = (232, 223, 200)
GREEN = (0, 110, 60)
AMBER = (140, 90, 0)

REGION_COLORS = {
    "EUROPE": (0, 90, 180),
    "MIDDLE EAST": (178, 34, 34),
    "ASIA": (200, 100, 0),
    "AFRICA": (0, 110, 60),
    "AMERICAS": (110, 60, 160),
    "OCEANIA": (0, 130, 130),
    "WORLD": (90, 84, 72),
}
REGIONS = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS",
           "OCEANIA", "WORLD"]

FONTS = HERE / "fonts"
SERIF = str(FONTS / "DejaVuSerif.ttf")
SERIF_B = str(FONTS / "DejaVuSerif-Bold.ttf")
SANS = str(FONTS / "DejaVuSans.ttf")
SANS_B = str(FONTS / "DejaVuSans-Bold.ttf")

BIG_TITLE = 17
TITLE = 12
BODY = 10
LIST = 10

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
# Stories: 15 cards, then 19 list items. Titles and summaries are
# short on purpose so they fit at the fixed sizes above.
# ------------------------------------------------------------------

STORIES = [
    {"id": 1, "region": "ASIA", "title": "Xi and Putin meet in Shenzhen",
     "summary": "A day before Trump joins them for a first three-way summit.",
     "status": "CONFIRMED", "cat": "ASIA - DIPLOMACY", "scene": "summit",
     "source": "Reuters", "caption": "Shenzhen, where the three meet",
     "tag": "CONFIRMED: Reuters and The Hindu report the talks."},
    {"id": 2, "region": "MIDDLE EAST", "title": "Iran hits Kuwait and Bahrain",
     "summary": "Tehran answers the US strike on Qeshm Island in the Gulf.",
     "status": "CONFIRMED", "cat": "MIDDLE EAST - IRAN WAR",
     "scene": "gulf", "source": "Reuters",
     "caption": "The Gulf, between Iran and the Arab shore",
     "tag": "CONFIRMED: Reuters reports the overnight strikes."},
    {"id": 3, "region": "EUROPE", "title": "Crimea bridge span falls to the sea",
     "summary": "Struck on Tuesday; the road span collapse is confirmed today.",
     "status": "CONFIRMED", "cat": "EUROPE - UKRAINE WAR",
     "scene": "bridge", "source": "Reuters",
     "caption": "The strait that joins Crimea and Russia",
     "tag": "CONFIRMED: 18 Nov reports show the span down."},
    {"id": 4, "region": "EUROPE", "title": "Russian strikes kill five in Odesa",
     "summary": "Kyiv bridges hit too; UK pledges missiles.",
     "status": "none", "cat": "EUROPE - UKRAINE WAR", "scene": "city",
     "source": "Reuters"},
    {"id": 5, "region": "MIDDLE EAST", "title": "Israeli tanks cross Gaza line",
     "summary": "Rare ground move kills three, reports say.",
     "status": "none", "cat": "MIDDLE EAST - GAZA", "scene": "gaza",
     "source": "BBC"},
    {"id": 6, "region": "AMERICAS", "title": "Peltola wins Alaska Senate race",
     "summary": "Democrats take a 56-44 Senate majority.",
     "status": "none", "cat": "AMERICAS - POLITICS", "scene": "ballot",
     "source": "AP"},
    {"id": 7, "region": "AMERICAS", "title": "US loses measles status",
     "summary": "A year of spread ends 26 years clear.",
     "status": "none", "cat": "AMERICAS - HEALTH", "scene": "clinic",
     "source": "PAHO"},
    {"id": 8, "region": "WORLD", "title": "Nvidia sales hit $115.8bn",
     "summary": "Shares still fall 2.9% after the beat.",
     "status": "none", "cat": "WORLD - BUSINESS", "scene": "chart",
     "source": "CNBC"},
    {"id": 9, "region": "WORLD", "title": "Anthropic IPO priced at $83",
     "summary": "Above its $70-78 range; trading starts soon.",
     "status": "none", "cat": "WORLD - BUSINESS", "scene": "bell",
     "source": "Reuters"},
    {"id": 10, "region": "EUROPE", "title": "EU plans 45bn euro Ukraine loan",
     "summary": "For 2027, repaid only after reparations.",
     "status": "none", "cat": "EUROPE - UKRAINE WAR", "scene": "euloan",
     "source": "Reuters"},
    {"id": 11, "region": "EUROPE", "title": "Imamoglu gets two more years",
     "summary": "Jailed Istanbul mayor faces a new ban.",
     "status": "none", "cat": "EUROPE - POLITICS", "scene": "court",
     "source": "Reuters"},
    {"id": 12, "region": "EUROPE", "title": "UniCredit agrees Commerzbank deal",
     "summary": "German HQ stays in Frankfurt, Berlin says.",
     "status": "none", "cat": "EUROPE - BUSINESS", "scene": "bank",
     "source": "Reuters"},
    {"id": 13, "region": "ASIA", "title": "Trump hails Manila trade deal",
     "summary": "Manila calls it only an understanding.",
     "status": "CLAIM", "cat": "ASIA - TRADE", "scene": "trade",
     "source": "Reuters",
     "tag": "CLAIM: Trump says deal; Manila disagrees."},
    {"id": 14, "region": "ASIA", "title": "Three leaders meet in China",
     "summary": "Trump joins Xi and Putin on Thursday.",
     "status": "none", "cat": "ASIA - DIPLOMACY", "scene": "leaders",
     "source": "BBC"},
    {"id": 15, "region": "AFRICA", "title": "Uganda activist charged in court",
     "summary": "Mugumya faces treachery after a year missing.",
     "status": "none", "cat": "AFRICA - POLITICS", "scene": "gavel",
     "source": "Reuters"},
    {"id": 16, "region": "MIDDLE EAST",
     "title": "Bahrain stops Iran attacks again", "source": "Reuters"},
    {"id": 17, "region": "MIDDLE EAST",
     "title": "Gaza baby dies of cold in floods", "source": "WHO"},
    {"id": 18, "region": "MIDDLE EAST",
     "title": "Mossad chief pushed Iran strikes", "source": "Reuters"},
    {"id": 19, "region": "EUROPE",
     "title": "UK inflation rises to 3.6% in Oct", "source": "Reuters"},
    {"id": 20, "region": "EUROPE",
     "title": "Fed minutes stay hawkish on prices", "source": "Reuters"},
    {"id": 21, "region": "AMERICAS",
     "title": "Waymo halts driverless freeway rides", "source": "TechCrunch"},
    {"id": 22, "region": "AMERICAS",
     "title": "Mullin faces House hearing on outages", "source": "AP"},
    {"id": 23, "region": "ASIA",
     "title": "EU approves Indonesia trade signing", "source": "EU"},
    {"id": 24, "region": "AFRICA",
     "title": "Ethiopia, Eritrea mass border troops", "source": "Reuters"},
    {"id": 25, "region": "EUROPE",
     "title": "Romania quake M5.3 near Comandau", "source": "USGS"},
    {"id": 26, "region": "AMERICAS",
     "title": "Torrential rain floods South Florida", "source": "BBC"},
    {"id": 27, "region": "EUROPE",
     "title": "Como win 9-1 at Lens, Douvikas treble", "source": "A Sports"},
    {"id": 28, "region": "EUROPE",
     "title": "Chelsea 1-0 PSG; Man City 2-0 Hacken", "source": "PSG"},
    {"id": 29, "region": "ASIA",
     "title": "William and Kate meet Modi in India", "source": "BBC"},
    {"id": 30, "region": "ASIA",
     "title": "Cyclone Akvan nears India coast", "source": "Hindu"},
    {"id": 31, "region": "WORLD",
     "title": "Cambridge word of 2026 is human", "source": "Anadolu"},
    {"id": 32, "region": "EUROPE",
     "title": "Europe faces worst wildfire season", "source": "EU"},
    {"id": 33, "region": "OCEANIA",
     "title": "Fiji declares drought disaster", "source": "RNZ"},
    {"id": 34, "region": "AFRICA",
     "title": "Ebola in DR Congo hits children hardest", "source": "Horizon"},
]

CARDS = STORIES[:15]
ALSO = STORIES[15:]
ALSO_BY_REGION = [(r, [s for s in ALSO if s["region"] == r])
                  for r in REGIONS if any(s["region"] == r for s in ALSO)]

NUMBERS = [
    ("$115.8bn", "Nvidia quarter", GREEN, ""),
    ("$83", "Anthropic IPO price", INK, ""),
    ("56-44", "Democratic Senate", INK, ""),
    ("5,400+", "US measles cases", INK, ""),
    ("9-1", "Como win at Lens", INK, ""),
    ("-1.11%", "Dow on Wednesday", RED, "down"),
]

WHY_TEXT = ("Three leaders gather in China as Gulf fire spreads and "
            "a bridge falls.")
THREAD_TEXT = ("US struck Qeshm Tuesday; Iran hit Kuwait and Bahrain "
               "overnight; Xi and Putin met in Shenzhen.")
DATECHECK_TEXT = ("DATES CHECKED - not from 18 Nov: Knesset speaker "
                  "Kahana (17 Nov) - Houthi drones at Riyadh (17 Nov) - "
                  "Kerch span struck 17 Nov, collapse confirmed 18 Nov.")


def check_stories():
    if len(STORIES) != 34:
        sys.exit(f"expected 34 stories, got {len(STORIES)}")
    if [s["id"] for s in STORIES] != list(range(1, 35)):
        sys.exit("story ids must be 1..34 in order")
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
    if sorted(by_id) != list(range(1, 35)):
        sys.exit("sources.json ids must be 1..34")
    for s in STORIES:
        e = by_id[s["id"]]
        if e["headline"].strip().lower() != s["title"].strip().lower():
            sys.exit(f"sources.json id {s['id']}: headline mismatch")
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
# Scenes: one small picture per card, drawn with numpy gradients
# and Pillow shapes. Deterministic: no random numbers at all.
# ------------------------------------------------------------------

def sky(arr_top, arr_bot, w, h):
    """Vertical gradient as a float array, shape (h, w, 3)."""
    top = np.array(arr_top, dtype=float) / 255.0
    bot = np.array(arr_bot, dtype=float) / 255.0
    t = np.linspace(0.0, 1.0, h)[:, None, None]
    base = top[None, None, :] * (1 - t) + bot[None, None, :] * t
    return np.repeat(base, w, axis=1)


def scene_image(scene, w, h):
    """Render one card illustration, w by h pixels, in 1024 units."""
    pw, ph = sc(w), sc(h)
    if scene == "gulf":
        arr = sky((70, 110, 150), (180, 210, 225), pw, ph)
    elif scene in ("bridge", "city", "gaza"):
        arr = sky((200, 170, 120), (235, 220, 190), pw, ph)
    elif scene in ("ballot", "clinic", "chart", "bell", "court", "bank",
                   "gavel", "euloan", "trade"):
        arr = sky((235, 232, 220), (250, 248, 240), pw, ph)
    else:
        arr = sky((90, 140, 190), (200, 225, 240), pw, ph)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    s = pw / max(1, w)  # device pixels per layout unit

    def X(v):
        return v * s

    def Y(v):
        return v * s

    def rect(x0, y0, x1, y1, fill):
        d.rectangle([X(x0), Y(y0), X(x1), Y(y1)], fill=fill)

    def ell(x0, y0, x1, y1, fill):
        d.ellipse([X(x0), Y(y0), X(x1), Y(y1)], fill=fill)

    def poly(pts, fill):
        d.polygon([(X(x), Y(y)) for x, y in pts], fill=fill)

    def line(pts, fill, width=2):
        d.line([(X(x), Y(y)) for x, y in pts], fill=fill,
               width=max(1, int(width * s)))

    mid = h * 0.62
    if scene in ("summit", "leaders"):
        rect(0, mid, w, h, (90, 140, 80))
        cols = [(200, 40, 40), (40, 80, 180), (220, 220, 220)] \
            if scene == "summit" else \
            [(200, 40, 40), (220, 220, 220), (40, 80, 180)]
        for i, col in enumerate(cols):
            fx = w * (0.22 + 0.28 * i)
            line([(fx, 4), (fx, mid)], (60, 60, 60), 2)
            poly([(fx, 4), (fx + w * 0.16, 9), (fx, 14)], col)
        rect(w * 0.15, mid - 6, w * 0.85, mid + 2, (120, 85, 50))
    elif scene == "gulf":
        rect(0, mid, w, h, (30, 90, 130))
        rect(w * 0.08, mid - 14, w * 0.72, mid - 2, (40, 40, 45))
        rect(w * 0.55, mid - 26, w * 0.68, mid - 14, (200, 200, 200))
        line([(w * 0.15, mid - 2), (w * 0.85, mid - 2)], (255, 255, 255), 1)
        ell(w * 0.78, 4, w * 0.92, 14, (255, 220, 120))
        for cx in (w * 0.20, w * 0.35, w * 0.50):
            ell(cx, mid - 34, cx + 12, mid - 24, (150, 150, 150))
    elif scene == "bridge":
        rect(0, mid + 8, w, h, (50, 110, 150))
        for wx in range(0, w, 14):
            line([(wx, mid + 14), (wx + 8, mid + 14)], (220, 235, 245), 1)
            line([(wx + 4, mid + 22), (wx + 12, mid + 22)], (220, 235, 245), 1)
        line([(0, mid), (w * 0.42, mid)], (90, 60, 40), 7)
        line([(w * 0.58, mid), (w, mid)], (90, 60, 40), 7)
        line([(w * 0.30, mid), (w * 0.30, mid - 24)], (90, 60, 40), 4)
        line([(w * 0.70, mid), (w * 0.70, mid - 24)], (90, 60, 40), 4)
        line([(w * 0.30, mid - 24), (w * 0.70, mid - 24)], (140, 100, 60), 2)
        poly([(w * 0.42, mid), (w * 0.50, mid + 18), (w * 0.58, mid)],
             (120, 80, 55))
        ell(w * 0.78, 3, w * 0.92, 13, (255, 220, 120))
    elif scene == "city":
        rect(0, mid, w, h, (70, 70, 75))
        for i, bh in enumerate((16, 26, 20, 30, 18)):
            bx = w * (0.06 + 0.18 * i)
            rect(bx, mid - bh, bx + w * 0.13, mid, (45, 45, 50))
        ell(w * 0.30, 2, w * 0.44, 12, (220, 130, 60))
        for cx in (w * 0.25, w * 0.60):
            ell(cx, 6, cx + 14, 16, (180, 180, 180))
    elif scene == "gaza":
        rect(0, mid, w, h, (210, 185, 140))
        for i in range(3):
            tx = w * (0.10 + 0.30 * i)
            poly([(tx, mid), (tx + w * 0.11, mid - 16),
                  (tx + w * 0.22, mid)], (250, 245, 230))
        line([(0, mid - 20), (w, mid - 20)], (120, 110, 100), 3)
        ell(w * 0.80, 3, w * 0.92, 12, (255, 210, 110))
    elif scene == "ballot":
        rect(w * 0.35, mid - 18, w * 0.65, mid + 6, (40, 90, 180))
        rect(w * 0.38, mid - 22, w * 0.62, mid - 18, (30, 70, 150))
        rect(w * 0.44, 4, w * 0.56, 14, (255, 255, 255))
        line([(w * 0.44, 10), (w * 0.48, 14), (w * 0.56, 5)],
             (0, 140, 60), 3)
        ell(w * 0.10, 4, w * 0.20, 12, (200, 200, 200))
    elif scene == "clinic":
        rect(w * 0.30, mid - 20, w * 0.70, mid + 4, (255, 255, 255))
        rect(w * 0.47, mid - 16, w * 0.53, mid - 2, (200, 40, 40))
        rect(w * 0.42, mid - 12, w * 0.58, mid - 6, (200, 40, 40))
        for cx, cy in ((w * 0.18, 10), (w * 0.80, 8), (w * 0.70, 16)):
            ell(cx, cy, cx + 6, cy + 6, (200, 60, 60))
    elif scene == "chart":
        line([(w * 0.10, 6), (w * 0.10, mid + 4)], (60, 60, 60), 2)
        line([(w * 0.10, mid + 4), (w * 0.92, mid + 4)], (60, 60, 60), 2)
        for i, bh in enumerate((8, 14, 11, 20)):
            bx = w * (0.20 + 0.17 * i)
            rect(bx, mid + 4 - bh, bx + w * 0.10, mid + 4, (40, 120, 80))
        line([(w * 0.12, mid - 6), (w * 0.35, mid - 14),
              (w * 0.60, mid - 10), (w * 0.88, mid - 22)],
             (0, 110, 60), 3)
    elif scene == "bell":
        ell(w * 0.38, mid - 20, w * 0.62, mid + 2, (220, 170, 40))
        rect(w * 0.47, mid - 28, w * 0.53, mid - 20, (180, 140, 30))
        line([(w * 0.15, mid - 8), (w * 0.85, mid - 8)], (60, 60, 60), 2)
        line([(w * 0.15, mid - 8), (w * 0.85, mid - 20)], (0, 110, 60), 2)
    elif scene == "euloan":
        for i in range(8):
            a = 2 * math.pi * i / 8
            cx = w * 0.5 + math.cos(a) * w * 0.28
            cy = h * 0.42 + math.sin(a) * h * 0.28
            poly([(cx, cy - 4), (cx + 3, cy), (cx, cy + 4), (cx - 3, cy)],
                 (240, 200, 40))
        ell(w * 0.42, h * 0.30, w * 0.58, h * 0.55, (240, 200, 40))
        d.text((X(w * 0.485), Y(h * 0.34)), "E",
               font=font(SANS_B, 14), fill=(40, 60, 140))
    elif scene == "court":
        line([(w * 0.50, 4), (w * 0.50, mid)], (60, 60, 60), 3)
        line([(w * 0.22, 10), (w * 0.78, 10)], (60, 60, 60), 3)
        line([(w * 0.22, 10), (w * 0.22, 20)], (60, 60, 60), 2)
        line([(w * 0.78, 10), (w * 0.78, 20)], (60, 60, 60), 2)
        poly([(w * 0.12, 20), (w * 0.32, 20), (w * 0.22, 30)], (180, 140, 40))
        poly([(w * 0.68, 20), (w * 0.88, 20), (w * 0.78, 30)], (180, 140, 40))
        rect(w * 0.40, mid, w * 0.60, mid + 4, (90, 70, 50))
    elif scene == "bank":
        poly([(w * 0.15, mid - 18), (w * 0.50, mid - 30),
              (w * 0.85, mid - 18)], (140, 120, 90))
        for i in range(4):
            bx = w * (0.20 + 0.17 * i)
            rect(bx, mid - 18, bx + w * 0.07, mid, (200, 190, 170))
        rect(w * 0.15, mid, w * 0.85, mid + 4, (120, 100, 80))
    elif scene == "trade":
        line([(w * 0.10, mid - 12), (w * 0.55, mid - 12)], (0, 110, 60), 3)
        poly([(w * 0.55, mid - 18), (w * 0.68, mid - 12),
              (w * 0.55, mid - 6)], (0, 110, 60))
        line([(w * 0.90, mid + 2), (w * 0.45, mid + 2)], (178, 34, 34), 3)
        poly([(w * 0.45, mid - 4), (w * 0.32, mid + 2),
              (w * 0.45, mid + 8)], (178, 34, 34))
        rect(w * 0.12, 6, w * 0.26, 16, (200, 160, 60))
        rect(w * 0.74, 6, w * 0.88, 16, (200, 160, 60))
    elif scene == "gavel":
        rect(0, mid, w, h, (150, 130, 105))
        line([(w * 0.18, mid - 16), (w * 0.82, mid - 4)], (120, 85, 50), 5)
        rect(w * 0.60, mid - 20, w * 0.86, mid - 8, (90, 60, 40))
        rect(w * 0.58, mid - 22, w * 0.88, mid - 18, (110, 75, 50))
        rect(w * 0.12, mid, w * 0.46, mid + 5, (90, 70, 50))
        line([(w * 0.30, 6), (w * 0.30, mid - 16)], (60, 60, 60), 2)
    return img


# ------------------------------------------------------------------
# World map: simplified continent outlines, Robinson projection.
# ------------------------------------------------------------------

LAND_POLYS = [
    [(-168, 66), (-150, 70), (-130, 71), (-110, 68), (-95, 80),
     (-80, 73), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-80, 26), (-86, 21), (-92, 15), (-97, 16), (-105, 20),
     (-112, 28), (-120, 34), (-125, 40), (-125, 49), (-135, 58),
     (-150, 60), (-165, 60)],
    [(-80, 10), (-77, 4), (-70, -3), (-60, 0), (-50, 0), (-40, -5),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-65, -40),
     (-70, -50), (-73, -40), (-72, -30), (-70, -18), (-77, -12),
     (-80, -3), (-81, 5)],
    [(-17, 15), (-16, 21), (-10, 31), (-5, 35), (0, 36), (10, 37),
     (20, 32), (30, 31), (35, 28), (38, 22), (43, 12), (51, 11),
     (48, 2), (41, -2), (40, -10), (36, -18), (33, -26), (28, -33),
     (20, -35), (17, -30), (14, -22), (12, -12), (13, -5), (9, 4),
     (0, 5), (-8, 4), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 52), (8, 55),
     (12, 56), (18, 56), (21, 55), (24, 58), (28, 62), (30, 70),
     (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (95, 76),
     (110, 74), (125, 73), (140, 72), (155, 70), (170, 67), (178, 65),
     (170, 60), (162, 56), (156, 51), (142, 46), (135, 43), (130, 38),
     (127, 35), (122, 31), (118, 25), (110, 20), (105, 9), (100, 8),
     (97, 15), (92, 21), (88, 22), (80, 10), (77, 8), (73, 16),
     (68, 22), (62, 25), (57, 26), (52, 28), (50, 30), (48, 30),
     (44, 29), (40, 31), (36, 36), (33, 36), (30, 36), (26, 38),
     (23, 36), (20, 40), (15, 44), (10, 44), (8, 38), (3, 37),
     (-2, 37), (-6, 36)],
    [(113, -22), (114, -30), (118, -35), (125, -32), (132, -32),
     (138, -35), (145, -38), (150, -37), (153, -27), (150, -22),
     (146, -19), (142, -11), (136, -12), (131, -12), (126, -14),
     (122, -17), (116, -20)],
    [(129, -6), (131, -2), (136, -4), (141, -8), (138, -10), (132, -10)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 42),
     (143, 44), (140, 42), (137, 37), (133, 34)],
    [(166, -34), (168, -38), (174, -41), (178, -38), (175, -35),
     (172, -35), (168, -37)],
]

_ROB_X = [1.0000, 0.9986, 0.9954, 0.9900, 0.9822, 0.9730, 0.9600,
          0.9427, 0.9216, 0.8962, 0.8679, 0.8350, 0.7986, 0.7597,
          0.7186, 0.6732, 0.6213, 0.5722, 0.5322]
_ROB_Y = [0.0000, 0.0620, 0.1240, 0.1860, 0.2480, 0.3100, 0.3720,
          0.4340, 0.4958, 0.5571, 0.6176, 0.6769, 0.7346, 0.7903,
          0.8435, 0.8936, 0.9394, 0.9761, 1.0000]


def robinson(lon, lat):
    a = abs(lat)
    i = min(17, int(a // 5))
    f = (a - i * 5) / 5
    xf = _ROB_X[i] + f * (_ROB_X[i + 1] - _ROB_X[i])
    yf = _ROB_Y[i] + f * (_ROB_Y[i + 1] - _ROB_Y[i])
    x = 0.8487 * math.radians(lon) * xf
    y = 1.3523 * yf * (1 if lat >= 0 else -1)
    return x, y


PIN_LONLAT = {
    1: (114.0, 22.5), 2: (48.0, 29.3), 3: (36.5, 45.3),
    4: (30.7, 46.5), 5: (34.5, 31.5), 6: (-150.0, 64.0),
    7: (-98.0, 39.0), 8: (-121.9, 37.4), 9: (-122.4, 37.8),
    10: (4.35, 50.85), 11: (29.0, 41.0), 12: (8.7, 50.1),
    13: (121.0, 14.6), 14: (116.4, 39.9), 15: (32.6, 0.3),
}
DOT_LONLAT = {
    16: (50.6, 26.2), 17: (34.2, 31.3), 18: (-77.0, 38.9),
    19: (-0.1, 51.5), 20: (-77.0, 38.9), 21: (-122.0, 37.5),
    22: (-77.0, 38.9), 23: (106.8, -6.2), 24: (39.0, 14.5),
    25: (26.2, 45.4), 26: (-80.2, 25.8), 27: (2.8, 50.4),
    28: (-0.1, 51.5), 29: (77.2, 28.6), 30: (80.3, 15.9),
    31: (0.1, 52.2), 32: (4.35, 50.85), 33: (178.0, -17.5),
    34: (25.0, -2.0),
}
PIN_CENTERS = []
# Display nudges in pixels for pins that sit on the same map pixel
# (Kerch, Odesa and Istanbul around the Black Sea; Santa Clara and
# San Francisco in California; Brussels and Frankfurt in Europe).
# The nudge keeps each pin readable while staying next to its place.
PIN_OFFSET = {2: (-14, -12), 3: (-20, -16), 4: (16, -16),
              5: (14, 10), 7: (0, -18), 8: (-12, 6), 9: (16, -4),
              10: (-6, -20), 11: (-16, 14), 12: (-24, 2)}


def draw_map(img, d, x, y, w, h):
    layer = Image.new("RGB", (sc(w), sc(h)), SEA)
    ld = Draw(ImageDraw.Draw(layer))

    def proj(lon, lat):
        rx, ry = robinson(lon, lat)
        return ((rx + 2.666) / 5.332 * w, (1.320 - ry) / 2.313 * h)

    for poly in LAND_POLYS:
        pts = [proj(lon, lat) for lon, lat in poly]
        ld.poly(pts, fill=LAND, outline=INK)
    img.paste(layer, (sc(x), sc(y)))
    for num, (lon, lat) in DOT_LONLAT.items():
        px, py = x + proj(lon, lat)[0], y + proj(lon, lat)[1]
        col = REGION_COLORS[STORIES[num - 1]["region"]]
        d.ell([px - 3, py - 3, px + 3, py + 3], fill=col, outline=INK,
              width=1)
    for num, (lon, lat) in PIN_LONLAT.items():
        tx, ty = x + proj(lon, lat)[0], y + proj(lon, lat)[1]
        ox, oy = PIN_OFFSET.get(num, (0, 0))
        px, py = tx + ox, ty + oy
        if (ox, oy) != (0, 0):
            d.line([(tx, ty), (px, py)], fill=INK, width=1)
            d.ell([tx - 2, ty - 2, tx + 2, ty + 2], fill=INK)
        PIN_CENTERS.append((num, px, py))
        col = REGION_COLORS[STORIES[num - 1]["region"]]
        d.ell([px - 8, py - 8, px + 8, py + 8], fill=col, outline=INK,
              width=1)
        f = font(SANS_B, 10)
        t = str(num)
        tw = d.length(t, f)
        d.text((px - tw / 2, py - 6), t, f, (255, 255, 255))


# ------------------------------------------------------------------
# Cards
# ------------------------------------------------------------------

CARD_BOUNDS = []
HEIGHT_LOG = []


def card_frame(d, x, y, w, h):
    d.rect([x, y, x + w, y + h], fill=CARD, outline=INK, width=2)
    d.rect([x, y, x + w, y + 5], fill=RED)
    return x + 12, y + 12, w - 24, h - 24


def source_mark(d, ix, iy, iw, ih, source, group):
    f = font(SANS, 8)
    tw = d.length(source, f)
    put(d, ix + iw - tw, iy + ih - 10, source, f, GREY, group,
        label="source")


def tag_line(d, ix, y, iw, text, color, group):
    f, lines, lh = block(d, text, SANS_B, 9, iw, 2, f"tag {group}")
    for ln in lines:
        put(d, ix, y, ln, f, color, group, label="tag")
        y += lh
    return y


def draw_big(img, d, x, y, w, h, story):
    num = story["id"]
    group = f"card{num}"
    ix, iy, iw, ih = card_frame(d, x, y, w, h)
    CARD_BOUNDS.append((group, ix, iy, ix + iw, iy + ih))
    col = REGION_COLORS[story["region"]]
    scene_h = 32 if num == 3 else 28
    img.paste(scene_image(story["scene"], iw, scene_h), (sc(ix), sc(iy)))
    put(d, ix, iy + scene_h + 1, story["caption"], font(SANS, 8), GREY,
        group, label="caption")
    cy = iy + scene_h + 12
    put(d, ix, cy, f"{num}. {story['cat']}", font(SANS_B, 13), col,
        group, label="cat")
    hy = cy + 15
    f, lines, lh = block(d, story["title"], SANS_B, BIG_TITLE, iw, 2,
                         f"big title {num}")
    for ln in lines:
        put(d, ix, hy, ln, f, INK, group, label="title")
        hy += lh
    sy = hy + 3
    f2, lines2, lh2 = block(d, story["summary"], SANS, BODY, iw, 3,
                            f"big sub {num}")
    for ln in lines2:
        put(d, ix, sy, ln, f2, INK, group, label="sub")
        sy += lh2
    if story.get("tag"):
        color = GREEN if story["status"] == "CONFIRMED" else AMBER
        tag_line(d, ix, sy + 3, iw, story["tag"], color, group)
    source_mark(d, ix, iy, iw, ih, story["source"], group)
    used = scene_h + 12 + 15 + len(lines) * lh + 3 + len(lines2) * lh2
    HEIGHT_LOG.append((f"big card {num}", used, ih - 12))


def draw_small(img, d, x, y, w, h, story):
    num = story["id"]
    group = f"card{num}"
    ix, iy, iw, ih = card_frame(d, x, y, w, h)
    CARD_BOUNDS.append((group, ix, iy, ix + iw, iy + ih))
    col = REGION_COLORS[story["region"]]
    scene_h = 34
    img.paste(scene_image(story["scene"], iw, scene_h), (sc(ix), sc(iy)))
    cy = iy + scene_h + 4
    put(d, ix, cy, f"{num}. {story['cat']}", font(SANS_B, 8), col,
        group, label="cat")
    hy = cy + 16
    f, lines, lh = block(d, story["title"], SANS_B, TITLE, iw, 2,
                         f"title {num}")
    for ln in lines:
        put(d, ix, hy, ln, f, INK, group, label="title")
        hy += lh
    sy = cy + 16 + 2 * lh + 3
    f2, lines2, lh2 = block(d, story["summary"], SANS, BODY, iw, 2,
                            f"sub {num}")
    for ln in lines2:
        put(d, ix, sy, ln, f2, INK, group, label="sub")
        sy += lh2
    if story.get("tag"):
        color = GREEN if story["status"] == "CONFIRMED" else AMBER
        tag_line(d, ix, sy + 3, iw, story["tag"], color, group)
    source_mark(d, ix, iy, iw, ih, story["source"], group)
    used = scene_h + 4 + 16 + 2 * lh + 3 + len(lines2) * lh2
    HEIGHT_LOG.append((f"small card {num}", used, ih - 12))


def check_layout():
    problems = []
    for label, got, need in HEIGHT_LOG:
        if got > need:
            problems.append(f"{label}: content {got}px over frame {need}px")
    for i, (n1, x1, y1) in enumerate(PIN_CENTERS):
        for n2, x2, y2 in PIN_CENTERS[i + 1:]:
            dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            if dist < 16:
                problems.append(f"map pins {n1} and {n2} collide "
                                f"({dist:.1f}px apart)")
    bounds = {g: (x0, y0, x1, y1) for g, x0, y0, x1, y1 in CARD_BOUNDS}
    by_group = {}
    for group, label, box in BOXES:
        by_group.setdefault(group, []).append((label, box))
        x0, y0, x1, y1 = box
        if x0 < 12 or y0 < 12 or x1 > 1012 or y1 > 1012:
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
          f"{len(PIN_CENTERS)} pins")


def main():
    check_stories()
    counts = region_counts()
    n_regions = sum(1 for r in REGIONS if counts[r] > 0)
    kicker_right = (f"{len(STORIES)} STORIES - {n_regions} REGIONS - "
                    "ALL FROM WEDNESDAY")

    img = Image.new("RGB", (sc(W), sc(H)), PAPER)
    d = Draw(ImageDraw.Draw(img))
    d.rect([10, 10, W - 11, H - 11], outline=INK, width=4)

    put(d, 16, 14, "A DAY OF WORLD NEWS, IN ONE FRAME", font(SANS_B, 13),
        RED, "header", label="kicker")
    rw = d.length(kicker_right, font(SANS_B, 13))
    put(d, 1008 - rw, 14, kicker_right, font(SANS_B, 13), INK, "header",
        label="kicker-right")
    d.line([(16, 31), (1008, 31)], fill=RED, width=2)

    size = 30
    while (d.length("Wednesday 18 November 2026", font(SERIF_B, size))
           > 980 and size > 28):
        size -= 2
    put_c(d, W // 2, 33, "Wednesday 18 November 2026", font(SERIF_B, size),
          INK, "header", label="banner")
    d.line([(16, 65), (1008, 65)], fill=RED, width=3)

    seg_font = font(SANS_B, 10)
    segs = [(f"{r} {counts[r]}", REGION_COLORS[r]) for r in REGIONS]
    sep_w = d.length(" - ", seg_font)
    total = sum(d.length(t, seg_font) for t, _ in segs)
    total += sep_w * (len(segs) - 1)
    sx = (W - total) / 2
    for i, (text, col) in enumerate(segs):
        put(d, sx, 69, text, seg_font, col, "header", label="region-bar")
        sx += d.length(text, seg_font)
        if i < len(segs) - 1:
            put(d, sx, 69, " - ", seg_font, GREY, "header", label="sep")
            sx += sep_w

    cell_w = (1008 - 16) / 6
    for i, (num, label, col, arrow) in enumerate(NUMBERS):
        cx = 16 + i * cell_w
        nfont = font(SANS_B, 13)
        if arrow:
            tw = d.length(num, nfont)
            total_w = tw + 6 + 10
            ax = cx + cell_w / 2 - total_w / 2
            if arrow == "down":
                d.poly([(ax, 82), (ax + 10, 82), (ax + 5, 90)], fill=col)
            put(d, ax + 16, 81, num, nfont, col, "numbers", label="num")
        else:
            put_c(d, cx + cell_w / 2, 81, num, nfont, col, "numbers",
                  label="num")
        f, lines, lh = block(d, label, SANS, 7, cell_w - 12, 2,
                             f"number label {i}")
        ly2 = 96
        for ln in lines:
            put_c(d, cx + cell_w / 2, ly2, ln, f, GREY, "numbers",
                  label="num-label")
            ly2 += lh
        if i:
            d.line([(cx, 83), (cx, 108)], fill=GREY, width=1)

    put_c(d, W // 2, 108, WHY_TEXT, font(SERIF, 10), INK, "header",
          label="why")

    for i in range(3):
        draw_big(img, d, 16 + i * 335, 122, 322, 164, CARDS[i])

    label = "HOW THE DAY UNFOLDED: "
    lw = d.length(label, font(SANS_B, 10))
    put(d, 16, 294, label, font(SANS_B, 10), RED, "header", label="thread")
    put(d, 16 + lw + 6, 294, THREAD_TEXT, font(SANS, 10), INK, "header",
        label="thread-text")

    for i in range(6):
        draw_small(img, d, 16 + i * 165, 307, 158, 146, CARDS[3 + i])
    for i in range(6):
        draw_small(img, d, 16 + i * 165, 456, 158, 158, CARDS[9 + i])

    mx, my, mw, mh = 16, 619, 486, 348
    d.rect([mx, my, mx + mw, my + mh], fill=CARD, outline=INK, width=2)
    d.rect([mx, my, mx + mw, my + 5], fill=RED)
    put(d, mx + 12, my + 12, "WHERE THE STORIES SIT", font(SANS_B, 13),
        INK, "map", label="map-title")
    draw_map(img, d, mx + 12, my + 32, mw - 24, 296)
    leg_font = font(SANS_B, 8)
    leg_w = 0
    for r in REGIONS:
        leg_w += 6 + 4 + d.length(r, leg_font)
    leg_w += 8 * (len(REGIONS) - 1)
    lx_leg = mx + mw / 2 - leg_w / 2
    for r in REGIONS:
        d.ell([lx_leg, my + 334, lx_leg + 6, my + 340],
              fill=REGION_COLORS[r])
        put(d, lx_leg + 10, my + 333, r, leg_font, REGION_COLORS[r],
            "map", label="legend")
        lx_leg += 6 + 4 + d.length(r, leg_font) + 8

    lx, ly, lw, lh = 514, 619, 494, 348
    d.rect([lx, ly, lx + lw, ly + lh], fill=CARD, outline=INK, width=2)
    d.rect([lx, ly, lx + lw, ly + 5], fill=RED)
    put(d, lx + 12, ly + 12, "THE REST OF WEDNESDAY, 18 NOVEMBER",
        font(SANS_B, 13), INK, "list", label="list-title")
    yy = ly + 30
    list_top, list_h = ly + 30, lh - 34
    for gi, (region, items) in enumerate(ALSO_BY_REGION):
        col = REGION_COLORS[region]
        put(d, lx + 12, yy, region, font(SANS_B, 9), col, "list",
            label="head")
        yy += 8
        for s in items:
            d.ell([lx + 12, yy + 1, lx + 18, yy + 7], fill=col)
            put(d, lx + 24, yy, f"{s['id']}. {s['title']}",
                font(SANS, LIST), INK, "list", label="row")
            sf = font(SANS, 8)
            sw = d.length(s["source"], sf)
            put(d, lx + lw - 12 - sw, yy + 1, s["source"], sf, GREY,
                "list", label="row-source")
            yy += 12
        if gi < len(ALSO_BY_REGION) - 1:
            yy += 3
    HEIGHT_LOG.append(("list", yy - list_top, list_h))

    d.rect([16, 970, 1008, 986], outline=INK, width=2)
    d.rect([16, 970, 22, 986], fill=RED)
    put(d, 30, 974, DATECHECK_TEXT, font(SANS, 8), INK, "footer",
        label="datecheck")

    put_c(d, W // 2, 990,
          "Each item on this page took place, or was first reported, on "
          "Wednesday 18 November 2026. Anything still disputed is "
          "labelled a claim.",
          font(SANS, 8), GREY, "footer", label="footer1")
    put_c(d, W // 2, 999,
          "Reporting: Reuters, AP, PAHO, WHO, UN, BBC, CNBC, EU, USGS, "
          "Anadolu. Pictures drawn for this page. CONFIRMED = verified "
          "by a wire; CLAIM = the source's word, not checked alone.",
          font(SANS, 8), GREY, "footer", label="footer2")

    check_layout()
    img.save(OUT, optimize=True)
    print("saved", OUT)


if __name__ == "__main__":
    main()
