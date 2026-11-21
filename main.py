"""THE WORLD TODAY - front page for Saturday 21 November 2026.

Draws the whole front page from scratch with the Python standard library
only (os / struct / zlib) and writes /output/entry.png. No network, no
external files, no PIL. Deterministic: the same run always writes the same
bytes.

Design: classic broadsheet. Big masthead, date line, one hero story with a
flat night-sky illustration of Kyiv under fire, six secondary stories with
small icons, and a 28-story index in four columns. 35 stories, 7 regions,
every story with a source and a confidence mark. All type is set in a
5x7 pixel face I drew for this page, scaled up so the smallest headline
is never below scale 2.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (245, 239, 224)
INK = (22, 22, 22)
RED = (163, 22, 33)
BLUE = (29, 78, 137)
TEAL = (14, 124, 107)
ORANGE = (179, 84, 30)
GREEN = (46, 125, 50)
PURPLE = (106, 61, 154)
GOLD = (141, 110, 0)
GREY = (110, 110, 104)
LIGHT_GREY = (200, 196, 184)
NIGHT = (20, 38, 62)
NIGHT2 = (12, 18, 32)
MOON = (242, 225, 170)
FIRE = (255, 122, 26)
SMOKE = (138, 143, 152)
WHITE = (250, 250, 248)

REGION_COLORS = {
    "EUROPE": BLUE,
    "ASIA": TEAL,
    "MIDDLE EAST": ORANGE,
    "AMERICAS": GREEN,
    "AFRICA": PURPLE,
    "OCEANIA": GOLD,
    "SCIENCE": RED,
}

# ------------------------------------------------------------- 5x7 face
# Each glyph is 7 rows of 5 bits, top row first. Drawn by hand for this
# page: one face, capitals, digits and the punctuation the page needs.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}


def text_width(text, scale):
    """Width in pixels of text at a scale (1px tracking between glyphs)."""
    return len(text) * (6 * scale) - scale


def wrap_text(text, max_chars):
    """Greedy word wrap to lines of at most max_chars characters."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur = cur + " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with square brush of side `thick`."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=False):
        if fill:
            for yy in range(cy - r, cy + r + 1):
                dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
                self.hline(cx - dx, yy, 2 * dx + 1, color)
            return
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            for px, py in (
                (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                (cx + y, cy - x), (cx - y, cy - x),
            ):
                self.set(px, py, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def text(self, x, y, s, scale, color):
        """Draw text with the 5x7 face. Unknown chars render as space."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(
                            cx + col * scale, y + row * scale,
                            scale, scale, color,
                        )
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        x = cx - text_width(s, scale) // 2
        return self.text(x, y, s, scale, color)


# ------------------------------------------------------------------- png
def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.px[start:start + stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------------- the news
# All 35 stories were first reported on Saturday 21 November 2026 (or
# happened that day). Sources are the outlets that reported each one.
# Confidence: HIGH = confirmed by the outlet named; REPORTED = the figure
# is the outlet's reported figure, still developing.
HERO = {
    "region": "EUROPE",
    "headline": "RUSSIA HITS KYIV WITH 400 DRONES AND 110 MISSILES; TWO LAND IN POLAND",
    "dek": "EIGHT KILLED IN THE CAPITAL AS THREE BRIDGES ARE HIT. NATO SCRAMBLES "
           "JETS AFTER A MISSILE IS FOUND IN POLAND, AND WARSAW CALLS IT A "
           "DELIBERATE PROVOCATION.",
    "source": "KYIV POST",
    "conf": "HIGH",
}

SECONDARY = [
    {
        "region": "SCIENCE", "icon": "globe",
        "headline": "COP31 TALKS IN OVERTIME OVER FOSSIL FUELS",
        "source": "POLLAR", "conf": "HIGH",
    },
    {
        "region": "ASIA", "icon": "gavel",
        "headline": "ICJ: MYANMAR GUILTY OF ROHINGYA GENOCIDE",
        "source": "REUTERS", "conf": "HIGH",
    },
    {
        "region": "AMERICAS", "icon": "chart",
        "headline": "AI SELL-OFF PUSHES S&P 500 AND DOW INTO CORRECTION",
        "source": "WSJ", "conf": "HIGH",
    },
    {
        "region": "ASIA", "icon": "flags",
        "headline": "TRUMP, XI AND PUTIN MEET IN SHENZHEN FOR FIRST TIME",
        "source": "KOREA TIMES", "conf": "HIGH",
    },
    {
        "region": "MIDDLE EAST", "icon": "shield",
        "headline": "SAUDI INTERCEPTS 3 HOUTHI MISSILES AIMED AT RIYADH",
        "source": "GMA NEWS", "conf": "HIGH",
    },
    {
        "region": "AMERICAS", "icon": "quake",
        "headline": "6.9 QUAKE SHAKES CENTRAL PERU; NO DEATHS REPORTED",
        "source": "USGS", "conf": "HIGH",
    },
]

# 28 more stories, four columns of seven.
INDEX = [
    ("SCIENCE", "BEPICOLOMBO ENTERS MERCURY ORBIT", "ESA", "HIGH"),
    ("ASIA", "CYCLONE AKVAN HITS ODISHA COAST", "AP", "HIGH"),
    ("MIDDLE EAST", "ISRAELI STRIKES KILL SIX IN GAZA", "AP", "REPORTED"),
    ("EUROPE", "DENMARK EXPELS RUSSIAN ATTACHE", "ANADOLU", "HIGH"),
    ("AMERICAS", "BOLSONARO IN HOSPITAL IN BRAZIL", "AP", "HIGH"),
    ("AFRICA", "SOUTH AFRICA MOURNS MLAMBO-NGCUKA", "AP", "HIGH"),
    ("EUROPE", "AUSTRIA MINISTRY WEBSITE HACKED", "AP", "HIGH"),
    ("AMERICAS", "US PRESSES KYIV ON JANUARY DEAL", "FINANCIAL TIMES", "REPORTED"),
    ("AMERICAS", "KUSHNER FLOATS NATO-FOR-LAND SWAP", "WSJ", "REPORTED"),
    ("EUROPE", "UK SENDS UKRAINE 1,000 DRONES", "REUTERS", "HIGH"),
    ("AMERICAS", "US CLEARS 900,000 AI CHIPS TO CHINA", "HOUSE PANEL", "HIGH"),
    ("AMERICAS", "ANTHROPIC SHARES FALL 9% AFTER IPO", "WSJ", "HIGH"),
    ("EUROPE", "ROME MARCHES IN GENERAL STRIKE", "AP", "HIGH"),
    ("SCIENCE", "CANCER PILL ERASES TUMOURS IN 1 IN 12", "REUTERS", "REPORTED"),
    ("OCEANIA", "AUSTRALIA, NZ CONDEMN RUSSIA WAR", "ANADOLU", "HIGH"),
    ("EUROPE", "UKRAINE BLOCKS RUSSIA AT COP31", "UKRINFORM", "HIGH"),
    ("EUROPE", "KINDERGARTEN HIT IN ZAPORIZHZHIA", "KYIV POST", "REPORTED"),
    ("MIDDLE EAST", "HORMUZ TENSIONS RISE AS IRAN WARNS", "REUTERS", "REPORTED"),
    ("MIDDLE EAST", "TRUMP: IRAN WANTS DEAL, NO TERMS", "REUTERS", "REPORTED"),
    ("EUROPE", "GERMANY: KYIV FACES HARSH WINTER", "REUTERS", "HIGH"),
    ("AMERICAS", "MOSCOW ENERGY REACHES BRAZIL", "REUTERS", "REPORTED"),
    ("AMERICAS", "HUMANS MUST RULE AI WEAPONS: US", "REUTERS", "HIGH"),
    ("EUROPE", "UK MPS DEMAND NEW AI LAW", "REUTERS", "HIGH"),
    ("AMERICAS", "INSIDER-TRADING SUSPECT IN US COURT", "AP", "HIGH"),
    ("SCIENCE", "COP31 DRAFT DROPS FOSSIL FUELS", "POLLAR", "HIGH"),
    ("AMERICAS", "NVIDIA TURMOIL DEEPENS AI ROUT", "WSJ", "REPORTED"),
    ("EUROPE", "EU SUMMONS RUSSIAN ENVOY", "REUTERS", "HIGH"),
    ("EUROPE", "ABU DHABI TALKS STALL OVER NATO", "TASS", "REPORTED"),
]


# ------------------------------------------------------------- hero art
def draw_hero_art(c, x, y, w, h):
    """Flat night sky over Kyiv: skyline, missile arcs, smoke, moon."""
    c.rect(x, y, w, h, NIGHT)
    # stars
    for sx, sy in (
        (30, 12), (90, 26), (150, 8), (210, 30), (300, 10), (380, 22),
        (470, 8), (560, 28), (640, 12), (720, 24), (800, 8), (880, 26),
        (940, 12), (60, 44), (250, 48), (520, 44), (760, 46), (920, 44),
    ):
        c.set(x + sx, y + sy, WHITE)
        c.set(x + sx + 1, y + sy, WHITE)
    # moon
    c.circle(x + 900, y + 34, 22, MOON, fill=True)
    c.circle(x + 892, y + 30, 18, NIGHT, fill=True)
    # missile arcs (orange trails with bright heads)
    c.line(x + 120, y + h - 6, x + 300, y + 18, FIRE, 3)
    c.circle(x + 300, y + 18, 4, WHITE, fill=True)
    c.line(x + 420, y + h - 6, x + 560, y + 30, FIRE, 3)
    c.circle(x + 560, y + 30, 4, WHITE, fill=True)
    c.line(x + 700, y + h - 6, x + 830, y + 12, FIRE, 3)
    c.circle(x + 830, y + 12, 4, WHITE, fill=True)
    # smoke columns rising from the city
    for sx, sy, sr in ((180, 78, 12), (186, 62, 15), (500, 82, 11),
                       (506, 66, 14), (760, 80, 12), (766, 64, 15)):
        c.circle(x + sx, y + sy, sr, SMOKE, fill=True)
    # skyline silhouette with lit windows
    base = y + h - 34
    buildings = [
        (0, 34, 46), (46, 26, 60), (106, 40, 38), (144, 30, 52),
        (196, 44, 34), (230, 28, 58), (288, 36, 44), (332, 26, 62),
        (394, 42, 36), (430, 30, 54), (484, 38, 42), (526, 26, 60),
        (586, 44, 34), (620, 30, 56), (676, 38, 40), (716, 28, 58),
        (774, 42, 36), (810, 30, 52), (862, 36, 44), (906, 28, 74),
    ]
    for bx, bw, bh in buildings:
        c.rect(x + bx, base - bh, bw, bh + 34, NIGHT2)
    # one church dome on the skyline
    c.circle(x + 660, base - 58, 12, NIGHT2, fill=True)
    c.rect(x + 659, base - 72, 2, 12, NIGHT2)
    # lit windows: small warm dots in a fixed pattern
    for wx in range(14, w - 8, 18):
        for wy in (base - 18, base - 30, base - 8):
            if (wx * 7 + wy * 3) % 11 < 4:
                c.rect(x + wx, wy, 3, 4, MOON)
    c.hline(x, y + h - 2, w, INK, 2)


# -------------------------------------------------------------- icons
def draw_icon(c, x, y, size, kind, color):
    """Small flat pictograms for the six secondary stories."""
    if kind == "globe":
        c.circle(x + size // 2, y + size // 2, size // 2 - 2, color)
        c.rect(x + 2, y + size // 2 - 1, size - 4, 2, color)
        c.rect(x + size // 2 - 1, y + 2, 2, size - 4, color)
    elif kind == "gavel":
        c.line(x + 6, y + size - 8, x + size - 6, y + 8, color, 4)
        c.rect(x + 4, y + 6, size - 14, 8, color)
        c.hline(x + 4, y + size - 6, size - 8, color, 3)
    elif kind == "chart":
        c.line(x + 4, y + size - 8, x + size - 4, y + 8, color, 3)
        c.line(x + size - 12, y + 8, x + size - 4, y + 8, color, 3)
        c.line(x + size - 4, y + 8, x + size - 4, y + 16, color, 3)
        c.vline(x + 4, y + 6, size - 12, color, 2)
    elif kind == "flags":
        for i, fx in enumerate((6, size // 2, size - 10)):
            c.vline(x + fx, y + 8, size - 14, color, 2)
            c.rect(x + fx + 2, y + 8, 10, 7, color if i != 1 else RED)
    elif kind == "shield":
        cx = x + size // 2
        pts = [(cx - 12, y + 6), (cx + 12, y + 6), (cx + 12, y + size // 2),
               (cx, y + size - 4), (cx - 12, y + size // 2)]
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            c.line(x0, y0, x1, y1, color, 3)
        c.text(x + size // 2 - 3, y + size // 2 - 3, "3", 1, color)
    elif kind == "quake":
        c.line(x + 4, y + size // 2, x + 12, y + size // 2 - 8, color, 3)
        c.line(x + 12, y + size // 2 - 8, x + 20, y + size // 2 + 8, color, 3)
        c.line(x + 20, y + size // 2 + 8, x + 28, y + size // 2 - 8, color, 3)
        c.line(x + 28, y + size // 2 - 8, x + size - 4, y + size // 2, color, 3)


# ------------------------------------------------------------- the page
def draw_page():
    c = Canvas(W, H, PAPER)
    M = 22                      # side margin
    CW = W - 2 * M              # 980 content width
    X1 = M + CW                 # 1002 right edge

    # outer frame
    c.hline(12, 12, 1000, INK, 3)
    c.hline(12, 1009, 1000, INK, 3)
    c.vline(12, 12, 1000, INK, 3)
    c.vline(1009, 12, 1000, INK, 3)

    # masthead
    mast = "THE WORLD TODAY"
    c.text_center(W // 2, 28, mast, 9, INK)
    c.hline(M, 98, CW, RED, 3)

    # date line
    c.text(M, 106, "SATURDAY, 21 NOVEMBER 2026", 2, INK)
    c.text_center(W // 2, 106, "35 STORIES - 7 REGIONS", 2, INK)
    right = "PRICE $2.00"
    c.text(X1 - text_width(right, 2), 106, right, 2, INK)
    c.hline(M, 128, CW, INK, 4)
    c.hline(M, 134, CW, INK, 1)

    # hero illustration
    draw_hero_art(c, M, 140, CW, 116)

    # hero headline (scale 3, two lines max)
    hl = wrap_text(HERO["headline"], 51)
    assert len(hl) <= 2, "hero headline wraps to %d lines" % len(hl)
    y = 264
    for line in hl:
        c.text(M, y, line, 3, INK)
        y += 26

    # hero dek (scale 2, two lines max)
    dk = wrap_text(HERO["dek"], 81)
    assert len(dk) <= 2, "hero dek wraps to %d lines" % len(dk)
    y = 322
    for line in dk:
        c.text(M, y, line, 2, INK)
        y += 17

    # hero source + confidence
    src = "SOURCES: KYIV POST / REUTERS / TIMES OF INDIA - CONFIDENCE: HIGH"
    c.text(M, 362, src, 1, GREY)
    tag = HERO["region"]
    c.rect(X1 - text_width(tag, 1) - 14, 360, 10, 10,
           REGION_COLORS[tag])
    c.text(X1 - text_width(tag, 1), 361, tag, 1,
           REGION_COLORS[tag])
    c.hline(M, 382, CW, INK, 2)

    # secondary stories: 2 rows x 3 columns
    col_w = 318
    for i, s in enumerate(SECONDARY):
        col = i % 3
        row = i // 3
        x = M + col * (col_w + 12)
        y = 390 + row * 96
        draw_icon(c, x, y, 36, s["icon"], REGION_COLORS[s["region"]])
        lines = wrap_text(s["headline"], 26)
        assert len(lines) <= 2, "secondary %d wraps to %d" % (i, len(lines))
        ly = y + 42
        for line in lines:
            c.text(x, ly, line, 2, INK)
            ly += 18
        meta = "%s - %s - %s" % (s["region"], s["source"], s["conf"])
        c.text(x, y + 80, meta, 1, GREY)
    c.hline(M, 584, CW, INK, 2)

    # index header
    c.text(M, 592, "THE DAY IN FULL", 2, INK)
    ih = "28 MORE STORIES - EVERY ONE SOURCED"
    c.text(X1 - text_width(ih, 1), 596, ih, 1, GREY)

    # index: 4 columns x 7 rows, column-major
    icol_w = 237
    for i, (region, headline, source, conf) in enumerate(INDEX):
        col = i // 7
        row = i % 7
        x = M + col * (icol_w + 10)
        y = 622 + row * 53
        color = REGION_COLORS[region]
        c.rect(x, y + 1, 9, 9, color)
        c.text(x + 13, y, "%s - %s" % (region, source), 1, color)
        lines = wrap_text(headline, 19)
        assert len(lines) <= 2, "index %d wraps to %d" % (i, len(lines))
        ly = y + 11
        for line in lines:
            c.text(x, ly, line, 2, INK)
            ly += 16
        c.text(x, y + 43, "CONFIDENCE: %s" % conf, 1, GREY)

    # footer
    foot = "THE WORLD TODAY - SATURDAY 21 NOVEMBER 2026 - EVERY STORY SOURCED"
    c.text_center(W // 2, 1000, foot, 1, GREY)
    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(outdir, exist_ok=True)
    canvas = draw_page()
    path = os.path.join(outdir, "entry.png")
    size = write_png(canvas, path)
    import hashlib
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (path, size, sha))


if __name__ == "__main__":
    main()
