#!/usr/bin/env python3
"""draw.py - renders entry.png for make.fun news-image-20261124.
'Tuesday 24 November 2026 - The World in One Day'.
Pure Python 3.13 standard library only (zlib, struct, os).
Flat 2D vector front page, 1024x1024, code-drawn.
Run: python3 draw.py  -> writes entry.png next to this file.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ----
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

# ---- 5x7 bitmap font (uppercase, digits, punctuation) ----
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

# bullet glyph (U+2022) drawn as a small square block
FONT['\u2022'] = ("00000", "00000", "01100", "01100", "01100", "00000", "00000")
# multiplication sign
FONT['\u00d7'] = ("00000", "10001", "01010", "00100", "01010", "10001", "00000")


def norm(text):
    """Normalise text to the font charset (all caps)."""
    out = []
    for ch in text:
        if ch in ('\u2019', '\u2018'):
            out.append("'")
        elif ch in ('\u201c', '\u201d'):
            out.append('"')
        elif ch in ('\u2013', '\u2014'):
            out.append('-')
        elif ch == '\u2026':
            out.append('.')
        else:
            out.append(ch.upper())
    return ''.join(out)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, int(x))
        y0 = max(0, int(y))
        x1 = min(self.w, int(x + w))
        y1 = min(self.h, int(y + h))
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x, y, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        r = int(r)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(xx, yy, c)

    def triangle(self, pts, c):
        # scanline fill of a triangle
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for yy in range(int(min(ys)), int(max(ys)) + 1):
            xs_at = []
            for i in range(3):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % 3]
                if y0 == y1:
                    continue
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs_at.append(x0 + t * (x1 - x0))
            if len(xs_at) >= 2:
                for xx in range(int(min(xs_at)), int(max(xs_at)) + 1):
                    self.set(xx, yy, c)

    def polygon(self, pts, c):
        # scanline fill of a simple polygon
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for yy in range(int(min(ys)), int(max(ys)) + 1):
            xs_at = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs_at.append(x0 + t * (x1 - x0))
            xs_at.sort()
            for k in range(0, len(xs_at) - 1, 2):
                for xx in range(int(xs_at[k]), int(xs_at[k + 1]) + 1):
                    self.set(xx, yy, c)


def text_w(text, scale):
    """Width in px of text at given scale (6 units per char)."""
    return len(norm(text)) * 6 * scale


def draw_text(cv, x, y, text, scale, color, align='l'):
    """Draw text; y is the top. Returns width drawn."""
    text = norm(text)
    w = len(text) * 6 * scale
    if align == 'c':
        x = x - w / 2
    elif align == 'r':
        x = x - w
    x = int(round(x))
    y = int(round(y))
    for ci, ch in enumerate(text):
        glyph = FONT.get(ch, FONT[' '])
        gx = x + ci * 6 * scale
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    px0 = int(round(gx + col * scale))
                    py0 = int(round(y + row * scale))
                    px1 = int(round(gx + (col + 1) * scale))
                    py1 = int(round(y + (row + 1) * scale))
                    cv.fill_rect(px0, py0, max(1, px1 - px0), max(1, py1 - py0), color)
    return w


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w px."""
    text = norm(text)
    words = text.split(' ')
    lines = []
    cur = ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---- flat vector scenes (one per panel) ----
# Each scene draws inside rect (x, y, w, h).

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
        import math
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
    # radar rings
    cx, cy = x + int(w * 0.5), y + int(h * 0.55)
    for r in (30, 20, 10):
        cv.circle(cx, cy, r, (120, 160, 210), fill=False)
    cv.line(cx, cy, cx + 26, cy - 18, GREEN, 2)
    cv.circle(cx + 26, cy - 18, 4, GREEN)
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
    ex, ey = x + int(w * 0.72), y + int(h * 0.3)
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
    draw_text(cv, tx, ty - 2, "!", 1.2, NAVY, align='c')


def scene_eu(cv, x, y, w, h):
    import math
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
    draw_text(cv, x + w / 2, y + int(h * 0.55), "$", 2.2, RED, align='c')


def scene_anthropic(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (240, 226, 200))
    base = y + int(h * 0.85)
    vals = [0.3, 0.45, 0.4, 0.6, 0.55, 0.8]
    bw = int(w / (len(vals) + 1))
    for i, v in enumerate(vals):
        bh = int(h * 0.65 * v)
        cv.fill_rect(x + int(w * 0.08) + i * bw, base - bh, int(bw * 0.62), bh,
                     ORANGE if i == len(vals) - 1 else (200, 150, 90))
    draw_text(cv, x + w / 2, y + int(h * 0.06), "AI", 2.4, NAVY, align='c')


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

