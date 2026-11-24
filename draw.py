#!/usr/bin/env python3
"""draw.py - renders entry.png for make.fun news-image-20261124.
'Tuesday 24 November 2026 - The World in One Day'.
Rendered with PIL + DejaVu fonts (draw-time only; the grader never
runs this file - main.py only copies entry.png, stdlib-only).
Flat 2D vector front page, 1024x1024, code-drawn.
Run: python3 draw.py  -> writes entry.png next to this file.
"""
import math
import os
import re

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# ---- palette (same as v2) ----
NAVY = (18, 34, 66)
NAVY2 = (28, 52, 96)
CREAM = (250, 243, 226)
PAPER = (253, 248, 236)
INK = (24, 28, 36)
RED = (178, 34, 34)
RED_DK = (140, 22, 22)
GOLD = (214, 164, 64)
BLUE = (52, 110, 168)
SKY = (198, 222, 238)
SEA = (176, 208, 228)
OLIVE = (148, 158, 92)
OLIVE_DK = (122, 134, 74)
GREEN = (46, 125, 70)
AMBER = (176, 120, 20)
PURPLE = (110, 80, 150)
GREY = (110, 114, 122)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
TEAL = (32, 120, 116)
ORANGE = (214, 110, 32)
BROWN = (122, 84, 52)
PINK = (216, 130, 140)
LIGHT_GREY = (228, 228, 224)
# DATE CHECK: high-contrast pale peach background, black text, red border
DC_BG = (255, 243, 232)

# ---- case helpers ----
# Words that must stay ALL-CAPS in title/sentence case.
ACRONYMS = {
    "COP31", "NATO", "EU", "AWACS", "AFCON", "KCNA", "WFP", "BBC", "AP",
    "AFP", "REUTERS", "US", "UK", "UN", "UNRWA", "CEO", "COP", "AI", "II",
    "NVIDIA", "CAS",
}
SPECIAL = {"SPACEX": "SpaceX", "SPACE.COM": "Space.com"}
# Small words kept lowercase in title case (unless first/last word).
SMALL_WORDS = {
    "a", "an", "the", "to", "in", "on", "at", "of", "for", "with", "by",
    "and", "or", "from", "over", "as", "since",
}
# Proper nouns that stay capitalised in sentence-case decks.
PROPER = {
    "KHARG", "TRUMP", "PACIFIC", "POLISH", "BENGHAZI", "SENEGAL", "MOROCCO",
}


def _split_punct(tok):
    """Split token into (leading punct, core, trailing punct). '$' stays in core."""
    i = 0
    while i < len(tok) and not tok[i].isalnum() and tok[i] != '$':
        i += 1
    j = len(tok)
    while j > i and not tok[j - 1].isalnum():
        j -= 1
    return tok[:i], tok[i:j], tok[j:]


def _title_part(part, first, last):
    """Title-case one hyphen-separated part (no punctuation)."""
    if not part:
        return part
    up = part.upper()
    if up in SPECIAL:
        return SPECIAL[up]
    if up in ACRONYMS:
        return up
    if part[0].isdigit():
        m = re.match(r"^([0-9][0-9.,]*)([A-Za-z].*)?$", part)
        if not m or not m.group(2):
            return part
        tail = m.group(2)
        if len(tail) == 1:
            return part
        return m.group(1) + tail.lower()
    if part.lower() in SMALL_WORDS and not first and not last:
        return part.lower()
    return part.capitalize()


def _title_core(core, first, last):
    if not core:
        return core
    if core.startswith("$"):
        return core
    return "-".join(
        _title_part(p, first and i == 0, last and i == len(core.split("-")) - 1)
        for i, p in enumerate(core.split("-"))
    )


def title_case(text):
    """Headline Title Case with acronyms kept caps, small words lower."""
    words = text.split(" ")
    out = []
    for wi, w in enumerate(words):
        lead, core, trail = _split_punct(w)
        out.append(lead + _title_core(core, wi == 0, wi == len(words) - 1) + trail)
    return " ".join(out)


def _sentence_part(part, first_alpha):
    """Sentence-case one hyphen-separated part."""
    if not part:
        return part
    up = part.upper()
    if up in SPECIAL:
        return SPECIAL[up]
    if up in ACRONYMS:
        return up
    if up in PROPER:
        return part.capitalize()
    if part[0].isdigit():
        m = re.match(r"^([0-9][0-9.,]*)([A-Za-z].*)?$", part)
        if not m or not m.group(2):
            return part
        tail = m.group(2)
        if len(tail) == 1:
            return part
        return m.group(1) + tail.lower()
    if first_alpha:
        return part.capitalize()
    return part.lower()


def sentence_case(text):
    """Sentence case: only the first alphabetic word (plus acronyms and
    proper nouns) is capitalised."""
    words = text.split(" ")
    out = []
    seen_alpha = False
    for w in words:
        lead, core, trail = _split_punct(w)
        if not core:
            out.append(w)
            continue
        if core.startswith("$"):
            out.append(w)
            seen_alpha = seen_alpha or any(c.isalpha() for c in core)
            continue
        parts = core.split("-")
        done = []
        for p in parts:
            is_first = (not seen_alpha) and any(c.isalpha() for c in p)
            done.append(_sentence_part(p, is_first))
            if is_first:
                seen_alpha = True
        if any(c.isalpha() for c in core):
            seen_alpha = True
        out.append(lead + "-".join(done) + trail)
    return " ".join(out)

