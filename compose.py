#!/usr/bin/env python3
"""Compose "The World in One Day" — a dense broadsheet front page that sums
up Thursday 19 November 2026 in a single 1024x1024 image.

The page follows the broadsheet meta: a masthead, a numbers band, a region
band, three hero stories, ten more numbered feature cards, a dot-matrix
world map with numbered pins for the feature stories, a UTC timeline, 27
one-line briefs, and five boxes none of the other front pages carry — SPORT,
WEATHER WATCH, MARKETS, QUOTE OF THE DAY and a FRIDAY PREVIEW — above a red
DATE CHECK box in the footer. 44 stories in all.

Three of the feature stories reuse the editorial illustration panels in
assets/ (summit, ICJ, COP31); the GTA VI hero art (a purple Vice City
skyline) and the Anthropic hero art (a green market chart) are drawn here
with Pillow, as is every word on the page.

Run:  python3 compose.py     -> writes entry.png next to this file.
The output is deterministic: two runs produce byte-identical files.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "entry.png")

# --- palette ---------------------------------------------------------------
CREAM = (0xF7, 0xF1, 0xE3)
PAPER = (0xFF, 0xFC, 0xF4)
NAVY = (0x14, 0x26, 0x4A)
CRIMSON = (0xB3, 0x20, 0x2C)
GOLD = (0xD9, 0xA4, 0x41)
INK = (0x22, 0x22, 0x22)

CANVAS = 1024
MARGIN = 12
WIDTH = CANVAS - 2 * MARGIN  # 1000 px of content
MAX_BYTES = 1_048_576  # 1 MiB

# --- fonts -------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF_B = os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")
SERIF_R = os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")
SANS_B = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
SANS_R = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# --- text helpers --------------------------------------------------------------

def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_width):
    """Greedy word wrap; returns the list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(draw, text, path, start_size, max_width, min_size=7):
    """Largest font, starting at start_size, that keeps text on one line."""
    size = start_size
    while size > min_size:
        font = F(path, size)
        if text_w(draw, text, font) <= max_width:
            return font
        size -= 1
    return F(path, size)


def block(draw, x, y, text, path, size, max_width, max_lines, fill,
          line_h=None, align="left"):
    """Draw wrapped text, shrinking the font until it fits max_lines.
    Returns the height consumed."""
    while size > 6:
        font = F(path, size)
        lines = wrap(draw, text, font, max_width)
        if len(lines) <= max_lines:
            break
        size -= 1
    font = F(path, size)
    lines = wrap(draw, text, font, max_width)
    lh = line_h if line_h else round(size * 1.22)
    for i, line in enumerate(lines):
        if align == "center":
            lx = x + (max_width - text_w(draw, line, font)) / 2
        else:
            lx = x
        draw.text((lx, y + i * lh), line, font=font, fill=fill)
    return len(lines) * lh


def centered(draw, cx, cy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, font=font,
              fill=fill)


def badge(draw, cx, cy, number, r=9):
    """A crimson circle with a white story number. On the map (r=8) it gets
    a cream halo ring so the pin stays legible over the dense dot field."""
    if r <= 8:
        draw.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2],
                     fill=CREAM)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CRIMSON)
    font = F(SANS_B, 10 if number < 10 else 9)
    centered(draw, cx, cy, str(number), font, (255, 255, 255))


def panel(name, width, height):
    """Load an illustration panel, center-cropped to exactly width x height."""
    img = Image.open(os.path.join(ASSETS, name)).convert("RGB")
    return ImageOps.fit(img, (width, height), Image.LANCZOS)


# --- drawn hero art -------------------------------------------------------------

