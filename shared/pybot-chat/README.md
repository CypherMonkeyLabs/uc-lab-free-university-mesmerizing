# Py chat (offline)

A small, copyable chat for a static lab. It answers from a JSON index built out of that lab's own pages. There is no cloud model, no API key, and no request off the site.

Python Lab uses it inside Py's panel. Another lab can copy this folder, write its own index builder, and keep the engine as-is.

## Files

| File | Role |
| --- | --- |
| `engine.js` | Tokenise, stem, synonyms, typo fix, BM25, confidence gate, seed matching, and intent rules. No DOM. |
| `ui.js` | Message list, suggestion chips, Mic, Send, Clear. The host supplies the words. |
| `chat.css` | Layout for the dock. It expects the lab's colour variables (`--ink`, `--bg`, `--accent`, `--line`, `--top-h`, `--bar-h`). |

The index is not in this folder. Python Lab writes it to `js/content/pybot-index.json` with:

```
node pipeline/build_pybot_index.mjs
```

Check retrieval with:

```
node tests/pybot-eval.mjs
```

## Wiring

1. Import `createRetriever` from `engine.js` and `fetch` the index (same origin).
2. Put `chatMarkup()` in the bot panel and call `paintChat` when messages change.
3. On Send, Enter, a chip, or the mic transcript, call `retriever.ask(text, host)`.
4. Show `text`. Link `href` only when it is set. The link label is `link` (`Open this lesson` for a lesson). A fallback has no `href`.
5. One follow-up chip uses `follow` / `followQ`. `ask` remembers a single previous turn, so "and in a dict?" and "show an example" can continue it. If the follow-up does not match, the reply says it is still on the previous topic and does not open a different lesson.
6. If the score is weak, the text starts with "I don't have that yet" and may name the closest lesson titles. Do not replace that with a guessed fact.
7. Precache `engine.js`, `ui.js`, `chat.css`, and the index in the service worker. Bump the cache name when those files change.

`host.progress` can return `{ done, total, xpLevel, nextHref, nextTitle }` for "what level am I". Omit it and the level reply stays generic.

## How another lab builds an index

Copy `engine.js`, `ui.js`, and `chat.css`. Write a builder that emits one JSON file:

```json
{
  "v": 2,
  "syn": { "dictionary": "dict" },
  "seeds": [],
  "docs": [
    { "i": "lesson:intro", "k": "lesson", "ti": "Intro", "h": "#/lesson/intro", "s": "start", "ex": "Short excerpt.", "w": ["intro"], "tw": ["intro"] }
  ]
}
```

`docs` are the pages you are willing to quote. `ex` is the sentence the chat shows. `w` and `tw` are already-stemmed body and title tokens (the same stemmer the engine uses, or leave that to your builder). Optional `eg` is an example the follow-up chip can reveal. `k` is a kind such as `lesson`, `slide`, `guide`, or `glossary`.

`syn` maps a surface word to the token you indexed (`dictionary` → `dict`).

`seeds` are optional curated excerpts for questions the ranker gets wrong. The engine does not invent the sentence. Your lab writes `ex` from its own lesson text. Seed fields:

| Field | Meaning |
| --- | --- |
| `i`, `h`, `ti`, `k` | Id, href, title, kind. Same idea as a doc. |
| `ex`, `eg` | Excerpt to show, and an optional example. |
| `topic` | Word stored for the next follow-up ("list", "loop"). |
| `all` | Every one of these tokens must be in the question. |
| `any` | At least one must be in the question. |
| `allow` | Other content words that may appear. A word outside this list rejects the seed. |
| `block` | If any of these tokens appear, skip the seed. |
| `loose` | Skip the allow check. Use for error names (`NameError`). |
| `how` | Set `false` to keep the allow check even on "how do I …". |
| `rank` | Added to the match score so a specific seed beats a general one. |

A how-question (`how do I`, `how to`, `how can`) skips `allow` unless `how` is `false`. Put the verb in `any` (`print`, `loop`, `sort`, `read`).

## What the engine decides before it searches

Injection is checked on the raw string, before retrieval and before memory. Patterns include "ignore", "pretend", "roleplay", "system prompt", "instructions", "repeat/print/reveal the text above", and "starting with You are". The reply is a fallback with intent `injection` and no link.

A question also needs a programming term before search. The term list is a curated programming vocabulary plus index terms that are not ordinary English. One ambiguous word such as "set" or "time" does not carry a question that is otherwise outside the lab. With no in-domain term, the fallback does not attach closest-page links.

Small talk (hi, hey there, thanks, bye, who are you, and short variants) is a fixed friendly reply with no lesson link. "What can you do" and "what topics can you help with" are help intents. They do not search.

Typos: a word that is not in the index vocabulary is corrected when one candidate wins. Doubled letters collapse first (`lisst` → `list`). Otherwise Damerau-Levenshtein distance is 1 for words shorter than 7 characters and 2 from 7 up. Ties prefer the longer shared prefix, then the shorter completion, then the term that appears in more pages. Stop words are not rewritten (`is` stays `is`). A 2–4 letter word can also match a stop word or a seed term (`wat` → `what`).

## When a hit is shown

BM25 (k1 1.2, b 0.75) ranks docs. A hit is shown only when the top score is at least 2.4, the matched known terms cover at least two thirds of the known query terms, and the margin over the next different page is at least 1.2 (or the score ratio is at least 1.22). A title phrase can pass with lower coverage. If the query has no indexed term, or more unknown terms than indexed terms and at most one indexed term, the engine falls back without showing a link.

Seeds are tried after intents and before BM25. The highest seed score wins. Python Lab's builder also adds one low-rank seed per lesson, from that lesson's title and excerpt, with `how: false` so a loose how-question does not steal it from a curated seed.

## What an answer is allowed to say

Excerpts come from the index fields `ex` and `eg`. The engine does not write a new Python fact. Greetings, the level line, the help line, and the "I don't have that yet" line are fixed sentences, and they do not claim a language rule that is not in the index.

Recorded voices in Python Lab are fixed clips. Read aloud uses the browser voice for an answer sentence. The voice picker still chooses those clips for the audio lessons.

## Short screens

`chat.css` lays the panel out as a column. The lesson scroller shrinks. The text field does not. Under 560px of viewport height the header, quick actions, and suggestion chips collapse, and the answer log keeps a 48px minimum with its own scrollbar so the reply can be read. Clear stays available. The host should position the panel with `visualViewport` (width, height, offsetTop) and `dvh`, and listen to `visualViewport` resize and scroll, so a phone keyboard does not cover the field.

## Licence

These files are part of Python Lab: MIT code. Do not add a third-party search library when you copy the folder.
