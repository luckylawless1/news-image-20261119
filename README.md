[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/luckylawless1/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/luckylawless1/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World in One Day — Thursday 19 November 2026 in one image

An entry for the make.fun bounty
[news-image-20261119](https://make.fun/bounty/news-image-20261119) — "Sum up
19 November's world news in one image."

The entry is a single square image, `entry.png`: a dense broadsheet front
page that packs the whole of Thursday 19 November 2026 into one page —
**50 stories across 7 regions**, every one of them first reported that
Thursday, and date-checked. This third edition corrects the first: four
stories the first edition dated to Thursday had broken earlier in the
week (the EU's €45bn Ukraine loan, the Jeffries vote, the Deutsche Bank
files and the "missing billion years" study). They are struck out and
named in a **CORRECTIONS & CLARIFICATIONS** strip, and the red DATE CHECK
box names the other pre-Thursday stories left out on purpose — the
$190.4m Van Gogh sale, Voyager 1's light-day, the US–Venezuela military
deal, the IAEA's North Korea report and Bolivia's El Niño decree.

## What's on the page

- **Masthead and numbers band** — the day in six figures: the World
  Court's 9–6 genocide verdict, Anthropic's record $81.3bn IPO raise,
  GTA VI's estimated $1.84bn first-day sales, the 204,070 people listed
  for evacuation in Odisha, Denmark's 109–0 Arctic pact vote, and
  Australia's 4.9% jobless rate.
- **Three hero stories** — (1) the Shenzhen trilateral summit of Trump,
  Xi and Putin and its four-point peace declaration, (2) GTA VI's
  midnight launch, (3) Anthropic's first day on Nasdaq, closing up 17%.
- **Ten more numbered features (4–13)** — the ICJ's 9–6 Rohingya
  genocide ruling, COP31's slimmed draft dropping fossil fuels and the
  $120bn target, Cyclone Akvan, the third strike on the Crimean Bridge,
  the tankers that hit mines in Hormuz, the Houthi missiles over Riyadh,
  Israel's ended Gaza tank raid, ex-PM Han Duck-soo's retrial in Seoul,
  Denmark's 109–0 Arctic pact vote, and Australia's jobs shock.
- **PICTURE OF THE DAY (14)** — fire on the water in the Strait of
  Hormuz, with crude flows through the strait at half pre-war levels.
- **WHERE IT HAPPENED** — a dot-matrix world map with red numbered pins
  1–13 marking where each hero and feature story happened.
- **THE DAY BY THE CLOCK — UTC** — the day's timeline, from GTA VI
  unlocking in New Zealand at 00:00 to COP31's slimmed draft in the
  evening.
- **36 briefs (15–50)** in four columns, from the Odesa strike and the
  Krasnodar refineries to Tonga's drought emergency and the IEA's
  Hormuz warning.
- **Five boxes the other front pages don't have:**
  - **SPORT** — marathon champion Peres Jepchirchir banned three years
    for EPO; Duckett's 133 seals England's ODI win.
  - **WEATHER WATCH** — Cyclone Akvan's 145 km/h winds and Friday
    landfall; Tonga's nationwide drought emergency.
  - **MARKETS** — ANT +17% at $97.17 on day one, Brent near $92 on the
    Hormuz reports, the Aussie dollar at a 2026 low.
  - **QUOTE OF THE DAY** — "End your war, end it now." — Anthony
    Albanese to Vladimir Putin, at APEC.
  - **FRIDAY PREVIEW** — Akvan's landfall, COP31's final text, GTA VI's
    first official sales tally.
- **CORRECTIONS & CLARIFICATIONS** — the strip that owns the first
  edition's four mis-dated stories (see above).

## How the image was made

`compose.py` (Python 3 + Pillow) draws the entire page: masthead, bands,
cards, map, timeline and boxes are all rendered text and shapes, so every
word is crisp. Three feature stories and the Picture of the Day reuse
the AI-generated editorial illustration panels in `assets/` (the
Shenzhen summit, the ICJ, COP31, Hormuz); the GTA VI hero art — a purple
Vice City skyline — and the Anthropic hero art — a green candlestick
chart labelled ANT $97.17 — are drawn by the program itself, as is the
dot-matrix world map, which is built from a coarse grid defined in the
code.

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