def vice_city_art(w, h):
    """A purple Vice City skyline silhouette with a low sun, drawn in code."""
    img = Image.new("RGB", (w, h), (58, 20, 110))
    d = ImageDraw.Draw(img)
    top, bot = (58, 20, 110), (216, 54, 128)
    for yy in range(h):
        t = yy / max(h - 1, 1)
        d.line([(0, yy), (w, yy)],
               fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    # low sun
    sx, sy, sr = int(w * 0.70), int(h * 0.58), int(h * 0.34)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 176, 66))
    d.ellipse([sx - sr + 4, sy - sr + 4, sx + sr - 4, sy + sr - 4],
              fill=(255, 205, 92))
    # skyline: (x fraction, width fraction, height fraction), back row first
    back = [(0.00, 0.09, 0.52), (0.10, 0.07, 0.66), (0.19, 0.10, 0.44),
            (0.31, 0.06, 0.58), (0.40, 0.09, 0.40), (0.52, 0.07, 0.62),
            (0.62, 0.10, 0.46), (0.75, 0.06, 0.56), (0.84, 0.08, 0.42),
            (0.94, 0.06, 0.50)]
    front = [(0.03, 0.08, 0.34), (0.16, 0.06, 0.42), (0.27, 0.09, 0.30),
             (0.44, 0.07, 0.38), (0.58, 0.06, 0.32), (0.70, 0.09, 0.40),
             (0.86, 0.07, 0.30), (0.96, 0.05, 0.36)]
    base = h - 8
    for row, colour in ((back, (38, 14, 74)), (front, (16, 6, 38))):
        for xf, wf, hf in row:
            x0, bw, bh = int(xf * w), int(wf * w), int(hf * h)
            d.rectangle([x0, base - bh, x0 + bw, base], fill=colour)
            for wy in range(base - bh + 4, base - 3, 7):
                for wx in range(x0 + 3, x0 + bw - 2, 6):
                    if (wx * 7 + wy * 13) % 5 < 2:
                        d.rectangle([wx, wy, wx + 2, wy + 3], fill=GOLD)
    # sea strip with light dashes
    d.rectangle([0, base, w, h], fill=(18, 12, 52))
    for xx in range(4, w - 8, 17):
        d.line([(xx, h - 4), (xx + 8, h - 4)], fill=(240, 120, 190), width=1)
    return img


def market_chart_art(w, h):
    """A green candlestick/line chart for the Anthropic IPO hero."""
    img = Image.new("RGB", (w, h), (7, 43, 32))
    d = ImageDraw.Draw(img)
    for gx in range(0, w, 32):  # faint grid
        d.line([(gx, 0), (gx, h)], fill=(16, 66, 50))
    for gy in range(0, h, 16):
        d.line([(0, gy), (w, gy)], fill=(16, 66, 50))
    candles = [  # (open, close) as fractions of height, trending up
        (0.78, 0.70), (0.72, 0.63), (0.66, 0.68), (0.64, 0.55),
        (0.57, 0.47), (0.50, 0.54), (0.48, 0.38), (0.40, 0.30),
        (0.33, 0.36), (0.30, 0.20),
    ]
    step = w / (len(candles) + 1)
    pts = []
    for i, (o, c) in enumerate(candles):
        cx = int(step * (i + 1))
        y_o, y_c = int(o * h), int(c * h)
        lo, hi = min(y_o, y_c), max(y_o, y_c)
        colour = (74, 222, 128) if y_c < y_o else (248, 113, 113)
        d.line([(cx, hi + 5), (cx, lo - 5)], fill=colour, width=1)
        d.rectangle([cx - 4, lo, cx + 4, max(hi, lo + 2)], fill=colour)
        pts.append((cx, y_c))
    d.line(pts, fill=(167, 243, 208), width=2)
    # label sits right of the story badge the page draws over the corner
    d.text((38, 5), "ANT $83", font=F(SANS_B, 16), fill=(134, 239, 172))
    d.text((38, 25), "NASDAQ DEBUT", font=F(SANS_B, 8), fill=(110, 190, 150))
    return img


# --- the world map ---------------------------------------------------------------
# Land spans per row of a 92 x 19 dot grid (roughly equirectangular).

MAP_SPANS = {
    0: [(8, 10), (14, 16), (19, 21), (30, 35), (58, 60), (66, 68), (74, 76),
        (82, 84)],
    1: [(6, 22), (28, 37), (55, 90)],
    2: [(5, 25), (30, 36), (48, 52), (53, 91)],
    3: [(6, 27), (33, 35), (46, 57), (58, 91)],
    4: [(7, 28), (45, 58), (59, 90)],
    5: [(8, 29), (44, 56), (58, 88)],
    6: [(9, 28), (43, 46), (47, 55), (57, 81), (82, 84)],
    7: [(10, 27), (44, 54), (56, 80), (83, 85)],
    8: [(12, 25), (26, 29), (43, 58), (59, 80)],
    9: [(14, 22), (27, 31), (42, 60), (61, 79)],
    10: [(27, 33), (41, 61), (63, 78), (80, 84)],
    11: [(28, 35), (42, 60), (66, 76), (79, 86)],
    12: [(29, 36), (43, 59), (70, 74), (78, 85)],
    13: [(30, 36), (44, 57), (76, 86)],
    14: [(30, 35), (45, 55), (77, 85)],
    15: [(31, 34), (46, 52), (78, 84)],
    16: [(31, 34), (47, 50), (89, 91)],
    17: [(32, 33), (90, 91)],
    18: [(32, 33)],
}
MAP_COLS, MAP_ROWS = 92, 19

