# Vocab Quest

A single-file, installable (PWA), fully-offline word game. Play in the browser or
add it to your home screen — everything (2,000+ words, definitions, sentences,
country data) is embedded in `index.html`, so it works in airplane mode.

## Game modes
- **📖 Definitions** — match the word to its meaning (12 options).
- **🔤 Word Scramble** — unscramble the word from its definition.
- **🚩 Flags** — guess the country from its flag.
- **🏛️ Capital → Country** and **🗺️ Country → Capital**.

Five difficulty tiers for the word games (Grade School → College; Final Boss coming
soon). Hearts, streaks, and a score keep it honest; the geography modes give three
guesses per question.

## How the word list is built
The `build/` folder holds the generator pipeline:
- Words, parts of speech, and synonym groups come from **WordNet**.
- Difficulty tiering uses **wordfreq** frequency data.
- Definitions are polished and example sentences written by an LLM (Claude), then
  validated (every sentence contains its word; no definition leaks its own word).
- An ambiguity audit builds a conflict map so two words that fit the same
  definition never appear together.

See [CREDITS.md](CREDITS.md) for data-source attribution and licensing.

## Running locally
Just open `index.html` in a browser — no build step, no server required.
