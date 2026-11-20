// The World in One Day — Thursday 19 November 2026 in one image.
//
// Entry for the make.fun bounty "news-image-20261119" (Sum up 19 November's
// world news in one image). The picture is a newspaper front page for
// Thursday 19 November 2026, composed by compose.py from the editorial
// illustration panels in assets/ — the Shenzhen trilateral summit of
// Presidents Trump, Xi and Putin, the ICJ ruling on the Rohingya genocide
// case, the deadlocked COP31 talks in Antalya, and the tankers burning in
// the Strait of Hormuz as the page's Picture of the Day — under a masthead,
// with 50 date-checked stories, a corrections strip, captions and a news
// ticker drawn by the program so every word is crisp.
//
// The composed page is committed beside this file as entry.png. This
// program's only job is to write that image to the output directory, byte
// for byte, so the run is deterministic: MAKEFUN_OUTPUT_DIR (default
// /output) receives an exact copy named entry.png, and repeated runs always
// produce identical bytes.

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const source = new URL("./entry.png", import.meta.url);
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const destination = join(outputDir, "entry.png");

// Create the output directory when it does not exist yet, so a local run
// (MAKEFUN_OUTPUT_DIR=out node main.ts) works without preparing it first.
mkdirSync(outputDir, { recursive: true });
copyFileSync(source, destination);
console.log(`wrote ${destination}`);
