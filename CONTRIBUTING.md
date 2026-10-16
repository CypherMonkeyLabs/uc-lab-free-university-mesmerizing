# Contributing

UC Lab Free University is a public teaching file. Small, checked improvements help the next reader. A full remix is welcome too, in a fork or in a pull request.

The engineering guide is [docs/REMIX.md](./docs/REMIX.md): file layout, section objects, naming, themes, the zip, the deck, and how to aim an AI coding agent at the HTML.

## Good pull requests

- A vendor URL that moved, with the replacement
- A section that throws, fails to open, or shows the wrong count
- A factual correction tied to a current official document
- A new section or theme that follows [docs/REMIX.md](./docs/REMIX.md)

## Please leave these out

- Customer names, real dial plans, call captures, and screenshots of production tools
- Secrets, tokens, internal hostnames, and personal contact details
- A CDN, a font host, or an account requirement
- A reformat of `campus/uc-lab-free-university.html` that only changes whitespace

## Before you open the pull request

```bash
python3 scripts/check-campus.py
python3 scripts/rebuild-campus-zip.py   # if the HTML changed
python3 scripts/brand-pptx.py           # if the deck changed
python3 scripts/scrub-pptx-metadata.py  # if the deck changed
```

Open the HTML from disk in Chrome, Safari, Edge, or Firefox. Search still works in airplane mode. If you added a section, load it by hash (`#your-id`).

Use the pull request template. Say which section ids you touched and which official document you checked.

## Issues

- Something fails to open: bug report
- The curriculum should change: curriculum change
- An official link rotted: broken link

GitHub shows those forms from `.github/ISSUE_TEMPLATE`. A curriculum change that adds or removes a trail is easier to review as an issue first, then a pull request.

## AI coding agents

Cursor and similar agents are fine. Point them at [docs/REMIX.md](./docs/REMIX.md) and require `python3 scripts/check-campus.py` before you push. Read the new prose yourself. The agent does not get a vote on ports, product names, or anything that came from a private MCP workspace.

Be kind in review. This file exists so a stranger can learn the call path without a lab badge.