# ---- fonts ----
_FONTS = {}


def F(path, size):
    key = (path, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, size)
    return _FONTS[key]


# Every text draw is recorded (x0, y0, x1, y1, text) for the layout check.
PLACEMENTS = []


class CV:
    """Thin PIL wrapper keeping the v2 Canvas method names."""

    def __init__(self, w, h, bg):
        self.img = Image.new("RGB", (w, h), bg)
        self.d = ImageDraw.Draw(self.img)
        self.w, self.h = w, h

    def fill_rect(self, x, y, w, h, c):
        self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)

    def rect(self, x, y, w, h, c, t=1):
        self.d.rectangle([x, y, x + w - 1, y + h - 1], outline=c, width=t)

    def line(self, x0, y0, x1, y1, c, t=1):
        self.d.line([(x0, y0), (x1, y1)], fill=c, width=t)

    def circle(self, cx, cy, r, c, fill=True):
        box = [cx - r, cy - r, cx + r, cy + r]
        if fill:
            self.d.ellipse(box, fill=c)
        else:
            self.d.ellipse(box, outline=c, width=2)

    def triangle(self, pts, c):
        self.d.polygon(pts, fill=c)

    def polygon(self, pts, c):
        self.d.polygon(pts, fill=c)


def text_w(text, fnt):
    return fnt.getlength(text)


def draw_text(cv, x, y, text, fnt, color, align='l'):
    """Draw text; y is the top of the ascender. Records its bbox."""
    anchor = {'l': 'la', 'c': 'ma', 'r': 'ra'}[align]
    bbox = cv.d.textbbox((x, y), text, font=fnt, anchor=anchor)
    PLACEMENTS.append((bbox[0], bbox[1], bbox[2], bbox[3], text))
    cv.d.text((x, y), text, font=fnt, fill=color, anchor=anchor)
    return fnt.getlength(text)


def draw_text_c(cv, cx, cy, text, fnt, color):
    """Draw text centred on (cx, cy) (middle anchor)."""
    bbox = cv.d.textbbox((cx, cy), text, font=fnt, anchor='mm')
    PLACEMENTS.append((bbox[0], bbox[1], bbox[2], bbox[3], text))
    cv.d.text((cx, cy), text, font=fnt, fill=color, anchor='mm')
    return fnt.getlength(text)


def wrap_text(text, fnt, max_w):
    """Greedy word wrap using real font metrics; returns fitting lines."""
    words = text.split(' ')
    lines = []
    cur = ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # single word too long: hard-split by characters
            while fnt.getlength(wd) > max_w:
                k = 1
                while k < len(wd) and fnt.getlength(wd[:k + 1]) <= max_w:
                    k += 1
                lines.append(wd[:k])
                wd = wd[k:]
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ---- flat vector scenes (one per panel) ----
# Each scene draws inside rect (x, y, w, h). Same art as v2.


