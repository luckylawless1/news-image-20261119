[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/luckylawless1/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/luckylawless1/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World in One Day — Thursday 19 November 2026 in one image

An entry for the make.fun bounty
[news-image-20261119](https://make.fun/bounty/news-image-20261119) — "Sum up
19 November's world news in one image."

The entry is a single square image, `entry.png`: a dense broadsheet front
page that packs the whole of Thursday 19 November 2026 into one page —
**44 stories across 7 regions**, every one of them first reported that
Thursday, and date-checked (two famous stories that broke on Wednesday
18 November — the $190.4m Van Gogh sale and Voyager 1 reaching one
light-day — are named in the red DATE CHECK box and deliberately left
out).

## What's on the page

- **Masthead and numbers band** — the day in six figures: Anthropic's
  record $81.3bn IPO raise, 15.9m GTA VI pre-orders, 200,000 people
  evacuated ahead of Cyclone Akvan, the proposed $120bn COP31 adaptation
  fund, 730,000 Rohingya who fled Myanmar, and the 551,864 students
  sitting South Korea's Suneung exam.
- **Three hero stories** — (1) the Shenzhen trilateral summit of Trump,
  Xi and Putin, (2) GTA VI's midnight launch, (3) Anthropic's record
  Nasdaq debut.
- **Ten more numbered features (4–13)** — the ICJ's Rohingya genocide
  ruling, the deadlocked COP31 talks in Antalya, Cyclone Akvan, the third
  strike on the Crimean Bridge, the burning tankers in Hormuz, the Houthi
  missile that reached Riyadh, Israel's operation in central Gaza,
  Suneung day in Seoul, Zelenskyy's "not without us", and the stalled
  Abu Dhabi talks.
- **WHERE IT HAPPENED** — a dot-matrix world map with red numbered pins
  1–13 marking where each feature story happened.
- **THE DAY BY THE CLOCK — UTC** — the day's timeline, from GTA VI going
  on sale in New Zealand at 00:00 to the COP31 endgame in the evening.
- **27 briefs (14–40)** in three columns, from the Odesa strike and the
  EU's €45bn Ukraine loan to the Senegal migrant boat and Australia's
  unemployment rise.
- **Five boxes the other front pages don't have:**
  - **SPORT** — Duckett's 133 seals England's ODI series win; GTA VI
    midnight queues in New York and London.
  - **WEATHER WATCH** — Cyclone Akvan's 130 km/h winds and Friday
    landfall, Florida flood warnings, Fiji's El Niño drought disaster.
  - **MARKETS** — ANT's $83 debut, the Fed minutes, the Deutsche Bank
    leak probe.
  - **QUOTE OF THE DAY** — "We'll see what happens." — Donald Trump, on
    the Iran war after 1 January.
  - **FRIDAY PREVIEW** — Akvan's landfall, Anthropic's first full
    trading day, COP31's final text.

## How the image was made

`compose.py` (Python 3 + Pillow) draws the entire page: masthead, bands,
cards, map, timeline and boxes are all rendered text and shapes, so every
word is crisp. Three feature stories reuse the AI-generated editorial
illustration panels in `assets/` (the Shenzhen summit, the ICJ, COP31);
the GTA VI hero art — a purple Vice City skyline — and the Anthropic
hero art — a green candlestick chart labelled ANT $83 — are drawn by the
program itself, as is the dot-matrix world map, which is built from a
coarse grid defined in the code.

## How to run

```sh
python3 compose.py                                  # rebuilds entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts # writes out/entry.png
```

`main.ts` (Node 22, standard library only) is the entry program: it copies
the committed `entry.png` into the output directory byte for byte, so
repeated runs always produce identical bytes. Running `compose.py` twice
also produces byte-identical output.

## License

MIT — see `LICENSE`.