# (column, row) of each feature story on the grid, plus a pixel nudge so
# crowded pins (the Gulf cluster, the Black Sea cluster) never overlap.
PINS = {
    1: (75, 8, 0, 0),        # Shenzhen
    2: (26, 8, 0, 0),        # GTA VI — Miami / Vice City
    3: (27, 6, 6, -4),       # Anthropic IPO — New York
    4: (47, 4, 0, 0),        # ICJ — The Hague
    5: (54, 6, 2, 6),        # COP31 — Antalya
    6: (68, 8, 0, 0),        # Cyclone Akvan — Odisha
    7: (55, 5, 10, -4),      # Kerch Bridge
    8: (60, 8, -6, -6),      # Strait of Hormuz
    9: (59, 8, -2, 8),       # Riyadh
    10: (56, 7, 4, 7),       # Gaza
    11: (78, 6, 0, 0),       # Suneung — Seoul
    12: (54, 4, -10, -3),    # Kyiv
    13: (60, 8, 14, 10),     # Abu Dhabi talks
}


def draw_map(page, draw, x, y, w, h):
    pitch_x = w / MAP_COLS
    pitch_y = h / MAP_ROWS
    for row, spans in MAP_SPANS.items():
        cy = y + (row + 0.5) * pitch_y
        for c0, c1 in spans:
            for col in range(c0, c1 + 1):
                cx = x + (col + 0.5) * pitch_x
                draw.ellipse([cx - 2.3, cy - 1.5, cx + 2.3, cy + 1.5],
                             fill=NAVY)
    for number, (col, row, ox, oy) in PINS.items():
        cx = x + (col + 0.5) * pitch_x + ox
        cy = y + (row + 0.5) * pitch_y + oy
        badge(draw, cx, cy, number, r=8)


# --- content -----------------------------------------------------------------------

NUMBERS = [
    ("$81.3bn", "Anthropic's record IPO raise"),
    ("15.9m", "GTA VI pre-orders"),
    ("200,000", "evacuated ahead of Cyclone Akvan"),
    ("$120bn", "COP31 adaptation fund proposed"),
    ("730,000", "Rohingya fled Myanmar"),
    ("551,864", "students sit South Korea's Suneung exam"),
]

HEROES = [
    ("SHENZHEN SUMMIT", "summit",
     "Trump, Xi & Putin hold their first trilateral summit on the APEC "
     "sidelines — and announce a 'peace declaration' after 90 minutes."),
    ("GTA VI LAUNCH", "vice",
     "Rockstar's GTA VI goes on sale at midnight — 15.9 million pre-orders "
     "and a 99/100 Metacritic score."),
    ("ANTHROPIC'S RECORD IPO", "chart",
     "Anthropic raises a record $81.3bn in its Nasdaq debut, valuing the "
     "AI lab at about $1.5 trillion."),
]