# ---- world map ----
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
         deck='3 MISSILES HIT POLAND', source='REUTERS', tag='C'),
    dict(num='05', city='BENGHAZI', scene='ship',
         headline='UKRAINE SINKS RUSSIAN SHIP',
         deck='SUNK BY DRONES IN BENGHAZI PORT', source='REUTERS', tag='O'),
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
    "IRAN FLOG SINGER AHMADI: 74 LASHES (REUTERS)",
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
    ("00:00", "N. KOREA WEIGHS SWISS SHUTDOWN"),
    ("01:00", "COP31 FALLOUT: PACIFIC DESPAIR"),
    ("02:00", "INDONESIA: SEARCH FOR 34 MISSING"),
    ("06:00", "NATO TO SEND AWACS TO POLAND"),
    ("09:00", "EU UNVEILS 22ND SANCTIONS PACKAGE"),
    ("14:00", "TRUMP PAUSES IOWA BLAST"),
]

NUMBERS = [
    ("34", "STORIES"), ("14", "TANKERS AT KHARG"), ("24", "DEAD IN FIRE"),
    ("$15BN", "IRAN CASH FLAGGED"), ("548", "COMMUTED"), ("3 MIN", "SEOUL WARNING"),
]

REGIONS = [("EUROPE", 12, BLUE), ("AMERICAS", 8, RED), ("MIDDLE EAST", 4, AMBER),
           ("GLOBAL", 4, GREY), ("ASIA", 3, GREEN), ("AFRICA", 2, ORANGE),
           ("OCEANIA", 1, TEAL)]


