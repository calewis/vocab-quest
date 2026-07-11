# Vocabulary entry refinement — instructions

You refine candidate words into polished entries for a vocabulary word game.
Your input chunk file is a JSON array of items shaped like
`{"w","pos","def","group","zipf","tier"}` where `tier` is a rough difficulty guess.

For EACH item output exactly one object — a KEEP or a DROP — into a JSON array in the
SAME order, and Write it to your assigned output path. Also print the JSON as your
final message. Output valid JSON only, no commentary.

## DROP → `{"w": <word>, "drop": "<short reason>"}`
Drop if the word is any of:
- a proper noun, personal name, place, brand, or an abbreviation
- a nationality, ethnicity, religion, or demonym (e.g. islamic, bavarian, tamil) — keep the game neutral
- an inflected form rather than a base word (plural, past tense, gerund, participle) — e.g. finished, winnings, gathering
- offensive, sexual, or a slur; anything unsuitable for a general or child audience
- so vague, technical, or purely functional that its everyday meaning can't make a clean single-answer puzzle

## KEEP → `{"w","pos","def","tier","sentence","form"}`
- **def**: a crisp, unambiguous definition of the word's PRIMARY EVERYDAY meaning. Definition quality is the single most important thing — a vague or ambiguous definition ruins the round. If the provided WordNet def reflects an obscure or wrong sense (e.g. "cod" as a seed-pod, "slur" as a music term), REPLACE it with the meaning a well-read adult would give. The definition must NOT contain the word itself or any obvious form of it, and must point to THIS word specifically, not a near-synonym.
- **pos**: the part of speech of that common sense — one of "noun", "verb", "adjective".
- **tier**: the age-appropriate difficulty tier, based on when a student realistically learns the word — one of "grade", "middle", "high", "college". Keep the input tier unless the word clearly belongs elsewhere; move it if so.
- **sentence**: ONE example sentence in a vivid, literary voice — a line you'd admire in a well-written novel: concrete, sensory, with real rhythm. It MUST:
  - be fully self-contained: understandable with zero prior context, no dangling pronouns referring to nothing
  - naturally contain the word (any inflection is fine)
  - NOT state or paraphrase the definition in a way that gives the answer away
  - match the reading level of its tier (see below)
- **form**: the EXACT word-form as it literally appears in your sentence (the substring the game will bold). If the sentence says "shone" for shine, form is "shone"; if "meticulous", form is "meticulous". It MUST be an exact substring of your sentence.

## Reading level by tier
- **grade** (ages 6–10): short sentences, simple common words, plain syntax — but still vivid and concrete. Do not use hard vocabulary in the sentence itself.
- **middle** (ages 11–13): everyday language, a little longer and richer.
- **high** (ages 14–17): SAT-level; more sophisticated imagery and structure.
- **college** (adult): full literary richness; complex syntax and elevated diction welcome.

Never let the example sentence be harder to read than the word being taught (except at college level).

## Examples
KEEP: `{"w":"meticulous","pos":"adjective","def":"showing great attention to detail","tier":"high","sentence":"She checked every stitch twice, meticulous as a jeweler setting a diamond.","form":"meticulous"}`
KEEP: `{"w":"snare","pos":"noun","def":"a trap, typically a noose, used to catch birds or animals","tier":"college","sentence":"The poacher had strung a wire snare between two saplings, hoping to catch a hare by morning.","form":"snare"}`
DROP: `{"w":"bavarian","drop":"demonym"}`
DROP: `{"w":"winnings","drop":"inflected/plural form"}`

Output nothing but the JSON array.
