#!/usr/bin/env python3
"""Compose "The World in One Day" — a dense broadsheet front page that sums
up Thursday 19 November 2026 in a single 1024x1024 image.

Third edition of the page. The first edition carried four stories dated to
Thursday that had in fact broken earlier in the week; this edition strikes
them out, names them in a CORRECTIONS & CLARIFICATIONS strip, and rebuilds
the page from the full day's wire record now that Thursday is history:
three hero stories, ten more numbered features, a PICTURE OF THE DAY panel,
36 one-line briefs, a dot-matrix world map with numbered pins, a UTC
timeline, six numbers, and the five boxes the other front pages do not
carry — SPORT, WEATHER WATCH, MARKETS, QUOTE OF THE DAY and a FRIDAY
PREVIEW — above a red DATE CHECK footer. 50 stories in all.

Three of the feature stories and the picture panel reuse the editorial
illustration panels in assets/ (summit, ICJ, COP31, Hormuz); the GTA VI
hero art (a purple Vice City skyline) and the Anthropic hero art (a green
market chart) are drawn here with Pillow, as is every word on the page.

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
    d.text((38, 5), "ANT $97.17", font=F(SANS_B, 16), fill=(134, 239, 172))
    d.text((38, 25), "CLOSE +17%", font=F(SANS_B, 8), fill=(110, 190, 150))
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

# (column, row) of each hero/feature story on the grid, plus a pixel nudge so
# crowded pins (the Gulf cluster, the Black Sea cluster) never overlap.
PINS = {
    1: (75, 8, 0, 0),        # Shenzhen
    2: (26, 8, 0, 0),        # GTA VI — Miami / Vice City
    3: (27, 6, 6, -4),       # Anthropic IPO — New York
    4: (47, 4, -6, 2),       # ICJ — The Hague
    5: (54, 6, 2, 6),        # COP31 — Antalya
    6: (68, 8, 0, 0),        # Cyclone Akvan — Odisha
    7: (55, 5, 10, -4),      # Kerch Bridge
    8: (60, 8, -6, -6),      # Strait of Hormuz
    9: (59, 8, -2, 8),       # Riyadh
    10: (56, 7, 4, 7),       # Gaza
    11: (78, 6, 0, 0),       # Han retrial — Seoul
    12: (48, 3, 8, -6),      # Arctic pact — Copenhagen
    13: (83, 14, 0, 0),      # Jobs shock — Canberra
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
    ("9–6", "the World Court's genocide verdict"),
    ("$81.3bn", "raised in Anthropic's record IPO"),
    ("$1.84bn", "GTA VI's first-day sales, estimated"),
    ("204,070", "listed for evacuation in Odisha"),
    ("109–0", "Denmark's Arctic pact vote"),
    ("4.9%", "Australia's jobless rate, a 5-year high"),
]

HEROES = [
    ("SHENZHEN SUMMIT", "summit",
     "Trump, Xi and Putin meet for 90 minutes at Kylin Villa and sign a "
     "four-point peace declaration — nuclear-risk talks, energy, UN "
     "reform — that never mentions Ukraine."),
    ("GTA VI LAUNCH", "vice",
     "Thirteen years on, GTA VI rolls out from New Zealand at midnight: "
     "a record 99 on Metacritic, and an estimated $1.84bn of sales on "
     "day one."),
    ("ANTHROPIC'S RECORD IPO", "chart",
     "ANT opens at $111.50 and closes at $97.17, up 17% on the $83 price "
     "set the night before — the biggest IPO ever, $107.3bn raised in "
     "all."),
]

FEATURES = [
    (4, "WORLD COURT: GENOCIDE RULING", "icj",
     "By 9 votes to 6 the Court finds Myanmar committed genocide "
     "against the Rohingya — a first — and orders reparations."),
    (5, "COP31 DRAFT DROPS FOSSIL FUELS", "cop31",
     "The slimmed Thursday draft drops the $120bn adaptation target "
     "and all fossil-fuel language; final text due Friday."),
    (6, "CYCLONE AKVAN NEARS LANDFALL", None,
     "204,070 people are listed for evacuation in Odisha as Akvan "
     "bears down on the Andhra coast; landfall is due Friday at noon."),
    (7, "CRIMEAN BRIDGE STRUCK AGAIN", None,
     "Ukraine strikes the Kerch Bridge for the third time in a week; "
     "Russia halts traffic while the damage is assessed."),
    (8, "TANKERS HIT MINES IN HORMUZ", None,
     "Iran's Guards say two tankers struck naval mines and are "
     "burning in the strait; US officials dispute Tehran's account."),
    (9, "HOUTHI MISSILES OVER RIYADH", None,
     "Saudi defences shoot down Houthi missiles over Riyadh; debris "
     "damages buildings in the capital, with no casualties reported."),
    (10, "ISRAEL ENDS GAZA TANK RAID", None,
     "Israel says its tank raid past the Yellow Line, begun on "
     "Wednesday, is over; Hamas calls the push a breach of the truce."),
    (11, "SEOUL: EX-PM HAN WINS RETRIAL", None,
     "South Korea's top court quashes part of Han Duck-soo's 15-year "
     "martial-law sentence and orders a retrial; he stays in detention."),
    (12, "DENMARK BACKS ARCTIC PACT", None,
     "Parliament votes 109–0 to ratify the Arctic security pact with "
     "the US and Greenland, clearing more American bases on the island."),
    (13, "AUSTRALIA'S JOBLESS HITS 4.9%", None,
     "Employment falls 43,500 in a shock print that takes another RBA "
     "hike off the table and sinks the dollar to a 2026 low."),
]

PICTURE = (
    14, "hormuz",
    "Fire on the water in the Strait of Hormuz (illustration). With "
    "mines reported in the shipping lanes, crude moving through the "
    "strait runs at about 8.5m barrels a day — half the pre-war flow.",
)

BRIEFS = [
    (15, "Odesa strike kills 4 and injures 13"),
    (16, "Zelenskyy: no talks on Ukraine without Ukraine"),
    (17, "Kyiv says it hit two oil refineries at Krasnodar"),
    (18, "EU delays its methane rules by two years"),
    (19, "Berlin charges an entrepreneur as a Russian informant"),
    (20, "French left splits over a Mélenchon pact"),
    (21, "Rome: author Corrado Augias dies at 91"),
    (22, "Two rivals to challenge FIFA's Infantino"),
    (23, "Inquiry: yacht Bayesian was vulnerable to wind"),
    (24, "APEC adopts the Shenzhen Outlook on trade and AI"),
    (25, "551,864 sit the Suneung exam; flights paused"),
    (26, "Jakarta passes its asset-seizure law after 18 years"),
    (27, "Awami League shutdown idles parts of Bangladesh"),
    (28, "Takaichi: Japan's Taiwan position is unchanged"),
    (29, "Seoul renews its dialogue call to Pyongyang"),
    (30, "India and Japan review their defence ties"),
    (31, "US pursues a $2bn Philippines loan package"),
    (32, "Carney sets out a China deal in Ottawa"),
    (33, "Paro Nacional strike shuts Bogotá"),
    (34, "Banxico minutes signal a long pause at 6.25%"),
    (35, "Floods shut South Florida schools again"),
    (36, "California braces for an atmospheric river"),
    (37, "Musk calls his midterm splurge 'pretty foolish'"),
    (38, "Houthi media report Saudi strikes on Sanaa"),
    (39, "Bapco refinery back on its feet in Bahrain"),
    (40, "Floods kill six in Kenya; hundreds displaced"),
    (41, "Somalia expels the UAE ambassador"),
    (42, "Sudan court sentences the absent RSF chief to death"),
    (43, "Cocaine and millions of pills seized near Benghazi"),
    (44, "Senegal: search resumes for a capsized boat's missing"),
    (45, "Pretoria holds the central bank rate at 7.25%"),
    (46, "Tonga declares a nationwide drought emergency"),
    (47, "Cyclone Xavier weakens to category 4"),
    (48, "Wellington court: pay-equity cuts broke the law"),
    (49, "A red giant star is seen eating a Sun-sized star"),
    (50, "IEA: Hormuz is history's worst energy-security threat"),
]

BOXES = [
    ("SPORT",
     "Jepchirchir banned 3 years for EPO; her Sydney title passes to "
     "Cheptai · Duckett's 133 seals England's ODI win."),
    ("WEATHER WATCH",
     "Akvan: winds to 145 km/h, landfall Friday noon · Tonga declares "
     "a drought emergency."),
    ("MARKETS",
     "ANT +17% at $97.17 on day one · Brent near $92 on the Hormuz "
     "reports · Aussie dollar at a 2026 low."),
    ("QUOTE OF THE DAY",
     "\"End your war, end it now.\" — Anthony Albanese to Vladimir "
     "Putin, at APEC."),
    ("FRIDAY PREVIEW",
     "Akvan makes landfall · COP31's final text lands in Antalya · "
     "GTA VI's first official sales tally."),
]

TIMELINE = (
    "00:00 GTA VI unlocks in New Zealand · 04:42 air-raid sirens sound "
    "in Riyadh · 09:00 the World Court reads its ruling · 16:48 "
    "Anthropic's first trade in New York · ALL DAY the Kerch Bridge "
    "stays shut · EVENING COP31's slimmed draft lands in Antalya"
)

CORRECTIONS = (
    "CORRECTIONS — our first edition mis-dated four stories: the EU's "
    "€45bn loan and the Jeffries vote (Wed), the Deutsche Bank files "
    "(Tue), the 'missing billion years' study (4 Nov)."
)

DATE_CHECK = (
    "DATE CHECK — first reported before Thursday and left out on "
    "purpose: the $190.4m Van Gogh sale (Wed) · Voyager 1's light-day "
    "(Wed) · the US–Venezuela military deal (Wed) · the IAEA's North "
    "Korea report (Wed) · Bolivia's El Niño decree (31 Oct)."
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
    strap = ("50 STORIES · 7 REGIONS · EVERY STORY FIRST REPORTED ON "
             "THURSDAY · DATE-CHECKED AND CORRECTED")
    centered(draw, CANVAS / 2, 107, strap,
             fit_one_line(draw, strap, SANS_B, 14, WIDTH - 20), (255, 255, 255))

    # 2 — numbers band ---------------------------------------------------------
    y = 124
    gap = 6
    bw = (WIDTH - 5 * gap) // 6
    for i, (num, label) in enumerate(NUMBERS):
        bx = x0 + i * (bw + gap)
        draw.rectangle([bx, y, bx + bw, y + 40], fill=NAVY)
        centered(draw, bx + bw / 2, y + 11, num,
                 fit_one_line(draw, num, SERIF_B, 18, bw - 10), GOLD)
        block(draw, bx + 5, y + 20, label, SANS_R, 8, bw - 10, 2,
              (240, 235, 220), line_h=9, align="center")

    # 3 — region band ------------------------------------------------------------
    y = 170
    draw.line([(x0, y), (x1, y)], fill=NAVY, width=1)
    regions = ("ASIA-PACIFIC 11 · EUROPE 13 · THE AMERICAS 7 · MIDDLE EAST 6 "
               "· AFRICA 6 · OCEANIA 4 · WORLD 3")
    centered(draw, CANVAS / 2, y + 9, regions,
             fit_one_line(draw, regions, SANS_B, 13, WIDTH), NAVY)
    draw.line([(x0, y + 20), (x1, y + 20)], fill=NAVY, width=1)

    # 4 — hero row -----------------------------------------------------------------
    y = 198
    card_w = (WIDTH - 2 * 8) // 3
    card_h = 152
    for i, (headline, art, body) in enumerate(HEROES):
        cx = x0 + i * (card_w + 8)
        draw.rectangle([cx, y, cx + card_w, y + card_h], fill=PAPER,
                       outline=NAVY, width=1)
        if art == "summit":
            img = panel("summit.png", card_w - 2, 66)
        elif art == "vice":
            img = vice_city_art(card_w - 2, 66)
        else:
            img = market_chart_art(card_w - 2, 66)
        page.paste(img, (cx + 1, y + 1))
        draw = ImageDraw.Draw(page)
        badge(draw, cx + 13, y + 13, i + 1, r=9)
        block(draw, cx + 8, y + 74, headline, SERIF_B, 14, card_w - 16, 1,
              NAVY, line_h=16)
        block(draw, cx + 8, y + 92, body, SANS_R, 10, card_w - 16, 4,
              INK, line_h=13)

    # 5 — feature cards 4–13 ---------------------------------------------------------
    y = 358
    cols, rows = 5, 2
    fw = (WIDTH - (cols - 1) * 6) // cols
    fh = 92
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
        block(draw, cx + 6, ty + 28, summary, SANS_R, 9, fw - 12,
              3 if thumb else 4, INK, line_h=11)

    # 6 — map box -----------------------------------------------------------------------
    y = 556
    draw.rectangle([x0, y, x1, y + 102], outline=NAVY, width=1)
    draw.rectangle([x0, y, x1, y + 18], fill=NAVY)
    draw.text((x0 + 8, y + 4), "WHERE IT HAPPENED", font=F(SANS_B, 11),
              fill=(255, 255, 255))
    note = "red pins 1–13 = the hero and feature stories above"
    draw.text((x1 - 8 - text_w(draw, note, F(SANS_R, 9)), y + 5), note,
              font=F(SANS_R, 9), fill=(210, 215, 230))
    draw_map(page, draw, x0 + 6, y + 22, WIDTH - 12, 76)

    # 7 — picture of the day (story 14) ---------------------------------------------------
    y = 666
    pnum, part, pcap = PICTURE
    draw.rectangle([x0, y, x1, y + 52], fill=PAPER, outline=NAVY, width=1)
    img = panel(f"{part}.png", 196, 50)
    page.paste(img, (x0 + 1, y + 1))
    draw = ImageDraw.Draw(page)
    badge(draw, x0 + 14, y + 14, pnum, r=9)
    draw.text((x0 + 206, y + 5), "PICTURE OF THE DAY", font=F(SERIF_B, 13),
              fill=NAVY)
    block(draw, x0 + 206, y + 23, pcap, SANS_R, 9, WIDTH - 214, 2, INK,
          line_h=11)

    # 8 — timeline strip ------------------------------------------------------------------
    y = 726
    draw.text((x0, y), "THE DAY BY THE CLOCK — UTC", font=F(SANS_B, 12),
              fill=CRIMSON)
    block(draw, x0, y + 16, TIMELINE, SANS_R, 10, WIDTH, 2, INK, line_h=12)

    # 9 — briefs 15–50 ----------------------------------------------------------------------
    y = 772
    col_w = (WIDTH - 3 * 12) // 4
    columns = [BRIEFS[i * 9:(i + 1) * 9] for i in range(4)]
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
        if worst <= 114:
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

    # 10 — differentiator boxes ---------------------------------------------------------------
    y = 890
    bw2 = (WIDTH - 4 * 6) // 5
    for i, (name, body) in enumerate(BOXES):
        bx = x0 + i * (bw2 + 6)
        draw.rectangle([bx, y, bx + bw2, y + 56], fill=PAPER, outline=NAVY,
                       width=1)
        draw.rectangle([bx, y, bx + bw2, y + 15], fill=NAVY)
        draw.text((bx + 6, y + 3), name, font=F(SANS_B, 9),
                  fill=(255, 255, 255))
        block(draw, bx + 6, y + 18, body, SANS_R, 9, bw2 - 12, 3, INK,
              line_h=11)

    # 11 — corrections strip ---------------------------------------------------------------------
    y = 952
    draw.rectangle([x0, y, x1, y + 18], fill=NAVY)
    centered(draw, CANVAS / 2, y + 9, CORRECTIONS,
             fit_one_line(draw, CORRECTIONS, SANS_B, 10, WIDTH - 16),
             (255, 255, 255))

    # 12 — footer: red DATE CHECK box + colophon line -------------------------------------------
    y = 976
    draw.rectangle([x0, y, x1, y + 24], fill=CRIMSON)
    centered(draw, CANVAS / 2, y + 12, DATE_CHECK,
             fit_one_line(draw, DATE_CHECK, SANS_B, 11, WIDTH - 16),
             (255, 255, 255))
    foot = ("50 stories · drawn and set in one page · sources: Reuters, "
            "AP, AFP, BBC, Al Jazeera, UN News and the wires of Thursday "
            "19 November 2026")
    centered(draw, CANVAS / 2, 1011, foot,
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
