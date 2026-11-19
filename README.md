# The World Today — 19 November 2026 in one image

An entry for the make.fun bounty
[news-image-20261119](https://make.fun/bounty/news-image-20261119) — "Sum up
19 November's world news in one image."

The entry is a single square image, `entry.png`: a newspaper front page for
Thursday 19 November 2026, with a masthead, five illustrated stories with
captions, and a news ticker along the bottom.

## The five stories pictured

1. **Shenzhen summit.** Presidents Trump, Xi Jinping and Vladimir Putin held
   their first trilateral summit in Shenzhen, China, on the sidelines of
   APEC, pledging strategic stability and nuclear-risk dialogue while the war
   in Ukraine hung over the talks.
2. **The Hague.** The International Court of Justice ruled in the Gambia v.
   Myanmar case over the genocide of the Rohingya.
3. **Antalya.** COP31 climate negotiations deadlocked as ministers tried to
   unblock a final text.
4. **Hormuz.** A tanker was struck in the Strait of Hormuz amid Iran–Gulf
   escalation, and the IEA warned of an unprecedented energy-security
   threat.
5. **Crimea.** The bridge linking annexed Crimea to Russia was struck for
   the third time in a week and traffic was suspended.

**Also today (the ticker):** Anthropic's record $81.3B IPO; a Van Gogh sold
for a record $190.4M; Cyclone Akvan forced over 100,000 evacuations in
Odisha, India; the IAEA reported North Korea expanding uranium enrichment.

## How the image was made

The five pictures are AI-generated editorial illustrations in a shared flat
style, held in `assets/`. They are composed into the front page by
`compose.py` using Pillow: the program center-crops each panel into its
slot, frames it, and draws the masthead, the caption strips and the ticker
itself, so every word on the page is crisp rendered text rather than part of
a generated picture.

## How to run

```sh
python3 compose.py                                  # rebuilds entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts # writes out/entry.png
```

`main.ts` (Node 22, standard library only) is the entry program: it copies
the committed `entry.png` into the output directory byte for byte, so
repeated runs always produce identical bytes.

## License

MIT — see `LICENSE`.