def scene_tanker(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    cv.circle(x + int(w * 0.78), y + int(h * 0.22), 12, GOLD)
    cv.fill_rect(x, y + int(h * 0.62), w, h - int(h * 0.62), BLUE)
    # tanker hull
    cv.fill_rect(x + int(w * 0.12), y + int(h * 0.42), int(w * 0.62), int(h * 0.24), RED_DK)
    cv.fill_rect(x + int(w * 0.18), y + int(h * 0.30), int(w * 0.18), int(h * 0.14), NAVY)
    cv.fill_rect(x + int(w * 0.40), y + int(h * 0.34), int(w * 0.10), int(h * 0.10), WHITE)
    cv.fill_rect(x + int(w * 0.52), y + int(h * 0.34), int(w * 0.10), int(h * 0.10), WHITE)
    # second ship far
    cv.fill_rect(x + int(w * 0.76), y + int(h * 0.52), int(w * 0.18), int(h * 0.12), NAVY2)
    # waves
    for i in range(5):
        cv.line(x + i * int(w / 5), y + int(h * 0.78) + (i % 2) * 4,
                x + (i + 1) * int(w / 5), y + int(h * 0.78) + (i % 2) * 4, WHITE, 2)


def scene_climate(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (222, 232, 214))
    # globe
    cx, cy, r = x + int(w * 0.5), y + int(h * 0.52), int(min(w, h) * 0.36)
    cv.circle(cx, cy, r, BLUE)
    cv.circle(cx - int(r * 0.3), cy - int(r * 0.2), int(r * 0.45), GREEN)
    cv.circle(cx + int(r * 0.35), cy + int(r * 0.3), int(r * 0.35), GREEN)
    cv.circle(cx, cy, r, NAVY, fill=False)
    # sun with rays
    sx, sy = x + int(w * 0.85), y + int(h * 0.18)
    cv.circle(sx, sy, 9, GOLD)
    for a in range(0, 360, 45):
        dx = int(14 * math.cos(math.radians(a)))
        dy = int(14 * math.sin(math.radians(a)))
        cv.line(sx, sy, sx + dx, sy + dy, GOLD, 2)
    # cracked ground line
    cv.line(x + int(w * 0.1), y + int(h * 0.88), x + int(w * 0.9), y + int(h * 0.88), BROWN, 3)


def scene_market(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (214, 232, 214))
    # bars
    base = y + int(h * 0.82)
    vals = [0.25, 0.4, 0.32, 0.55, 0.48, 0.72, 0.95]
    bw = int(w / (len(vals) + 1))
    for i, v in enumerate(vals):
        bh = int(h * 0.7 * v)
        col = GREEN if i == len(vals) - 1 else TEAL
        cv.fill_rect(x + int(w * 0.08) + i * bw, base - bh, int(bw * 0.6), bh, col)
    # arrow up
    cv.line(x + int(w * 0.08), y + int(h * 0.62), x + int(w * 0.9), y + int(h * 0.14), RED, 3)
    cv.triangle([(x + int(w * 0.9), y + int(h * 0.14)),
                 (x + int(w * 0.78), y + int(h * 0.14)),
                 (x + int(w * 0.9), y + int(h * 0.30))], RED)


def scene_radar(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, NAVY2)
    # radar rings (radii fit inside the h=30 strip: cy=y+16, r<=14)
    cx, cy = x + int(w * 0.5), y + int(h * 0.55)
    for r in (14, 9, 5):
        cv.circle(cx, cy, r, (120, 160, 210), fill=False)
    cv.line(cx, cy, cx + 12, cy - 8, GREEN, 2)
    cv.circle(cx + 12, cy - 8, 4, GREEN)
    # plane silhouette
    cv.triangle([(x + int(w * 0.12), y + int(h * 0.2)),
                 (x + int(w * 0.30), y + int(h * 0.16)),
                 (x + int(w * 0.16), y + int(h * 0.30))], WHITE)
    cv.fill_rect(x + int(w * 0.08), y + int(h * 0.86), int(w * 0.84), 3, GOLD)


def scene_ship(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (24, 44, 74))
    cv.fill_rect(x, y + int(h * 0.6), w, h - int(h * 0.6), (40, 90, 140))
    # corvette
    cv.fill_rect(x + int(w * 0.2), y + int(h * 0.42), int(w * 0.5), int(h * 0.18), GREY)
    cv.triangle([(x + int(w * 0.7), y + int(h * 0.42)),
                 (x + int(w * 0.7), y + int(h * 0.60)),
                 (x + int(w * 0.86), y + int(h * 0.60))], GREY)
    cv.fill_rect(x + int(w * 0.3), y + int(h * 0.32), int(w * 0.08), int(h * 0.12), WHITE)
    # explosion star
    ex, ey = x + int(w * 0.72), y + int(h * 0.36)
    cv.circle(ex, ey, 10, GOLD)
    cv.circle(ex, ey, 5, ORANGE)
    # drones
    cv.circle(x + int(w * 0.15), y + int(h * 0.22), 3, WHITE)
    cv.circle(x + int(w * 0.3), y + int(h * 0.12), 3, WHITE)


def scene_fire(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (40, 36, 36))
    # building
    cv.fill_rect(x + int(w * 0.12), y + int(h * 0.3), int(w * 0.76), int(h * 0.7), BROWN)
    for i in range(3):
        for j in range(2):
            cv.fill_rect(x + int(w * 0.2) + i * int(w * 0.24),
                         y + int(h * 0.42) + j * int(h * 0.22),
                         int(w * 0.12), int(h * 0.12), GOLD)
    # flames
    for i, fx in enumerate((0.25, 0.5, 0.75)):
        cv.triangle([(x + int(w * fx) - 14, y + int(h * 0.34)),
                     (x + int(w * fx), y + int(h * 0.02) - i * 3),
                     (x + int(w * fx) + 14, y + int(h * 0.34))], ORANGE if i % 2 else GOLD)
    # smoke
    cv.circle(x + int(w * 0.2), y + int(h * 0.08), 8, GREY)
    cv.circle(x + int(w * 0.6), y + int(h * 0.05), 7, GREY)


def scene_gaza(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (232, 214, 190))
    # buildings
    cv.fill_rect(x + int(w * 0.08), y + int(h * 0.45), int(w * 0.2), int(h * 0.55), (150, 130, 105))
    cv.fill_rect(x + int(w * 0.34), y + int(h * 0.3), int(w * 0.24), int(h * 0.7), (170, 148, 120))
    cv.fill_rect(x + int(w * 0.64), y + int(h * 0.5), int(w * 0.26), int(h * 0.5), (140, 120, 95))
    # smoke columns
    cv.circle(x + int(w * 0.42), y + int(h * 0.16), 10, GREY)
    cv.circle(x + int(w * 0.48), y + int(h * 0.08), 8, GREY)
    cv.circle(x + int(w * 0.78), y + int(h * 0.2), 9, (170, 170, 168))
    # sun
    cv.circle(x + int(w * 0.85), y + int(h * 0.14), 8, GOLD)


def scene_plane(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + int(h * 0.7), w, int(h * 0.3), OLIVE)
    # jet
    cv.triangle([(x + int(w * 0.15), y + int(h * 0.35)),
                 (x + int(w * 0.55), y + int(h * 0.28)),
                 (x + int(w * 0.2), y + int(h * 0.48))], NAVY)
    cv.fill_rect(x + int(w * 0.5), y + int(h * 0.28), int(w * 0.3), 4, NAVY)
    # warning triangle
    tx, ty = x + int(w * 0.8), y + int(h * 0.55)
    cv.triangle([(tx, ty - 12), (tx - 12, ty + 10), (tx + 12, ty + 10)], AMBER)
    draw_text_c(cv, tx, ty + 1, "!", F(SANS_B, 15), NAVY)


def scene_eu(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (30, 60, 140))
    cx, cy = x + int(w * 0.5), y + int(h * 0.5)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx = cx + int(0.32 * min(w, h) * math.cos(a))
        sy = cy + int(0.32 * min(w, h) * math.sin(a))
        cv.circle(sx, sy, 3, GOLD)
    cv.fill_rect(x + int(w * 0.1), y + int(h * 0.82), int(w * 0.8), 3, WHITE)


def scene_iowa(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + int(h * 0.62), w, int(h * 0.38), (190, 170, 90))
    # silo
    cv.fill_rect(x + int(w * 0.14), y + int(h * 0.3), int(w * 0.16), int(h * 0.34), GREY)
    cv.circle(x + int(w * 0.22), y + int(h * 0.3), int(w * 0.08), RED)
    # pause sign
    cv.fill_rect(x + int(w * 0.6), y + int(h * 0.14), int(w * 0.07), int(h * 0.4), RED)
    cv.fill_rect(x + int(w * 0.74), y + int(h * 0.14), int(w * 0.07), int(h * 0.4), RED)


def scene_bank(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (228, 226, 214))
    # bank building
    cv.triangle([(x + int(w * 0.1), y + int(h * 0.3)),
                 (x + int(w * 0.5), y + int(h * 0.08)),
                 (x + int(w * 0.9), y + int(h * 0.3))], NAVY2)
    cv.fill_rect(x + int(w * 0.14), y + int(h * 0.3), int(w * 0.72), int(h * 0.55), LIGHT_GREY)
    for i in range(4):
        cv.fill_rect(x + int(w * 0.2) + i * int(w * 0.17), y + int(h * 0.36),
                     int(w * 0.08), int(h * 0.44), NAVY2)
    draw_text_c(cv, x + w / 2, y + int(h * 0.62), "$", F(SANS_B, 15), RED)


def scene_anthropic(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (240, 226, 200))
    base = y + int(h * 0.85)
    vals = [0.3, 0.45, 0.4, 0.6, 0.55, 0.8]
    bw = int(w / (len(vals) + 1))
    for i, v in enumerate(vals):
        bh = int(h * 0.65 * v)
        cv.fill_rect(x + int(w * 0.08) + i * bw, base - bh, int(bw * 0.62), bh,
                     ORANGE if i == len(vals) - 1 else (200, 150, 90))
    draw_text_c(cv, x + w / 2, y + int(h * 0.30), "AI", F(SANS_B, 15), NAVY)


def scene_football(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (60, 140, 70))
    # pitch lines
    cv.rect(x + int(w * 0.08), y + int(h * 0.12), int(w * 0.84), int(h * 0.76), WHITE, 2)
    cv.circle(x + int(w * 0.5), y + int(h * 0.5), 12, WHITE, fill=False)
    cv.line(x + int(w * 0.5), y + int(h * 0.12), x + int(w * 0.5), y + int(h * 0.88), WHITE, 2)
    # ball
    cv.circle(x + int(w * 0.72), y + int(h * 0.68), 9, WHITE)
    cv.circle(x + int(w * 0.72), y + int(h * 0.68), 3, BLACK)


SCENES = {
    'tanker': scene_tanker, 'climate': scene_climate, 'market': scene_market,
    'radar': scene_radar, 'ship': scene_ship, 'fire': scene_fire,
    'gaza': scene_gaza, 'plane': scene_plane, 'eu': scene_eu,
    'iowa': scene_iowa, 'bank': scene_bank, 'anthropic': scene_anthropic,
    'football': scene_football,
}

# ---- world map (same continents and pins as v2; all pins on land) ----
CONTINENTS = {
    'NA': [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
           (-75, 62), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
           (-80, 26), (-85, 20), (-90, 15), (-95, 18), (-100, 20), (-105, 22),
           (-110, 25), (-115, 30), (-120, 35), (-125, 42), (-130, 50),
           (-140, 58), (-155, 60), (-165, 60)],
    'SA': [(-80, 10), (-75, 5), (-70, 0), (-65, -5), (-60, -10), (-55, -15),
           (-50, -20), (-45, -25), (-40, -30), (-45, -35), (-55, -40),
           (-60, -45), (-65, -50), (-70, -55), (-75, -50), (-75, -40),
           (-75, -30), (-78, -20), (-80, -12), (-82, -5), (-80, 5)],
    'AFR': [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
            (35, 28), (40, 20), (43, 12), (48, 10), (51, 12), (45, 5),
            (40, -5), (35, -15), (30, -25), (25, -30), (20, -35), (15, -30),
            (12, -18), (12, -8), (9, 0), (5, 5), (-5, 5), (-10, 8), (-15, 12)],
    'EUR': [(-10, 36), (-5, 44), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
            (15, 58), (20, 55), (25, 60), (30, 62), (35, 65), (40, 68),
            (45, 68), (40, 60), (35, 55), (30, 50), (25, 45), (20, 40),
            (15, 38), (10, 38), (5, 38), (0, 38), (-5, 36)],
    'ASIA': [(40, 68), (50, 70), (60, 72), (70, 73), (80, 74), (90, 75),
             (100, 76), (110, 76), (120, 75), (130, 72), (140, 72), (150, 70),
             (160, 68), (170, 67), (178, 65), (170, 60), (160, 58), (155, 52),
             (150, 45), (145, 40), (140, 38), (135, 35), (130, 33), (127, 35),
             (122, 38), (120, 32), (115, 25), (110, 20), (108, 12), (105, 8),
             (100, 5), (97, 10), (95, 15), (92, 20), (90, 22), (85, 20),
             (80, 15), (77, 8), (75, 12), (70, 20), (65, 25), (60, 25),
             (55, 25), (50, 28), (48, 30), (45, 30), (40, 29), (35, 29.5),
             (33, 31), (33.5, 33), (37, 34.5), (40, 35), (42, 35), (38, 36),
             (33, 35.5), (28, 36.5), (26, 38.5), (27, 40), (30, 41),
             (35, 41.5), (40, 40), (38, 45), (40, 55), (40, 62)],
    'IDN_SUMATRA': [(95, 5.5), (98, 3.5), (101, 0.5), (103, -1.5),
                    (105, -3.5), (106, -5), (104, -5.5), (102, -3),
                    (100, -0.5), (97, 2), (95, 4.5)],
    'IDN_JAVA': [(104, -4.5), (108, -5), (112, -5.5), (114, -6),
                 (114, -9.5), (110, -9.5), (106, -9), (104, -7)],
    'AUS': [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
            (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
            (153, -32), (153, -27), (150, -22), (146, -19), (142, -11),
            (137, -12), (132, -12), (127, -14), (122, -17), (118, -20)],
}

# (number, lon, lat, dx, dy) - dx/dy manual decluster offsets in px.
# v2: every pin centre on rendered land (verified point-in-polygon +
# pixel ring); pins 3/12 both New York, declustered; pin 12 moved
# from San Francisco to New York (its story's city).
PINS = [
    (1, 51.4, 35.7, 5, 0),      # Tehran
    (2, 30.7, 36.9, -2, -4),    # Antalya
    (3, -74.0, 40.7, 0, -14),   # New York
    (4, 21.0, 52.2, 6, 0),      # Warsaw
    (5, 20.1, 32.1, 0, 10),     # Benghazi
    (6, 106.8, -6.2, 0, 1),     # Jakarta (on new Java island polygon)
    (7, 34.5, 31.5, 8, 0),      # Gaza
    (8, 130.9, 37.5, -6, -6),   # Ulleung
    (9, 4.35, 50.85, 2, 6),     # Brussels
    (10, -93.1, 41.9, -4, -10), # Iowa
    (11, -77.0, 38.9, -22, 12), # Washington
    (12, -74.0, 40.7, -10, 2),  # New York (Anthropic)
    (13, -17.4, 14.7, 12, 0),   # Dakar
]


# ---- page data ----
# Headlines/decks are stored in v2 ALL-CAPS form and converted at draw
# time: headlines -> Title Case, decks -> sentence case (acronyms kept).
VERACITY = {'C': ('CONFIRMED', GREEN), 'O': ('OFFICIALS', BLUE),
            'R': ('REPORTED', AMBER), 'F': ('FORECAST', PURPLE)}

HEROES = [
    dict(num='01', city='KHARG ISLAND', region='MIDDLE EAST', scene='tanker',
         headline='IRAN VOWS TO FIGHT US BLOCKADE',
         deck='14 TANKERS AT KHARG; TRUMP WARNS THEY WILL SINK',
         source='REUTERS • EURONEWS • FOX NEWS', tag='O'),
    dict(num='02', city='ANTALYA', region='GLOBAL', scene='climate',
         headline='COP31 ENDS WITH NO DEAL',
         deck='FIRST NO-DEAL COP SINCE 2009; PACIFIC IN DESPAIR',
         source='BBC • CNN • GUARDIAN', tag='C'),
    dict(num='03', city='NEW YORK', region='AMERICAS', scene='market',
         headline='HUANG BACK AT NVIDIA',
         deck='CEO REINSTATED IN TRUMP DEAL; SHARES SURGE',
         source='REUTERS • BLOOMBERG', tag='R'),
]

SMALL = [
    dict(num='04', city='WARSAW', scene='radar',
         headline='NATO SENDS AWACS TO POLAND',
         deck='3 MISSILES HIT POLISH SOIL', source='REUTERS', tag='C'),
    dict(num='05', city='BENGHAZI', scene='ship',
         headline='UKRAINE SINKS RUSSIAN SHIP',
         deck='HIT BY DRONES IN BENGHAZI PORT', source='REUTERS', tag='O'),
    dict(num='06', city='INDONESIA', scene='fire',
         headline='24 DEAD IN FACTORY FIRE',
         deck='34 MISSING; SEARCH ON', source='REUTERS', tag='C'),
    dict(num='07', city='GAZA', scene='gaza',
         headline='STRIKES KILL 3 IN GAZA',
         deck='UNRWA WORKER AMONG DEAD', source='REUTERS', tag='C'),
    dict(num='08', city='ULLEUNG', scene='plane',
         headline='RUSSIAN JET SPARKS ALERT',
         deck='WARNING LIFTED AFTER 3 MINUTES', source='REUTERS', tag='C'),
    dict(num='09', city='BRUSSELS', scene='eu',
         headline='EU PROPOSES NEW RUSSIA CURBS',
         deck='ATHLETE BAN IN 22ND PACKAGE', source='REUTERS', tag='O'),
    dict(num='10', city='IOWA', scene='iowa',
         headline='TRUMP PAUSES IOWA BLAST',
         deck='TOXIC LEAD AZIDE STAYS PUT', source='REUTERS', tag='C'),
    dict(num='11', city='WASHINGTON', scene='bank',
         headline='US HITS IRAN SHADOW BANKS',
         deck='$15BN IN FLOWS FLAGGED', source='US TREASURY', tag='C'),
    dict(num='12', city='NEW YORK', scene='anthropic',
         headline='ANTHROPIC OPTIONS DEBUT',
         deck='BRISK VOLUME; SHARES SLIP', source='REUTERS', tag='R'),
    dict(num='13', city='DAKAR', scene='football',
         headline='CAS TO RULE ON AFCON TITLE',
         deck='SENEGAL APPEALS MOROCCO WIN', source='REUTERS', tag='F'),
]

ALSO_ON = [
    "SINGER AHMADI GETS 74 LASHES (REUTERS)",
    "GERMANY TO USE KYIV DELTA WAR TOOL (REUTERS)",
    "ZELENSKIY: RUSSIA PLANS NEW STRIKES (REUTERS)",
    "RUSSIAN DRONE ENTERS POLISH AIRSPACE (REUTERS)",
    "N. KOREA MAY SHUT SWISS OFFICE (KCNA)",
    "MURMANSK GOVERNOR HELD IN GRAFT CASE (REUTERS)",
    "SENATE PROBES VANCE-VITOL OIL DEAL (REUTERS)",
    "MEXICO NABS 'EL CHAPO ISIDRO' (REUTERS)",
    "US MAY TRAIN SYRIAN TROOPS (REUTERS)",
    "MOSCOW WARNS ESTONIA OF 'OPEN WAR' (REUTERS)",
    "TRUMP BLASTS NEWSOM OVER 548 COMMUTES (REUTERS)",
    "WFP: WARS HIT FOOD AID FOR 7.3M (REUTERS)",
    "HIT CARGO SHIP SPARTA II DOCKS SAFE (REUTERS)",
    "MELENCHON GAINS IN FRENCH POLL (REUTERS)",
    "DENMARK COURT BACKS GHETTO EVICTIONS (REUTERS)",
    "UK: SPACEX CURBS 'DENTED TRUST' (REUTERS)",
    "OIL SLUMPS TO 3-MONTH LOW (REUTERS)",
    "HEDGE FUNDS IN WORST WEEK SINCE 2025 (REUTERS)",
    "AMAZON LAUNCHES KUIPER SATELLITES (SPACE.COM)",
    "AUSTRALIA: COP FALLOUT; HANSON TEST (REUTERS)",
    "MOSCOW HONOURS SECRET POLICE FOUNDER (REUTERS)",
]

TIMELINE = [
    ("00:00", "IRAN VOWS TO FIGHT BLOCKADE"),
    ("01:00", "COP31 FALLOUT: PACIFIC DESPAIR"),
    ("02:00", "INDONESIA: SEARCH FOR 34 MISSING"),
    ("06:00", "NATO TO SEND AWACS TO POLAND"),
    ("09:00", "EU UNVEILS 22ND SANCTIONS PACKAGE"),
    ("14:00", "TRUMP PAUSES IOWA BLAST"),
]

NUMBERS = [
    ("34", "STORIES"), ("14", "TANKERS AT KHARG"), ("24", "DEAD IN FIRE"),
    ("$15BN", "IRAN CASH FLAGGED"), ("548", "COMMUTED"),
    ("74 LASHES", "SINGER FLOGGED"),
]

REGIONS = [("EUROPE", 12, BLUE), ("AMERICAS", 8, RED), ("MIDDLE EAST", 4, AMBER),
           ("GLOBAL", 4, GREY), ("ASIA", 3, GREEN), ("AFRICA", 2, ORANGE),
           ("OCEANIA", 1, TEAL)]

def draw_chip(cv, x, y, tag):
    word, col = VERACITY[tag]
    cv.fill_rect(x, y, 16, 16, col)
    draw_text_c(cv, x + 8, y + 8, tag, F(SANS_B, 11), WHITE)


def build():
    cv = CV(W, H, PAPER)

    # ---- masthead 0..100 ----
    cv.fill_rect(0, 0, W, 100, NAVY)
    draw_text(cv, 16, 8, 'THE DAY IN WORLD NEWS', F(SANS_B, 14), CREAM)
    draw_text(cv, W - 16, 8, '34 STORIES \u2022 7 REGIONS \u2022 ONE DAY',
              F(SANS_B, 14), GOLD, align='r')
    msize = 48
    while F(SERIF_B, msize).getlength('Tuesday 24 November 2026') > 960 and msize > 36:
        msize -= 2
    draw_text(cv, W / 2, 25, 'Tuesday 24 November 2026', F(SERIF_B, msize),
              CREAM, align='c')
    ticker = 'Top: ' + ' \u2022 '.join(sentence_case(h['headline']) for h in HEROES)
    draw_text(cv, W / 2, 83, ticker, F(SANS, 13), (200, 210, 225), align='c')

    # ---- multicolour stripe 100..106 ----
    stripe_cols = [RED, GOLD, GREEN, BLUE, ORANGE, TEAL]
    for i, c in enumerate(stripe_cols):
        cv.fill_rect(i * W // 6, 100, W // 6 + 1, 6, c)

    # ---- UTC timeline strip 106..176 ----
    cv.fill_rect(0, 106, W, 70, CREAM)
    draw_text(cv, 16, 109, 'TUESDAY 24 NOVEMBER - AS THE DAY UNFOLDED (UTC)',
              F(SANS_B, 13), NAVY)
    cv.line(16, 130, W - 16, 130, NAVY, 2)
    col_w = (W - 32) / 6
    for i, (t, label) in enumerate(TIMELINE):
        cx = 16 + i * col_w
        cv.circle(int(cx + 8), 130, 5, RED)
        draw_text(cv, cx, 134, t, F(SANS_B, 12), RED)
        lines = wrap_text(title_case(label), F(SANS, 11), col_w - 12)
        assert len(lines) <= 2, ('timeline', label, lines)
        for j, ln in enumerate(lines[:2]):
            draw_text(cv, cx, 149 + j * 13, ln, F(SANS, 11), INK)

    # ---- 6 big numbers 176..226 (gold divider + BY THE NUMBERS tab) ----
    cv.fill_rect(0, 176, W, 50, PAPER)
    cv.fill_rect(0, 176, W, 3, GOLD)
    cv.fill_rect(12, 175, 156, 12, PAPER)
    draw_text(cv, 16, 176, 'BY THE NUMBERS', F(SANS_B, 9), GREY)
    for i, (num, label) in enumerate(NUMBERS):
        cx = 16 + i * col_w
        draw_text(cv, cx, 188, num, F(SANS_B, 22), RED)
        draw_text(cv, cx, 214, title_case(label), F(SANS, 10), INK)

    # ---- region bar 226..242 ----
    cv.fill_rect(0, 226, W, 16, PAPER)
    reg_text = 'Regions: ' + ' \u2022 '.join(
        '%s %d' % (title_case(n), v) for n, v, _ in REGIONS)
    draw_text(cv, W / 2, 227, reg_text, F(SANS, 11), NAVY, align='c')
    bx = 8
    total = sum(v for _, v, _ in REGIONS)
    for _, v, col in REGIONS:
        seg = int(1008 * v / total)
        cv.fill_rect(bx, 240, seg, 2, col)
        bx += seg

    # ---- 3 hero panels 242..432 ----
    hx = [8, 346, 684]
    for k, hero in enumerate(HEROES):
        x = hx[k]
        y = 242
        w = 332
        cv.rect(x, y, w, 190, NAVY, 2)
        SCENES[hero['scene']](cv, x + 2, y + 2, w - 4, 86)
        # kicker strip over art bottom
        cv.fill_rect(x + 2, y + 72, w - 4, 16, NAVY)
        draw_text(cv, x + 8, y + 74,
                  '%s \u2022 %s \u2022 %s' % (hero['num'], hero['city'], hero['region']),
                  F(SANS_B, 13), CREAM)
        # veracity chip top-right of art
        word, col = VERACITY[hero['tag']]
        cf = F(SANS_B, 11)
        cw = int(text_w(word, cf)) + 12
        cv.fill_rect(x + w - cw - 6, y + 6, cw, 16, col)
        draw_text(cv, x + w - cw, y + 8, word, cf, WHITE)
        # red banner = headline
        cv.fill_rect(x + 2, y + 88, w - 4, 52, RED)
        lines = wrap_text(title_case(hero['headline']), F(SANS_B, 21), w - 20)
        assert len(lines) <= 2, ('hero headline', hero['headline'], lines)
        for j, ln in enumerate(lines[:2]):
            draw_text(cv, x + 10, y + 90 + j * 25, ln, F(SANS_B, 21), WHITE)
        # deck
        dlines = wrap_text(sentence_case(hero['deck']), F(SANS, 14), w - 16)
        assert len(dlines) <= 2, ('hero deck', hero['deck'], dlines)
        for j, ln in enumerate(dlines[:2]):
            draw_text(cv, x + 8, y + 144 + j * 17, ln, F(SANS, 14), INK)
        # source (y+174: ink bottom 425, border rows 430-431 -> 4px margin)
        draw_text(cv, x + 8, y + 174, hero['source'], F(SANS, 10), GREY)

    # ---- 10 small panels, 2 rows of 5 (y 436 / 566, h 124) ----
    pw, gap = 196, 7
    for row in range(2):
        for col_i in range(5):
            p = SMALL[row * 5 + col_i]
            x = 8 + col_i * (pw + gap)
            y = 436 + row * 130
            cv.rect(x, y, pw, 124, NAVY, 1)
            SCENES[p['scene']](cv, x + 1, y + 1, pw - 2, 30)
            draw_chip(cv, x + pw - 18, y + 3, p['tag'])
            draw_text(cv, x + 6, y + 33, '%s \u2022 %s' % (p['num'], p['city']),
                      F(SANS_B, 12), NAVY)
            hlines = wrap_text(title_case(p['headline']), F(SANS_B, 15), pw - 12)
            assert len(hlines) <= 2, ('headline', p['headline'], hlines)
            for j, ln in enumerate(hlines[:2]):
                draw_text(cv, x + 6, y + 49 + j * 18, ln, F(SANS_B, 15), INK)
            dlines = wrap_text(sentence_case(p['deck']), F(SANS, 11), pw - 12)
            assert len(dlines) <= 2, ('deck', p['deck'], dlines)
            for j, ln in enumerate(dlines[:2]):
                draw_text(cv, x + 6, y + 85 + j * 13, ln, F(SANS, 11), INK)
            # source (y+110: ink bottom 555, border row 559 -> 3px margin)
            draw_text(cv, x + 6, y + 110, p['source'], F(SANS, 10), GREY)

    # ---- map + ALSO ON 692..950 ----
    cv.fill_rect(0, 692, W, 258, CREAM)
    draw_text(cv, 16, 696, 'WHERE IT HAPPENED', F(SANS_B, 13), NAVY)
    draw_text(cv, 438, 696, 'ALSO ON - 14 TO 34', F(SANS_B, 13), NAVY)
    # map box
    mx0, my0, mx1, my1 = 8, 720, 430, 940
    cv.fill_rect(mx0, my0, mx1 - mx0, my1 - my0, SEA)
    cv.rect(mx0, my0, mx1 - mx0, my1 - my0, NAVY, 1)

    def ll2xy(lon, lat):
        fx = (lon + 180.0) / 360.0
        fy = (85.0 - lat) / 145.0
        return (mx0 + fx * (mx1 - mx0), my0 + fy * (my1 - my0))

    for poly in CONTINENTS.values():
        pts = [ll2xy(lon, lat) for lon, lat in poly]
        cv.polygon(pts, OLIVE)
    # sea labels
    for label, lon, lat in (('ATLANTIC', -32, 8), ('PACIFIC', -152, -2),
                            ('INDIAN OCEAN', 88, -28)):
        lx, ly = ll2xy(lon, lat)
        draw_text(cv, lx, ly, label, F(SANS, 10), (90, 120, 150), align='c')
    # pins 1..13
    for num, lon, lat, dx, dy in PINS:
        px, py = ll2xy(lon, lat)
        px += dx
        py += dy
        cv.circle(int(px), int(py), 9, RED)
        cv.circle(int(px), int(py), 9, WHITE, fill=False)
        draw_text_c(cv, int(px), int(py), str(num), F(SANS_B, 11), WHITE)

    # ALSO ON two columns x 11 rows, one line per item
    col_xs = [438, 732]
    col_ws = [284, 284]
    for idx, item in enumerate(ALSO_ON):
        num = 14 + idx
        ci = idx // 11
        ri = idx % 11
        cx = col_xs[ci]
        cy = 712 + ri * 22
        full = '%d %s' % (num, title_case(item))
        lines = wrap_text(full, F(SANS, 9.5), col_ws[ci])
        assert len(lines) == 1, ('also-on', full, lines)
        draw_text(cv, cx, cy, lines[0], F(SANS, 9.5), INK)

    # ---- DATE CHECK 950..998: black text on pale peach, red border ----
    cv.fill_rect(8, 950, W - 16, 48, DC_BG)
    cv.rect(8, 950, W - 16, 48, RED, 2)
    dc = [
        ('Date Check \u2014 Wires read up to 15:00 UTC, Tue 24 Nov 2026. '
         'Every story here was reported, or still developing, on 24 Nov '
         'in at least one time zone.', True),
        ('Left out: Voyager 1 (20 Nov) \u2022 Bitcoin low (21 Nov) \u2022 '
         'Nigeria boat toll (22 Nov).', False),
        ('Not yet: Iran\u2019s 14 tankers test the blockade \u2022 '
         'EU package needs unanimity.', False),
    ]
    for j, (ln, bold) in enumerate(dc):
        fnt = F(SANS_B, 11) if bold else F(SANS, 11)
        assert fnt.getlength(ln) <= 992, ('date-check', ln)
        draw_text(cv, 16, 953 + j * 13, ln, fnt, INK)

    # ---- footer 998..1024 ----
    draw_text(cv, W / 2, 1000,
              'Every story here was reported on Tue 24 Nov 2026 in at least one time zone.',
              F(SANS, 10), INK, align='c')
    draw_text(cv, W / 2, 1012,
              'Sources: Reuters, AP, BBC, CNN, Guardian, AFP, Space.com \u2022 Original drawings.',
              F(SANS, 10), GREY, align='c')
    return cv


def save_png(cv, path):
    cv.img.save(path, "PNG")
    return os.path.getsize(path)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    cv = build()
    size = save_png(cv, os.path.join(here, 'entry.png'))
    print('entry.png bytes:', size)
    print('limit 1048576, ok:', size <= 1048576)
