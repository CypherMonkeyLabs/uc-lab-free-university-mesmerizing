# Kit

The round-2 chrome is the Webex lab kit, adapted for this Unified Communications course.

Copied and kept:

- `assets/css/frame.css`, `wow.css`, `footer.css`, `canon.css`, `shell.css`, `polish.css`, `university.css`
- `scripts/gzip-static.mjs` serves the tree with gzip so a mobile Lighthouse run matches a normal host

Written for this lab:

- `assets/css/uc.css` forces one banner row, the header Menu button, the sliding drawer, the phone bar, and the guide dock
- `assets/js/frame.js` wires the drawer, display controls (font size and font colour), and search
- `assets/js/university.js` exposes the contact URL and the GitHub organization only
- `guide/guide.js` and `guide/guide.css` are the monkey, the six-step tour, read-along, and voice input. The tour card (gradient border, glow, pill buttons, step dots, and the spotlight) lives in `guide/guide.css`, so a copy of those two files keeps the card.
- `scripts/build_uc_round2.py` holds the room facts
- `scripts/uc_site.py` writes pages, SVG, sheets, and office files
- `scripts/verify-university.mjs` checks counts and allowed brand hosts

Brand links are only:

- https://cyphermonkeylabs.com
- https://github.com/CypherMonkeyLabs
- https://linktr.ee/cypherMonkey

Citation links may point at the RFC Editor, Cisco, Webex Help, and the ITU. Rebuild with `python3 scripts/uc_site.py`.
