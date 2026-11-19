#!/usr/bin/env python3
"""Compose "The World Today" — a one-image front page of 19 November 2026's news.

Reads the five editorial illustration panels in assets/ and arranges them on a
1024x1024 newspaper front page: a masthead, a hero story, two rows of two
stories, and a news ticker along the bottom. All words (masthead, captions,
ticker) are drawn here with Pillow so every letter stays crisp.

Run:  python3 compose.py     -> writes entry.png next to this file.
"""

import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "entry.png")

# --- palette -------------------------------------------------------------
CREAM = (0xF3, 0xEA, 0xD8)
NAVY = (0x16, 0x23, 0x3F)
CRIMSON = (0xB3, 0x20, 0x2C)
GOLD = (0xD9, 0xA4, 0x41)
WHITE = (0xFF, 0xFF, 0xFF)

CANVAS = 1024
MAX_BYTES = 1_000_000


def find_bold_font():
    """Locate a bold TrueType font, preferring DejaVu Sans Bold."""
    preferred = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if os.path.exists(preferred):
        return preferred
    try:
        out = subprocess.run(
            ["fc-list", ":style=Bold", "file"], capture_output=True, text=True
        ).stdout
        for line in out.splitlines():
            path = line.split(":")[0].strip()
            if path.endswith(".ttf") and os.path.exists(path):
                return path
    except Exception:
        pass
    raise SystemExit("no bold TTF font found")


FONT = find_bold_font()


def fit_font(draw, text, max_width, start_size):
    """Return the largest bold font, starting at start_size, whose rendered
    text fits within max_width pixels (shrinks one point at a time)."""
    size = start_size
    while size > 8:
        font = ImageFont.truetype(FONT, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(FONT, size)


def centered(draw, cx, cy, text, font, fill):
    """Draw text centered on the point (cx, cy)."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, font=font, fill=fill)


def panel(name, width, height):
    """Load a panel and center-crop/resize it to exactly width x height."""
    img = Image.open(os.path.join(ASSETS, name)).convert("RGB")
    return ImageOps.fit(img, (width, height), Image.LANCZOS)


def framed(canvas, draw, img, x, y):
    """Paste an image and frame it with a 3px navy border."""
    canvas.paste(img, (x, y))
    w, h = img.size
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=NAVY, width=3)


def caption(draw, x, y, w, h, fill, text, start_size):
    """Draw a caption strip and its centered one-line white bold caption."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=fill)
    font = fit_font(draw, text, w - 16, start_size)
    centered(draw, x + w / 2, y + h / 2, text, font, WHITE)


def main():
    page = Image.new("RGB", (CANVAS, CANVAS), CREAM)
    draw = ImageDraw.Draw(page)

    # --- masthead ---------------------------------------------------------
    draw.rectangle([0, 0, CANVAS - 1, 111], fill=NAVY)
    title_font = ImageFont.truetype(FONT, 54)
    centered(draw, CANVAS / 2, 14 + 27, "THE WORLD TODAY", title_font, CREAM)
    date_font = ImageFont.truetype(FONT, 29)
    centered(draw, CANVAS / 2, 74 + 15, "THURSDAY · 19 NOVEMBER 2026", date_font, GOLD)
    # crimson rule under the masthead
    draw.rectangle([0, 116, CANVAS - 1, 118], fill=CRIMSON)

    # --- hero: the Shenzhen summit ---------------------------------------
    framed(page, draw, panel("summit.png", 984, 360), 20, 124)
    caption(
        draw, 20, 484, 984, 40, NAVY,
        "SHENZHEN SUMMIT — TRUMP, XI & PUTIN MEET FACE TO FACE", 23,
    )

    # --- row 2: The Hague and Antalya -------------------------------------
    framed(page, draw, panel("icj.png", 482, 190), 20, 536)
    framed(page, draw, panel("cop31.png", 482, 190), 522, 536)
    caption(
        draw, 20, 726, 482, 38, CRIMSON,
        "UN COURT RULES ON ROHINGYA GENOCIDE CASE", 19,
    )
    caption(
        draw, 522, 726, 482, 38, CRIMSON,
        "COP31 CLIMATE TALKS DEADLOCKED IN ANTALYA", 19,
    )

    # --- row 3: Hormuz and Crimea -----------------------------------------
    framed(page, draw, panel("hormuz.png", 482, 150), 20, 776)
    framed(page, draw, panel("crimea.png", 482, 150), 522, 776)
    caption(
        draw, 20, 926, 482, 38, NAVY,
        "HORMUZ CRISIS — TANKER HIT, ENERGY FEARS", 19,
    )
    caption(
        draw, 522, 926, 482, 38, NAVY,
        "CRIMEAN BRIDGE STRUCK — THIRD TIME IN A WEEK", 19,
    )

    # --- ticker ------------------------------------------------------------
    # crimson rule above the ticker
    draw.rectangle([0, 968, CANVAS - 1, 970], fill=CRIMSON)
    draw.rectangle([0, 976, CANVAS - 1, 1011], fill=NAVY)
    ticker = (
        "ALSO TODAY: ANTHROPIC'S RECORD $81B IPO • VAN GOGH SELLS FOR $190M • "
        "CYCLONE AKVAN EVACUATES 100,000 IN INDIA"
    )
    ticker_font = fit_font(draw, ticker, CANVAS - 24, 20)
    centered(draw, CANVAS / 2, (976 + 1012) / 2, ticker, ticker_font, GOLD)

    # --- save, keeping the file at or under 1,000,000 bytes ----------------
    page.save(OUT, "PNG", optimize=True)
    if os.path.getsize(OUT) > MAX_BYTES:
        page.quantize(colors=256, method=Image.MEDIANCUT).save(
            OUT, "PNG", optimize=True
        )

    final = Image.open(OUT)
    print(f"entry.png: {os.path.getsize(OUT)} bytes, {final.size[0]}x{final.size[1]}")
    if final.size != (1024, 1024) or os.path.getsize(OUT) > MAX_BYTES:
        sys.exit("entry.png failed the size/dimension limits")


if __name__ == "__main__":
    main()