FEATURES = [
    (4, "WORLD COURT RULES ON ROHINGYA", "icj",
     "The ICJ rules Myanmar committed state-sponsored genocide in The "
     "Gambia's case — the first ruling of its kind."),
    (5, "COP31 DEADLOCKED IN ANTALYA", "cop31",
     "Climate talks stall in their final 48 hours over fossil fuels and "
     "the proposed $120bn adaptation fund."),
    (6, "CYCLONE AKVAN", None,
     "200,000 people evacuated across Odisha and Andhra Pradesh as Akvan "
     "strengthens; landfall expected Friday."),
    (7, "CRIMEAN BRIDGE STRUCK AGAIN", None,
     "Ukraine hits the Kerch Bridge for the third time in a week; rail "
     "traffic across the strait halted."),
    (8, "TANKERS BURN IN HORMUZ", None,
     "Three tankers reported on fire in the Strait of Hormuz as Iran "
     "widens attacks on Kuwait and Bahrain."),
    (9, "HOUTHI MISSILE REACHES RIYADH", None,
     "Debris from a Houthi missile damages the PIF Tower in Riyadh; the "
     "coalition intercepts another launch."),
    (10, "ISRAEL ENTERS CENTRAL GAZA", None,
     "Israeli forces launch a ground operation near Nuseirat, the first "
     "beyond the 'Yellow Line' since the ceasefire."),
    (11, "SUNEUNG DAY IN SEOUL", None,
     "551,864 students sit South Korea's make-or-break university exam; "
     "flights paused, markets open late."),
    (12, "KYIV: NOT WITHOUT US", None,
     "Zelenskyy insists no peace decisions about Ukraine can be made "
     "without Ukraine at the table."),
    (13, "ABU DHABI TALKS STALL", None,
     "Ukraine-Russia-US talks end without a breakthrough as strikes black "
     "out eastern Ukraine's power grid."),
]

BRIEFS = [
    (14, "Odesa strike kills 4, injures 13"),
    (15, "EU proposes €45bn Ukraine loan"),
    (16, "EU delays methane rules under US pressure"),
    (17, "Cyberattack reported at the European Commission"),
    (18, "Prince Harry open to service against Russia"),
    (19, "Japan's Takaichi: Taiwan position unchanged"),
    (20, "Seoul renews dialogue call to Pyongyang"),
    (21, "IAEA: North Korea expanding uranium enrichment"),
    (22, "Yunus ancestral home torched in Bangladesh"),
    (23, "Indonesia passes asset-forfeiture law"),
    (24, "US-China AI chip curbs stay in place"),
    (25, "Flooding rains swamp Florida coast"),
    (26, "Earth's 'missing billion years' of rock explained"),
    (27, "Mélenchon rallies supporters in Paris"),
    (28, "Record cocaine haul seized near Benghazi"),
    (29, "Paro Nacional strike shuts Bogotá"),
    (30, "Australia unemployment rises"),
    (31, "Russian charged with spying on Silicon Valley defence staff"),
    (32, "Court fight over Venezuelan migrant protections"),
    (33, "Democrats nominate Jeffries for Speaker, 251-11"),
    (34, "Musk regrets midterm campaign spending"),
    (35, "Terror charges over Illinois temple plot"),
    (36, "US and Venezuela restore military ties"),
    (37, "Pastor convicted over Moïse assassination"),
    (38, "Ebola response struggles in DR Congo"),
    (39, "RSF commander defects in Sudan"),
    (40, "Migrant boat sinks off Senegal, dozens missing"),
]

BOXES = [
    ("SPORT",
     "Duckett's 133 seals an ODI series win for England · GTA VI midnight "
     "queues wrap around stores in New York and London."),
    ("WEATHER WATCH",
     "Cyclone Akvan: 130 km/h winds, Odisha landfall Friday · Florida: "
     "flood warnings on the southeast coast · Fiji: state of disaster "
     "declared in El Niño drought."),
    ("MARKETS",
     "ANT debuts at $83 after record $81.3bn raise · Fed minutes: rates "
     "held, further hikes expected · Deutsche Bank probed after 15m-file "
     "leak."),
    ("QUOTE OF THE DAY",
     "\"We'll see what happens.\" — Donald Trump, on the Iran war after "
     "1 January."),
    ("FRIDAY PREVIEW",
     "Akvan makes landfall · Anthropic's first full trading day · COP31's "
     "final text due in Antalya."),
]

TIMELINE = (
    "00:00 GTA VI on sale in New Zealand · MORNING Shenzhen summit opens · "
    "09:00 World Court ruling, The Hague · ALL DAY Kerch Bridge closed · "
    "14:30 Anthropic rings the Nasdaq bell · EVENING COP31 endgame in Antalya"
)


# --- page assembly -------------------------------------------------------------------