def draw_chip(cv, x, y, tag, big=False):
    word, col = VERACITY[tag]
    if big:
        w = text_w(word, 1.5) + 10
        cv.fill_rect(x, y, w, 16, col)
        draw_text(cv, x + 5, y + 3, word, 1.5, WHITE)
        return w
    cv.fill_rect(x, y, 14, 14, col)
    draw_text(cv, x + 4, y + 2, tag, 1.5, WHITE)
    return 14


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead 0..100 ----
    cv.fill_rect(0, 0, W, 100, NAVY)
    draw_text(cv, 16, 10, 'THE DAY IN WORLD NEWS', 2, CREAM)
    draw_text(cv, W - 16, 10, '34 STORIES \u2022 7 REGIONS \u2022 ONE DAY', 2, GOLD, align='r')
    draw_text(cv, W / 2, 32, 'TUESDAY 24 NOVEMBER 2026', 6, CREAM, align='c')
    draw_text(cv, W / 2, 80,
              'TOP: IRAN VOWS TO FIGHT BLOCKADE \u2022 COP31 ENDS WITH NO DEAL \u2022 HUANG BACK AT NVIDIA',
              2, (200, 210, 225), align='c')

    # ---- multicolour stripe 100..106 ----
    stripe_cols = [RED, GOLD, GREEN, BLUE, ORANGE, TEAL]
    for i, c in enumerate(stripe_cols):
        cv.fill_rect(i * W // 6, 100, W // 6 + 1, 6, c)

    # ---- UTC timeline strip 106..178 ----
    cv.fill_rect(0, 106, W, 72, CREAM)
    draw_text(cv, 16, 110, 'TUESDAY 24 NOVEMBER - AS THE DAY UNFOLDED (UTC)', 2, NAVY)
    cv.line(16, 134, W - 16, 134, NAVY, 2)
    col_w = (W - 32) / 6
    for i, (t, label) in enumerate(TIMELINE):
        cx = 16 + i * col_w
        cv.circle(int(cx + 8), 134, 5, RED)
        draw_text(cv, cx, 140, t, 2, RED)
        lines = wrap_text(label, 1.5, col_w - 12)
        for j, ln in enumerate(lines[:3]):
            draw_text(cv, cx, 156 + j * 11, ln, 1.5, INK)

    # ---- 6 big numbers 178..224 ----
    cv.fill_rect(0, 178, W, 46, PAPER)
    for i, (num, label) in enumerate(NUMBERS):
        cx = 16 + i * col_w
        draw_text(cv, cx, 182, num, 4, RED)
        draw_text(cv, cx, 212, label, 1.5, INK)

    # ---- region bar 224..242 ----
    cv.fill_rect(0, 224, W, 18, PAPER)
    reg_text = 'REGIONS: ' + ' \u2022 '.join('%s %d' % (n, v) for n, v, _ in REGIONS)
    draw_text(cv, W / 2, 226, reg_text, 1.5, NAVY, align='c')
    bx = 8
    total = sum(v for _, v, _ in REGIONS)
    for _, v, col in REGIONS:
        seg = int(1008 * v / total)
        cv.fill_rect(bx, 238, seg, 4, col)
        bx += seg

    # ---- 3 hero panels 242..432 ----
    hx = [8, 346, 684]
    for k, hero in enumerate(HEROES):
        x = hx[k]
        y = 242
        w = 332
        cv.rect(x, y, w, 190, NAVY, 2)
        SCENES[hero['scene']](cv, x + 2, y + 2, w - 4, 88)
        # kicker strip over art bottom
        cv.fill_rect(x + 2, y + 74, w - 4, 16, NAVY)
        draw_text(cv, x + 8, y + 77,
                  '%s \u2022 %s \u2022 %s' % (hero['num'], hero['city'], hero['region']),
                  1.6, CREAM)
        # veracity chip top-right of art
        word, col = VERACITY[hero['tag']]
        cw = text_w(word, 1.5) + 10
        cv.fill_rect(x + w - cw - 6, y + 6, cw, 16, col)
        draw_text(cv, x + w - cw - 1, y + 9, word, 1.5, WHITE)
        # red banner = headline
        cv.fill_rect(x + 2, y + 90, w - 4, 52, RED)
        lines = wrap_text(hero['headline'], 3, w - 20)
        for j, ln in enumerate(lines[:2]):
            draw_text(cv, x + 10, y + 94 + j * 22, ln, 3, WHITE)
        # deck
        dlines = wrap_text(hero['deck'], 2, w - 16)
        for j, ln in enumerate(dlines[:2]):
            draw_text(cv, x + 8, y + 146 + j * 13, ln, 2, INK)
        # source
        draw_text(cv, x + 8, y + 178, hero['source'], 1.6, GREY)

    # ---- 10 small panels, 2 rows of 5 ----
    pw, gap = 196, 7
    for row in range(2):
        for col_i in range(5):
            p = SMALL[row * 5 + col_i]
            x = 8 + col_i * (pw + gap)
            y = 440 + row * 128
            cv.rect(x, y, pw, 122, NAVY, 1)
            SCENES[p['scene']](cv, x + 1, y + 1, pw - 2, 36)
            draw_chip(cv, x + pw - 17, y + 4, p['tag'])
            draw_text(cv, x + 6, y + 40, '%s \u2022 %s' % (p['num'], p['city']), 2, NAVY)
            hlines = wrap_text(p['headline'], 2, pw - 12)
            for j, ln in enumerate(hlines[:2]):
                draw_text(cv, x + 6, y + 54 + j * 14, ln, 2, INK)
            dlines = wrap_text(p['deck'], 1.9, pw - 12)
            for j, ln in enumerate(dlines[:2]):
                draw_text(cv, x + 6, y + 84 + j * 13, ln, 1.9, INK)
            draw_text(cv, x + 6, y + 112, p['source'], 1.5, GREY)

    # ---- map + ALSO ON 692..950 ----
    cv.fill_rect(0, 692, W, 258, CREAM)
    draw_text(cv, 16, 696, 'WHERE IT HAPPENED', 2, NAVY)
    draw_text(cv, 438, 696, 'ALSO ON - 14 TO 34', 2, NAVY)
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
        draw_text(cv, lx, ly, label, 1.4, (90, 120, 150), align='c')
    # pins 1..13
    for num, lon, lat, dx, dy in PINS:
        px, py = ll2xy(lon, lat)
        px += dx
        py += dy
        cv.circle(int(px), int(py), 9, RED)
        cv.circle(int(px), int(py), 9, WHITE, fill=False)
        lab = str(num)
        draw_text(cv, int(px), int(py) - 5, lab, 1.5, WHITE, align='c')

    # ALSO ON two columns x 11 rows (2 lines max per item, scale 1.5)
    col_xs = [438, 732]
    col_ws = [284, 284]
    for idx, item in enumerate(ALSO_ON):
        num = 14 + idx
        ci = idx // 11
        ri = idx % 11
        cx = col_xs[ci]
        cy = 708 + ri * 22
        full = '%d %s' % (num, item)
        lines = wrap_text(full, 1.5, col_ws[ci])
        for j, ln in enumerate(lines[:2]):
            draw_text(cv, cx, cy + j * 11, ln, 1.5, INK)

    # ---- DATE CHECK 950..998 ----
    cv.fill_rect(8, 950, W - 16, 48, (255, 238, 238))
    cv.rect(8, 950, W - 16, 48, RED, 2)
    dc = [
        'DATE CHECK - WIRES READ UP TO 15:00 UTC, TUE 24 NOV 2026.',
        'EVERY STORY HERE WAS REPORTED, OR STILL DEVELOPING, ON 24 NOV IN AT LEAST ONE TIME ZONE.',
        "LEFT OUT: VOYAGER 1 (20 NOV) \u2022 BITCOIN LOW (21 NOV) \u2022 NIGERIA BOAT TOLL (22 NOV).",
        "NOT YET: IRAN'S 14 TANKERS TEST THE BLOCKADE \u2022 EU PACKAGE NEEDS UNANIMITY.",
    ]
    for j, ln in enumerate(dc):
        draw_text(cv, 16, 953 + j * 11, ln, 1.5, RED_DK)

    # ---- footer 998..1024 ----
    draw_text(cv, W / 2, 999,
              'EVERY STORY HERE WAS REPORTED ON TUE 24 NOV 2026 IN AT LEAST ONE TIME ZONE.',
              1.5, INK, align='c')
    draw_text(cv, W / 2, 1012,
              'SOURCES: REUTERS, AP, BBC, CNN, GUARDIAN, AFP, SPACE.COM \u2022 ORIGINAL DRAWINGS.',
              1.5, GREY, align='c')
    return cv


def save_png(cv, path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += cv.px[yy * W * 3:(yy + 1) * W * 3]

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        c += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
        return c

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 6))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    cv = build()
    size = save_png(cv, os.path.join(here, 'entry.png'))
    print('entry.png bytes:', size)
    print('limit 1048576, ok:', size <= 1048576)