def main():
    page = Image.new("RGB", (CANVAS, CANVAS), CREAM)
    draw = ImageDraw.Draw(page)
    x0 = MARGIN
    x1 = CANVAS - MARGIN

    # 1 — masthead ------------------------------------------------------------
    title_font = fit_one_line(draw, "THE WORLD IN ONE DAY", SERIF_B, 58, WIDTH)
    centered(draw, CANVAS / 2, 34, "THE WORLD IN ONE DAY", title_font, NAVY)
    centered(draw, CANVAS / 2, 76, "THURSDAY · 19 NOVEMBER 2026",
             F(SANS_B, 17), CRIMSON)
    draw.rectangle([x0, 90, x1, 92], fill=GOLD)
    draw.rectangle([x0, 96, x1, 118], fill=CRIMSON)
    strap = ("44 STORIES · 7 REGIONS · EVERY STORY FIRST REPORTED ON "
             "THURSDAY · DATE-CHECKED")
    centered(draw, CANVAS / 2, 107, strap,
             fit_one_line(draw, strap, SANS_B, 14, WIDTH - 20), (255, 255, 255))

    # 2 — numbers band ---------------------------------------------------------
    y = 124
    gap = 6
    bw = (WIDTH - 5 * gap) // 6
    for i, (num, label) in enumerate(NUMBERS):
        bx = x0 + i * (bw + gap)
        draw.rectangle([bx, y, bx + bw, y + 44], fill=NAVY)
        centered(draw, bx + bw / 2, y + 13, num,
                 fit_one_line(draw, num, SERIF_B, 19, bw - 10), GOLD)
        block(draw, bx + 5, y + 24, label, SANS_R, 9, bw - 10, 2,
              (240, 235, 220), line_h=10, align="center")

    # 3 — region band ------------------------------------------------------------
    y = 174
    draw.line([(x0, y), (x1, y)], fill=NAVY, width=1)
    regions = ("ASIA-PACIFIC 11 · EUROPE 9 · THE AMERICAS 10 · MIDDLE EAST 5 "
               "· AFRICA 4 · OCEANIA 2 · WORLD 3")
    centered(draw, CANVAS / 2, y + 11, regions,
             fit_one_line(draw, regions, SANS_B, 13, WIDTH), NAVY)
    draw.line([(x0, y + 22), (x1, y + 22)], fill=NAVY, width=1)

    # 4 — hero row -----------------------------------------------------------------
    y = 204
    card_w = (WIDTH - 2 * 8) // 3
    card_h = 172
    for i, (headline, art, body) in enumerate(HEROES):
        cx = x0 + i * (card_w + 8)
        draw.rectangle([cx, y, cx + card_w, y + card_h], fill=PAPER,
                       outline=NAVY, width=1)
        if art == "summit":
            img = panel("summit.png", card_w - 2, 78)
        elif art == "vice":
            img = vice_city_art(card_w - 2, 78)
        else:
            img = market_chart_art(card_w - 2, 78)
        page.paste(img, (cx + 1, y + 1))
        draw = ImageDraw.Draw(page)
        badge(draw, cx + 13, y + 13, i + 1, r=9)
        block(draw, cx + 8, y + 86, headline, SERIF_B, 14, card_w - 16, 1,
              NAVY, line_h=16)
        block(draw, cx + 8, y + 104, body, SANS_R, 10, card_w - 16, 4,
              INK, line_h=13)

    # 5 — feature cards 4–13 ---------------------------------------------------------
    y = 384
    cols, rows = 5, 2
    fw = (WIDTH - (cols - 1) * 6) // cols
    fh = 100
    for idx, (num, headline, thumb, summary) in enumerate(FEATURES):
        cx = x0 + (idx % cols) * (fw + 6)
        cy = y + (idx // cols) * (fh + 6)
        draw.rectangle([cx, cy, cx + fw, cy + fh], fill=PAPER, outline=NAVY,
                       width=1)
        ty = cy + 5
        if thumb:
            img = panel(f"{thumb}.png", fw - 10, 20)
            page.paste(img, (cx + 5, ty))
            draw = ImageDraw.Draw(page)
            ty += 24
        badge(draw, cx + 11, ty + 7, num, r=8)
        block(draw, cx + 23, ty, headline, SERIF_B, 11, fw - 28, 2, NAVY,
              line_h=13)
        block(draw, cx + 6, ty + 28, summary, SANS_R, 9, fw - 12, 4, INK,
              line_h=11)

    # 6 — map box -----------------------------------------------------------------------
    y = 596
    draw.rectangle([x0, y, x1, y + 126], outline=NAVY, width=1)
    draw.rectangle([x0, y, x1, y + 18], fill=NAVY)
    draw.text((x0 + 8, y + 4), "WHERE IT HAPPENED", font=F(SANS_B, 11),
              fill=(255, 255, 255))
    note = "red pins 1–13 = the feature stories above"
    draw.text((x1 - 8 - text_w(draw, note, F(SANS_R, 9)), y + 5), note,
              font=F(SANS_R, 9), fill=(210, 215, 230))
    draw_map(page, draw, x0 + 6, y + 22, WIDTH - 12, 100)

    # 7 — timeline strip ------------------------------------------------------------------
    y = 730
    draw.text((x0, y), "THE DAY BY THE CLOCK — UTC", font=F(SANS_B, 12),
              fill=CRIMSON)
    block(draw, x0, y + 16, TIMELINE, SANS_R, 10, WIDTH, 2, INK, line_h=13)

    # 8 — briefs 14–40 ----------------------------------------------------------------------
    y = 776
    col_w = (WIDTH - 2 * 12) // 3
    columns = [BRIEFS[0:9], BRIEFS[9:18], BRIEFS[18:27]]
    size = 10
    while size > 8:  # shrink until the tallest column fits the space
        font = F(SANS_R, size)
        worst = 0
        for col in columns:
            hgt = 0
            for num, text in col:
                nw = text_w(draw, f"{num} ", F(SANS_B, size))
                hgt += len(wrap(draw, text, font, col_w - nw - 2)) * (size + 2) + 2
            worst = max(worst, hgt)
        if worst <= 118:
            break
        size -= 1
    font = F(SANS_R, size)
    lh = size + 2
    for ci, col in enumerate(columns):
        cx = x0 + ci * (col_w + 12)
        cy = y
        for num, text in col:
            ntxt = f"{num}"
            nw = text_w(draw, ntxt, F(SANS_B, size))
            draw.text((cx, cy), ntxt, font=F(SANS_B, size), fill=CRIMSON)
            lines = wrap(draw, text, font, col_w - nw - 5)
            for li, line in enumerate(lines):
                draw.text((cx + nw + 5, cy + li * lh), line, font=font,
                          fill=INK)
            cy += len(lines) * lh + 2

    # 9 — differentiator boxes ---------------------------------------------------------------
    y = 902
    bw2 = (WIDTH - 4 * 6) // 5
    for i, (name, body) in enumerate(BOXES):
        bx = x0 + i * (bw2 + 6)
        draw.rectangle([bx, y, bx + bw2, y + 64], fill=PAPER, outline=NAVY,
                       width=1)
        draw.rectangle([bx, y, bx + bw2, y + 15], fill=NAVY)
        draw.text((bx + 6, y + 3), name, font=F(SANS_B, 9),
                  fill=(255, 255, 255))
        block(draw, bx + 6, y + 19, body, SANS_R, 9, bw2 - 12, 4, INK,
              line_h=11)

    # 10 — footer: red DATE CHECK box + colophon line -------------------------------------------
    y = 974
    draw.rectangle([x0, y, x1, y + 24], fill=CRIMSON)
    check = ("DATE CHECK — first reported Wednesday 18 Nov and deliberately "
             "left out: the $190.4m Van Gogh sale and Voyager 1 reaching "
             "one light-day.")
    centered(draw, CANVAS / 2, y + 12, check,
             fit_one_line(draw, check, SANS_B, 11, WIDTH - 16),
             (255, 255, 255))
    foot = ("44 stories · drawn and set in one page · sources: wire and "
            "daily briefs of Thursday 19 November 2026")
    centered(draw, CANVAS / 2, 1012, foot,
             fit_one_line(draw, foot, SANS_R, 10, WIDTH), NAVY)

    # --- save, keeping the file at or under 1 MiB ----------------------------------------------
    page.save(OUT, "PNG", optimize=True)
    if os.path.getsize(OUT) > MAX_BYTES:
        page.quantize(colors=256, method=Image.MEDIANCUT).save(
            OUT, "PNG", optimize=True)

    final = Image.open(OUT)
    print(f"entry.png: {os.path.getsize(OUT)} bytes, "
          f"{final.size[0]}x{final.size[1]}")
    if final.size != (1024, 1024) or os.path.getsize(OUT) > MAX_BYTES:
        sys.exit("entry.png failed the size/dimension limits")


if __name__ == "__main__":
    main()
